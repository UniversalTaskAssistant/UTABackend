from DataStructures import *
from ModelManagement import ModelManager
from SystemConnection import SystemConnector
from TaskDeclearation import TaskDeclarator
from TaskExecution import AppTasker, InquiryTasker
from ThirdPartyAppManagement import ThirdPartyAppManager
from UIProcessing import UIProcessor

import time


class UTA:
    def __init__(self, img_path, xml_path, output_dir):
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

    def initialize_agents(self):
        self.task_declarator.initialize_agents()
        self.app_tasker.initialize_agents()
        self.app_recommender.initialize_agents()
        self.inquiry_tasker.initialize_agent()

    def execute_inquiry_task(self, conversation):
        self.inquiry_tasker.execute_inquiry_task(conversation)

    def clarify_task(self, task, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        '''
        return self.task_declarator.clarify_task(task, printlog=printlog)

    def decompose_and_classify_tasks(self, task, printlog=False):
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

    def capture_ui_information(self):
        """
        Captures the current UI and view hierarchy.
        Returns:
            UI data.
        """
        screenshot = self.system_connector.cap_screenshot()
        vh = self.system_connector.cap_current_ui_hierarchy()

        self.system_connector.save_xml(vh, self.xml_path)
        self.system_connector.save_img(screenshot, self.img_path)

        ui_resize = self.system_connector.get_device_resolution()
        ui_data = self.ui_processor.load_ui_data(self.img_path, self.xml_path, ui_resize, self.output_dir)
        ui = self.ui_processor.process_ui(ui_data)
        return ui

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
        if action['Action'].lower() == 'click':
            self.system_connector.click_screen(ui, element, show)
        elif action['Action'].lower() == 'scroll up':
            self.system_connector.up_scroll_screen(ui, element, show)
        elif action['Action'].lower() == 'scroll down':
            self.system_connector.down_scroll_screen(ui, element, show)
        elif action['Action'].lower() == 'swipe right':
            self.system_connector.right_swipe_screen(ui, element, show)
        elif action['Action'].lower() == 'swipe left':
            self.system_connector.left_swipe_screen(ui, element, show)
        elif action['Action'].lower() == 'long press':
            self.system_connector.long_press_screen(ui, element, show)
        elif action['Action'].lower() == 'input':
            self.system_connector.input_text(action['Input Text'])
        else:
            raise ValueError(f"No expected action returned from model, returned action: {action['Action']}")
        time.sleep(waiting_time)

    def automate_app_and_system_task(self, step_id, task, except_apps=None, printlog=False, show_operation=False,
                      debug=False, related_app_max_try=3):
        """
        Automates a task based on the current UI and task description.
        Args:
            step_id (int): Identifier for the current step.
            task (str): Description of the task to be automated.
            except_apps (list, optional): Apps to be excluded.
            printlog (bool): Enables logging if True.
            show_operation (bool): Shows UI operation if True.
            related_app_max_try (int): Max attempts to launch related apps.
        Returns:
            _Step: Step information.
        """

        step_record = AutoModeStep(step_id)  # Create a new step with the given step_id

        ui_data = self.capture_ui_information()  # Capture the current UI and analyze it for further processing
        step_record.set_attributes(ui_data=ui_data)  # Assign UI data to the step

        relation = self.app_tasker.check_task_ui_relation(ui_data, task, except_elements=except_apps, printlog=printlog)
        # relationship of the current UI with the task
        step_record.set_attributes(relation=relation)

        if relation.relation == 'Completed':
            # If task is already completed
            step_record.set_attributes(execution_result="Task is completed.")
            return step_record
        elif relation.relation == 'Unrelated':
            # Check for a back navigation possibility if current UI is unrelated to the task
            back_availability_action = self.app_tasker.check_go_back_availability(ui_data, task,
                                                                                reset_history=True, printlog=printlog)
            if back_availability_action.action.lower() == 'click':
                # Execute the recommended back navigation action
                self.execute_ui_operation(back_availability_action, ui_data, show_operation)
                step_record.set_attributes(recommended_action=back_availability_action, is_go_back=True,
                                           execution_result="Enter next turn.")
                if debug:
                    step_record.annotate_ui_openation()
                return step_record
            else:
                # If back navigation is not possible, look for related apps
                step_record.set_attributes(recommended_action=back_availability_action)
                excepted_related_apps = self.system_connector.get_current_package_and_activity_name()['package_name']
                device_app_list = self.system_connector.get_app_list_on_the_device()

                # Try to find and launch a related app
                for i in range(related_app_max_try):
                    rel_app = self.app_recommender.check_related_apps(task, app_list=device_app_list,
                                                                      except_apps=excepted_related_apps,
                                                                      printlog=printlog)
                    if rel_app == 'None':
                        step_record.set_attributes(execution_result="No related app can be found.")
                        return step_record
                    else:
                        self.system_connector.launch_app(rel_app)
                        cur_app, cur_activity = self.system_connector.get_current_package_and_activity_name().values()
                        if cur_app in rel_app:
                            step_record.set_attributes(execution_result="Enter next turn.")
                            return step_record
                        else:
                            excepted_related_apps.append(rel_app)
                step_record.set_attributes(execution_result="Failed to launch related apps within max attempts.")
                return step_record
        else:
            # If the relation is neither completed nor unrelated
            # Check for an action to perform in the current UI
            action = self.app_tasker.check_ui_action(ui_data, task, printlog=printlog)
            self.execute_ui_operation(action, ui, show_operation)
            step_record.set_attributes(recommended_action=action, execution_result="Enter next turn.")
            if debug:
                step_record.annotate_ui_openation()
            return step_record