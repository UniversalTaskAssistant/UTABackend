import json
import time
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

    def handle_unrelated_ui(self, task, ui_data, relation, printlog):
        """
        Handle cases where the UI is unrelated to the task.
        """
        back_availability_action = self.app_tasker.check_go_back_availability(ui_data, task, reset_history=True,
                                                                              printlog=printlog)
        if back_availability_action.action == 'Click':
            # self.execute_ui_operation(back_availability_action, ui_data, show_operation)
            return ui_data, relation, back_availability_action, "Can go back, execute the back action."

        return ui_data, relation, None, "Cannot go back, try to find and launch a related app."

    def try_related_apps(self, task, ui_data, relation, app_list, except_apps, printlog):
        """
        Try to find a related app.
        """
        rel_app = self.app_recommender.check_related_apps(task, app_list=app_list,
                                                          except_apps=except_apps, printlog=printlog)
        if rel_app == 'None':
            return ui_data, relation, None, "No related app can be found."

        action = Action(action='Launch App', element_id=-1, description=rel_app["App"], reason=rel_app["Reason"],
                        input_text="N/A")
        return ui_data, relation, action, "Found related app, try to launch the app."

    def automate_app_and_system_task(self, ui_data, task, except_apps=None, printlog=False):
        """
        Automates a task based on the current UI and task description.
        Args:
            task (str): Description of the task to be automated.
            except_apps (list, optional): Apps to be excluded.
            printlog (bool): Enables logging if True.
            show_operation (bool): Shows UI operation if True.
            related_app_max_try (int): Max attempts to launch related apps.
        Returns:
            ui_data, relation, recommended_action, execution_result
        """

        relation = self.app_tasker.check_task_ui_relation(ui_data, task, except_elements=except_apps, printlog=printlog)

        if relation.relation in ['Completed', 'Unrelated']:
            if relation.relation == 'Completed':
                return ui_data, relation, None, "Task is completed."
            return self.handle_unrelated_ui(task, ui_data, relation, printlog)

        # Handle the case where the relation is neither completed nor unrelated
        action = self.app_tasker.check_ui_action(ui_data, task, printlog=printlog)
        if action == "N/A":
            return self.handle_unrelated_ui(task, ui_data, relation, printlog)

        return ui_data, relation, action, "Enter next turn."

    def store_data_to_local(self, json_file, file_name):
        """
        Stores the given JSON data in a specified file.

        Args:
            json_file (dict): JSON data to be saved.
            file_name (str): The name of the file to store the data.
        """
        self.system_connector.save_json(json_file, pjoin(file_name, self.output_dir))

    '''
    *****************************************
    *** Can only be used in emulator mode ***
    *****************************************
    
    '''

    def connect_to_emulator(self):
        """
        Connect to emulator.
        """
        self.system_connector.connect_adb_device()

    def capture_ui_information(self):
        """
        Captures the current UI and view hierarchy.
        Returns:
            screenshot, view hierarchy, and resolution.
        """
        screenshot = self.system_connector.cap_screenshot()
        vh = self.system_connector.cap_current_ui_hierarchy()
        ui_resize = self.system_connector.get_device_resolution()
        return screenshot, vh, ui_resize

    def execute_ui_operation(self, action, ui, show=False, waiting_time=2):
        """
        Executes a UI operation based on the recommended action.
        Args:
            action (dict): Action to be performed.
            ui: The UI object on which the action is to be performed.
            show (bool): Shows the operation if True.
            waiting_time (int): Time to wait after performing the action.
        Raises:
            ValueError: If an unexpected action is encountered.
        """
        element = ui.elements[action['Element']]
        if action['Action'] == 'Click':
            self.system_connector.click_screen(ui, element, show)
        elif action['Action'] == 'Scroll Up':
            self.system_connector.up_scroll_screen(ui, element, show)
        elif action['Action'] == 'Scroll Down':
            self.system_connector.down_scroll_screen(ui, element, show)
        elif action['Action'] == 'Swipe Right':
            self.system_connector.right_swipe_screen(ui, element, show)
        elif action['Action'] == 'Swipe Left':
            self.system_connector.left_swipe_screen(ui, element, show)
        elif action['Action'] == 'Long Press':
            self.system_connector.long_press_screen(ui, element, show)
        elif action['Action'] == 'Input':
            self.system_connector.input_text(action['Input Text'])
        else:
            raise ValueError(f"No expected action returned from model, returned action: {action['Action']}")
        time.sleep(waiting_time)

    def automate_task(self, task, max_turn=100, clarify_max_turn=3, related_app_max_turn=3, debug=False,
                      except_apps=None, printlog=False, show_operation=False):
        """
        Main function to automate a given task, handling task decomposition, execution, and result storage.

        Args:
            task (str): The task description.
            max_turn (int, optional): Maximum iterations for task automation. Defaults to 100.
            clarify_max_turn (int, optional): Maximum iterations for task clarification. Defaults to 3.
            related_app_max_turn (int, optional): Maximum attempts to launch related apps. Defaults to 3.
            debug (bool, optional): Enables debug mode if set to True. Defaults to False.
            except_apps (list, optional): List of apps to exclude from task automation. Defaults to None.
            printlog (bool, optional): Enables detailed logging if set to True. Defaults to False.
            show_operation (bool, optional): Whether to visually show UI operations. Defaults to False.
        """
        # Initializes the task execution agents
        self.connect_to_emulator()
        self.initialize_agents()

        screenshot, vh, ui_resize = self.capture_ui_information()
        ui_data = self.process_ui(screenshot, vh, ui_resize)

        # Create a new original task object and increment task ID
        original_task = OriginalTask(self.ori_task_postfix_id, original_task=task)
        conversation = task
        clarifyed_result = {"Clear": "False", "Question": ""}

        # Loop for task clarification with user interaction
        while clarify_max_turn and clarifyed_result['Clear'] == "False":
            clarifyed_result = self.clarify_task(conversation, printlog)
            original_task.append_clarifying_conversation(({'role': 'user', 'content': task},
                                                          {'role': 'assistant', 'content': clarifyed_result}))

            conversation = input(clarifyed_result)  # we send this to front and wait for answer
            clarify_max_turn -= 1
        original_task.set_attributes(clarifyed_task=clarifyed_result['content'])

        # Decompose and classify the task into sub-tasks
        task_class_tuple = self.decompose_and_classify_tasks(task, printlog)
        for (clarifyed_task, task_class) in task_class_tuple:
            # Create a new autonomic task object and increment task ID
            new_task = AutonomicTask(self.autonomic_task_postfix_id, task=clarifyed_task, task_type=task_class)
            self.autonomic_task_postfix_id += 1

            # Process task based on its classification
            if task_class == "General Inquiry":
                llm_response = self.execute_inquiry_task(clarifyed_task)

                # Create an inquiry step and append it to the new task
                inquiry_step = InquiryStep(self.step_postfix_id)
                inquiry_step.set_attributes(user_conversation={'role': 'user', 'content': clarifyed_task},
                                            llm_conversation={'role': 'assistant', 'content': llm_response})
                self.step_postfix_id += 1

                new_task.append_step(inquiry_step)
                new_task.set_attributes(execution_result="Finish")
            else:
                # Loop for executing non-inquiry tasks
                for step_turn in range(max_turn):
                    ui_data, relation, action, result = self.automate_app_and_system_task(clarifyed_task,
                                                                                          except_apps=except_apps,
                                                                                          printlog=printlog,
                                                                                          show_operation=show_operation,
                                                                                          related_app_max_try=related_app_max_turn)

                    # Create a new automation step
                    auto_mode_step = AutoModeStep(self.step_postfix_id)  # Create a new step with the given step_id
                    auto_mode_step.set_attributes(ui_data=ui_data, relation=relation, execution_result=result)

                    # Check the recommended action and set attributes
                    if action:
                        auto_mode_step.set_attributes(recommended_action=action)
                        if result == "Can go back, enter next turn.":
                            auto_mode_step.set_attributes(is_go_back=True)

                    # Annotate UI operation for debugging
                    if debug:
                        auto_mode_step.annotate_ui_openation()
                    self.step_postfix_id += 1

                    new_task.append_step(auto_mode_step)

                    # Break loop if task is completed or failed
                    if result in {"Failed to launch related apps within max attempts.", "No related app can be found."}:
                        new_task.set_attributes(execution_result="Failed")
                        break
                    elif result == "Task is completed.":
                        new_task.set_attributes(execution_result="Finish")
                        break
                    else:
                        continue
            original_task.append_autonomic_task(new_task)
            self.user.append_user_task(original_task)

        # Store the user's task data in a local file or database
        self.store_data_to_local(json.loads(str(self.user)), f"result_user_{self.user.user_id}")  # later should be
        # changed to database/server
