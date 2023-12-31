import os
from os.path import join as pjoin
import json
from datetime import datetime

from uta.DataStructures import *
from uta.ModelManagement import ModelManager
from uta.SystemConnection import SystemConnector
from uta.TaskDeclearation import TaskDeclarator
from uta.TaskExecution import TaskExecutor
from uta.ThirdPartyAppManagement import ThirdPartyAppManager
from uta.UIProcessing import UIProcessor


class UTA:
    def __init__(self):
        """
        Initialize the UTA class with necessary modules and user data paths.
        """
        # basics
        self.model_manager = ModelManager()
        self.system_connector = SystemConnector()
        # workers
        self.ui_processor = UIProcessor(self.model_manager)
        self.task_declarator = TaskDeclarator(self.model_manager)
        self.task_executor = TaskExecutor(self.model_manager)
        self.app_recommender = ThirdPartyAppManager(self.model_manager)
        # for debugging
        self.cur_task = None  # current task, for testing and debugging

    def instantiate_task(self, user_id, task_id, user_msg=None):
        """
        Instantiate a Task object by loading an existing one or creating a new one according to the given info
        Args:
            user_id (str): User id to identify the folder
            task_id (str): Task id to identify the file
            user_msg (str): User's input message. For new task, it is the task description. For existing task, append it to conversation.
        Returns:
            Task (Task): Task object
        """
        task = self.system_connector.load_task(user_id=user_id, task_id=task_id)
        # if the task does not exist, creat a new one within the user's folder
        if not task:
            self.system_connector.set_user_task_folder(user_id=user_id, task_id=task_id)
            task = Task(task_id=task_id, user_id=user_id)
            # set the user message as the task description for a new task
            if user_msg:
                task.task_description = user_msg
        else:
            if user_msg:
                task.conversation_clarification.append({'role': 'user', 'content': user_msg})
        self.cur_task = task
        return task

    def instantiate_ui(self):
        pass

    '''
    ************************
    *** Task Declaration ***
    ************************
    '''
    def declare_task(self, user_id, task_id, user_msg):
        """
        Declare the task.
        First, clarify it, if unclear, return response to the frontend for user feedback.
        Second, if already clear, decompose the task to atomic tasks if necessary
        Args:
            user_id (str): User id, associated to the folder named with the user_id
            task_id (str): Task id, associated to the json file named with task in the user folder
            user_msg (str): User's input message.
        """
        task = self.instantiate_task(user_id, task_id, user_msg)
        clarify = self.clarify_task(task)
        if clarify['Clear'] == 'True':
            decompose = self.decompose_task(task)
            self.system_connector.save_task(task)
            return decompose
        else:
            self.system_connector.save_task(task)
            return clarify

    def clarify_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): Task object
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None", "Options":[]}
        """
        return self.task_declarator.clarify_task(task=task, printlog=printlog)

    def decompose_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        """
        return self.task_declarator.decompose_task(task=task, printlog=printlog)

    def classify_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        """
        return self.task_declarator.classify_task(task=task, printlog=printlog)

    '''
    ***********************
    *** Task Automation ***
    ***********************
    '''
    def automate_task(self, user_id, task_id, ui_img, ui_xml):
        """
        Returns:
            Action (dict): {"Action": }
        """
        task = self.instantiate_task(user_id, task_id)
        ui = self.instantiate_ui()
        pass

    def execute_inquiry_task(self, conversation):
        """
        Execute an inquiry task using the provided conversation string.

        Args:
            conversation (str): The conversation string for the inquiry.
        Returns:
            The response from the inquiry tasker.
        """
        llm_response = self.inquiry_tasker.execute_inquiry_task(conversation)
        self.history_manager.store_inquiry_step(step_id=self.step_id, parent_id=self.autonomic_task_id,
                                                user_conversation=conversation, llm_conversation=llm_response)
        # Store inquiry step
        self.step_id += 1
        return llm_response

    def process_ui(self, screenshot, vh, ui_resize):
        """
        Process UI data.
        Returns:
            UI data.
        """
        self.system_connector.save_xml(vh, self.xml_path)
        self.system_connector.save_img(screenshot, self.img_path)

        ui_data = self.ui_processor.load_ui_data(self.img_path, self.xml_path, ui_resize, self.output_dir)
        ui = self.ui_processor.process_ui(ui_data)
        return ui

    def handle_unrelated_ui(self, task, ui_data, relation, app_list, except_apps, printlog):
        """
        Handle cases where the UI is unrelated to the task.
        """
        back_availability_action = self.app_tasker.check_go_back_availability(ui_data, task, reset_history=True,
                                                                              printlog=printlog)
        if back_availability_action.action == 'Click':
            execution_result = "Can go back, execute the back action."

            self.history_manager.store_auto_mode_step(step_id=self.step_id, parent_id=self.autonomic_task_id,
                                                      ui_data=ui_data, relation=relation,
                                                      action=back_availability_action,
                                                      execution_result=execution_result)  # Store steps
            self.step_id += 1

            return relation, back_availability_action, execution_result

        return self.try_related_apps(task, ui_data, relation, app_list, except_apps, printlog)

    def try_related_apps(self, task, ui_data, relation, app_list, except_apps, printlog):
        """
        Try to find a related app.
        """
        rel_app = self.check_related_apps(task, app_list=app_list,
                                          except_apps=except_apps, printlog=printlog)
        if rel_app == 'None':
            execution_result = "No related app can be found."

            self.history_manager.store_auto_mode_step(step_id=self.step_id, parent_id=self.autonomic_task_id,
                                                      ui_data=ui_data, relation=relation,
                                                      action="None",
                                                      execution_result=execution_result)  # Store steps
            self.step_id += 1

            return relation, None, execution_result

        action = Action(action='Launch App', element_id=-1, description=rel_app["App"], reason=rel_app["Reason"],
                        input_text="N/A")
        execution_result = "Found related app, try to launch the app."

        self.history_manager.store_auto_mode_step(step_id=self.step_id, parent_id=self.autonomic_task_id,
                                                  ui_data=ui_data, relation=relation,
                                                  action="None",
                                                  execution_result=execution_result)  # Store steps
        self.step_id += 1

        return ui_data, relation, action, execution_result

    def automate_app_and_system_task(self, ui_data, task, app_list=None, except_apps=None, printlog=False):
        """
        Automates a task based on the current UI and task description.
        Args:
            ui_data: processed UI_Data
            task (str): Description of the task to be automated.
            app_list (list, optional): Apps to be independently considered.
            except_apps (list, optional): Apps to be excluded.
            printlog (bool): Enables logging if True.
        Returns:
            relation, recommended_action, execution_result
        """

        relation = self.app_tasker.check_task_ui_relation(ui_data, task, except_elements=except_apps, printlog=printlog)

        if relation.relation in {'Completed', 'Unrelated'}:
            if relation.relation == 'Completed':
                execution_result = "Task is completed."

                self.history_manager.store_auto_mode_step(step_id=self.step_id, parent_id=self.autonomic_task_id,
                                                          ui_data=ui_data,  relation=relation, action="None",
                                                          execution_result=execution_result)  # Store steps
                self.step_id += 1

                return relation, None, execution_result
            return self.handle_unrelated_ui(task, ui_data, relation, app_list, except_apps, printlog)

        # Handle the case where the relation is neither completed nor unrelated
        action = self.app_tasker.check_ui_action(ui_data, task, printlog=printlog)
        if action == "N/A":
            return self.handle_unrelated_ui(task, ui_data, relation, app_list, except_apps, printlog)

        execution_result = "Enter next turn."

        self.history_manager.store_auto_mode_step(step_id=self.step_id, parent_id=self.autonomic_task_id,
                                                  ui_data=ui_data, relation=relation, action="None",
                                                  execution_result=execution_result)  # Store steps
        self.step_id += 1

        return relation, action, execution_result

    def check_related_apps(self, task, app_list, except_apps=None, printlog=False):
        """
        Checks for apps related to a given task.
        Args:
            task (str): The task for which related apps are to be found.
            app_list (list): A list of apps to consider.
            except_apps (list, optional): Apps to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            JSON data with related app information.
        """
        return self.app_recommender.check_related_apps(task, app_list, except_apps, printlog)

    def store_user_to_local(self, file_name):
        """
        Stores the user data in a specified file.

        Args:
            file_name (str): The name of the file to store the user data.
        """
        json_file = json.loads(str(self.history_manager.get_user()))
        self.system_connector.save_json(json_file, pjoin(file_name, self.output_dir))


if __name__ == '__main__':
    uta = UTA()
    resp = uta.declare_task(user_id='1', task_id='1', user_msg='Send a message to my mom')
    resp = uta.declare_task(user_id='1', task_id='1', user_msg='Send it in whats app')
