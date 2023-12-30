from os.path import join as pjoin

from DataStructures import *
from ModelManagement import ModelManager
from SystemConnection import SystemConnector
from TaskDeclearation import TaskDeclarator
from TaskExecution import AppTasker, InquiryTasker
from ThirdPartyAppManagement import ThirdPartyAppManager
from UIProcessing import UIProcessor


class UTA:
    def __init__(self, user_id, img_path, xml_path, output_dir):
        """
        Initialize the UTA class with necessary modules and user data paths.

        Args:
            user_id (str): The identifier for the user.
            img_path (str): Path to store screenshots.
            xml_path (str): Path to store UI hierarchy XML data.
            output_dir (str): Directory to store output files.
        """
        self.model_manager = ModelManager()
        self.task_declarator = TaskDeclarator(self.model_manager)
        self.system_connector = SystemConnector()
        self.ui_processor = UIProcessor(self.model_manager)
        self.app_tasker = AppTasker(self.model_manager)
        self.app_recommender = ThirdPartyAppManager(self.model_manager)
        self.inquiry_tasker = InquiryTasker("inquiry_tasker", self.model_manager)

        self.xml_path = img_path
        self.img_path = xml_path
        self.output_dir = output_dir
        self.user = User(user_id)

        self.ori_task_postfix_id = 0
        self.autonomic_task_postfix_id = 1
        self.step_postfix_id = 1

    def initialize_agents(self):
        """
        Initializes all the agents required for task processing.
        Resets task and step identifiers for a new user session.
        """
        self.task_declarator.initialize_agents()
        self.app_tasker.initialize_agents()
        self.app_recommender.initialize_agents()
        self.inquiry_tasker.initialize_agent()

        self.ori_task_postfix_id += 1
        self.autonomic_task_postfix_id = 1
        self.step_postfix_id = 1

    def execute_inquiry_task(self, conversation):
        """
        Execute an inquiry task using the provided conversation string.

        Args:
            conversation (str): The conversation string for the inquiry.
        Returns:
            The response from the inquiry tasker.
        """
        return self.inquiry_tasker.execute_inquiry_task(conversation)

    def clarify_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        """
        return self.task_declarator.clarify_task(task, printlog=printlog)

    def decompose_and_classify_tasks(self, task, printlog=False):
        """
        Decomposes the given task into sub-tasks and classifies each one.

        Args:
            task (str): The main task to decompose.
            printlog (bool, optional): Flag to enable logging of the process. Defaults to False.
        Returns:
            List of tuples: Each tuple contains a sub-task and its classification.
        """
        task_class_tuple = []
        decomposed_tasks = self.task_declarator.decompose_task(task, printlog=printlog)
        if decomposed_tasks['Decompose'] == 'True':
            for sub_task in decomposed_tasks['Sub-tasks']:
                task_class = self.task_declarator.classify_task(sub_task, printlog=printlog)['Task Type']
                task_class_tuple.append((sub_task, task_class))
        else:
            task_class = self.task_declarator.classify_task(task, printlog=printlog)['Task Type']
            task_class_tuple.append((task, task_class))

        return task_class_tuple

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
            # self.execute_ui_operation(back_availability_action, ui_data, show_operation)
            return relation, back_availability_action, "Can go back, execute the back action."

        return self.try_related_apps(task, ui_data, relation, app_list, except_apps, printlog)

    def try_related_apps(self, task, ui_data, relation, app_list, except_apps, printlog):
        """
        Try to find a related app.
        """
        rel_app = self.app_recommender.check_related_apps(task, app_list=app_list,
                                                          except_apps=except_apps, printlog=printlog)
        if rel_app == 'None':
            return relation, None, "No related app can be found."

        action = Action(action='Launch App', element_id=-1, description=rel_app["App"], reason=rel_app["Reason"],
                        input_text="N/A")
        return ui_data, relation, action, "Found related app, try to launch the app."

    def automate_app_and_system_task(self, ui_data, task, app_list=None, except_apps=None, printlog=False):
        """
        Automates a task based on the current UI and task description.
        Args:
            task (str): Description of the task to be automated.
            except_apps (list, optional): Apps to be excluded.
            printlog (bool): Enables logging if True.
        Returns:
            relation, recommended_action, execution_result
        """

        relation = self.app_tasker.check_task_ui_relation(ui_data, task, except_elements=except_apps, printlog=printlog)

        if relation.relation in {'Completed', 'Unrelated'}:
            if relation.relation == 'Completed':
                return relation, None, "Task is completed."
            return self.handle_unrelated_ui(task, ui_data, relation, app_list, except_apps, printlog)

        # Handle the case where the relation is neither completed nor unrelated
        action = self.app_tasker.check_ui_action(ui_data, task, printlog=printlog)
        if action == "N/A":
            return self.handle_unrelated_ui(task, ui_data, relation, app_list, except_apps, printlog)

        return relation, action, "Enter next turn."

    def store_data_to_local(self, json_file, file_name):
        """
        Stores the given JSON data in a specified file.

        Args:
            json_file (dict): JSON data to be saved.
            file_name (str): The name of the file to store the data.
        """
        self.system_connector.save_json(json_file, pjoin(file_name, self.output_dir))

