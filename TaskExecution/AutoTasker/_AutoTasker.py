from . import _TaskUIActionChecker, _TaskUIRelationChecker
import time
from DataStructures import _AutoModeStep


class _AutoTasker:
    def __init__(self, img_path, xml_path, ui_resize, output_dir, **kwargs):
        """
        Initializes the AutoTasker which automates UI interactions based on task requirements.
        Args:
            img_path (str): Path to save the captured screenshot.
            xml_path (str): Path to save the UI hierarchy XML.
            ui_resize (tuple): Dimensions to resize UI images.
            output_dir (str): Directory for output data.
            **kwargs: Additional keyword arguments.
        """
        self.relation_checker = _TaskUIRelationChecker(kwargs['relation_checker_model'], kwargs['model_manager'])
        self.action_checker = _TaskUIActionChecker(kwargs['action_checker_model'], kwargs['model_manager'])
        self.system_connector = kwargs['system_connector']
        self.app_recommender = kwargs['third_party_app_manager']
        self.ui_processor = kwargs['ui_processor']

        self.system_connector.connect_device()

        self.img_path = img_path
        self.xml_path = xml_path
        self.ui_resize = ui_resize
        self.output_dir = output_dir

    def reset_model_agents(self):
        """
        Resets the internal state of model agents used for UI relation and action checking.
        """
        self.relation_checker.reset_ui_relation_checker()
        self.action_checker.reset_ui_action_checker()

    def automate_task(self, step_id, task, except_apps=None, printlog=False, show_operation=False,
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
        step_record = _AutoModeStep(step_id)  # Create a new step with the given step_id

        ui = self.__capture_and_analyse_ui()  # Capture the current UI and analyze it for further processing
        step_record.set_attributes(ui_data=ui)  # Assign UI data to the step

        relation = self.relation_checker.check_relation(ui, task, except_apps, printlog)  # Check the
        # relationship of the current UI with the task
        step_record.set_attributes(relation=relation)

        if relation['Relation'] == 'Completed':
            # If task is already completed
            step_record.set_attributes(execution_result="Task is completed.")
            return step_record
        elif relation['Relation'] == 'Unrelated':
            # Check for a back navigation possibility if current UI is unrelated to the task
            back_availability_action = self.action_checker.check_go_back_availability(ui, task,
                                                                                reset_history=True, printlog=printlog)
            if back_availability_action.action.lower() == 'click':
                # Execute the recommended back navigation action
                self.execute_ui_operation(back_availability_action, ui, show_operation)
                step_record.set_attributes(recommended_action=back_availability_action, is_go_back=True,
                                           execution_result="Enter next turn.")
                if debug:
                    step_record.annotate_ui_openation()
                return step_record
            else:
                # If back navigation is not possible, look for related apps
                step_record.set_attributes(recommended_action=back_availability_action)
                excepted_related_apps = [self.app_recommender.get_package_name()]
                device_app_list = self.system_connector.get_app_list_on_the_device()

                # Try to find and launch a related app
                for i in range(related_app_max_try):
                    rel_app = self.app_recommender.check_related_apps(task, app_list=device_app_list,
                                                                  except_apps=excepted_related_apps, printlog=printlog)
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
            action = self.action_checker.check_action(step_id, ui, task, printlog=printlog)
            self.execute_ui_operation(action, ui, show_operation)
            step_record.set_attributes(recommended_action=action, execution_result="Enter next turn.")
            if debug:
                step_record.annotate_ui_openation()
            return step_record

    def __capture_and_analyse_ui(self):
        """
        Captures the current UI and processes it for automation.
        Returns:
            Processed UI data.
        """
        screenshot = self.system_connector.cap_screenshot()
        vh = self.system_connector.cap_current_ui_hierarchy()

        self.system_connector.save_xml(vh, self.xml_path)
        self.system_connector.save_img(screenshot, self.img_path)

        ui_data = self.ui_processor.load_ui_data(self.img_path, self.xml_path, self.ui_resize, self.output_dir)
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