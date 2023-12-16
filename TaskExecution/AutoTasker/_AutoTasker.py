from . import _TaskUIActionChecker, _TaskUIRelationChecker
from SystemConnection import SystemConnector
from AppRecommendation import AppRecommender
from UIProcessing import UIProcessor
import time
from ._Step import _AutoModeStep


class _AutoTasker:
    def __init__(self):
        """
        Initializes the AutoTasker.
        """
        self.relation_checker = _TaskUIRelationChecker()
        self.action_checker = _TaskUIActionChecker()
        self.system_connector = SystemConnector()
        self.app_recommender = AppRecommender()
        self.ui_processor = UIProcessor()

    def reset_model_agents(self):
        self.relation_checker.reset_ui_relation_checker()
        self.action_checker.reset_ui_action_checker()

    def automate_task(self, step_id, task, except_apps=None, printlog=False, show_operation=False, related_app_max_try=3):
        step = _AutoModeStep(step_id)

        ui = self.ui_processor.process_ui()
        step.set_attributes(ui_data=ui)

        relation = self.relation_checker.check_relation(step_id, ui, task, except_apps, printlog)
        step.set_attributes(relation=relation)

        if relation['Relation'] == 'Completed':
            print('[- Task is Completed -]')
            return step, "Task is completed"
        elif relation['Relation'] == 'Unrelated':
            back_availability_action = self.action_checker.check_go_back_availability(step_id, ui, task,
                                                                                reset_history=True, printlog=printlog)
            if back_availability_action.action.lower() == 'click':
                self.execute_ui_operation(back_availability_action, ui, show_operation)
                step.set_attributes(recommend_action=back_availability_action, is_go_back=True)
                return step, "Enter next turn"
            else:
                step.set_attributes(recommend_action=back_availability_action)
                excepted_related_apps = [self.app_recommender.get_package_name()]
                device_app_list = self.system_connector.get_app_list_on_the_device()

                for i in range(related_app_max_try):
                    rel_app = self.app_recommender.check_related_apps(task, app_list=device_app_list,
                                                                  except_apps=excepted_related_apps, printlog=printlog)
                    if rel_app == 'None':
                        return step, "No related app can be found"
                    else:
                        self.system_connector.launch_app(rel_app)
                        cur_app, cur_activity = self.system_connector.get_current_package_and_activity_name().values()
                        if cur_app in rel_app:
                            return step, "Enter next turn"
                        else:
                            excepted_related_apps.append(rel_app)
                return step, "Failed to launch related apps within max attempts"
        else:
            action = self.action_checker.check_action(step_id, ui, task, printlog=printlog)
            self.execute_ui_operation(action, ui, show_operation)
            step.set_attributes(recommend_action=action)
            return step, "Enter next turn"

    def execute_ui_operation(self, action, ui, show=False, waiting_time=2):
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