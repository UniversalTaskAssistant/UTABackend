from . import _TaskUIActionChecker, _TaskUIRelationChecker
from SystemConnection import SystemConnector
from AppRecommendation import AppRecommender
import time


class _AutoTasker:
    def __init__(self):
        """
        Initializes the AutoTasker.
        """
        self.relation_checker = _TaskUIRelationChecker()
        self.action_checker = _TaskUIActionChecker()
        self.system_connector = SystemConnector()
        self.app_recommender = AppRecommender()
        self.ui_processor = None
        self.hitory_manager = None

    def reset_model_agents(self):
        self.relation_checker.reset_ui_relation_checker()
        self.action_checker.reset_ui_action_checker()

    def automate_task(self, task, except_apps=None, printlog=False, show_operation=False, related_app_max_try=3):
        gui = self.ui_processor.collect_analyse_ui()
        relation = self.relation_checker.check_relation(gui, task, except_apps, printlog)

        if relation['Relation'] == 'Completed':
            self.hitory_manager.record_task()
            print('[- Task is Completed -]')
            return "Task is completed"
        elif relation['Relation'] == 'Unrelated':
            back_availability = self.action_checker.check_go_back_availability(gui, task, reset_history=True,
                                                                               printlog=printlog)
            if back_availability['Can'].lower() == 'yes':
                action = {'Action': 'Click', "Element": back_availability['Element'],
                          'Description': back_availability['Description']}
                self.execute_ui_operation(action, gui, show_operation)
                self.hitory_manager.record_step()
                return "Enter next turn"
            else:
                excepted_related_apps = [self.app_recommender.get_package_name()]
                device_app_list = self.system_connector.get_app_list_on_the_device()

                for i in range(related_app_max_try):
                    rel_app = self.app_recommender.check_related_apps(task, app_list=device_app_list,
                                                                  except_apps=excepted_related_apps, printlog=printlog)
                    if rel_app == 'None':
                        return "No related app can be found"
                    else:
                        self.system_connector.launch_app(rel_app)
                        cur_app, cur_activity = self.system_connector.get_current_package_and_activity_name().values()
                        if cur_app in rel_app:
                            self.hitory_manager.record_step()
                            return "Enter next turn"
                        else:
                            excepted_related_apps.append(rel_app)
                return "Failed to launch related apps within max attempts"
        else:
            action = self.action_checker.check_action(gui, task, printlog=printlog)
            self.execute_ui_operation(action, gui, show_operation)
            self.hitory_manager.record_step()
            return "Enter next turn"

    def execute_ui_operation(self, action, gui, show=False, waiting_time=2):
        element = gui.elements[action['Element']]
        if action['Action'].lower() == 'click':
            self.system_connector.click_screen(gui, element, show)
        elif action['Action'].lower() == 'scroll up':
            self.system_connector.up_scroll_screen(gui, element, show)
        elif action['Action'].lower() == 'scroll down':
            self.system_connector.down_scroll_screen(gui, element, show)
        elif action['Action'].lower() == 'swipe right':
            self.system_connector.right_swipe_screen(gui, element, show)
        elif action['Action'].lower() == 'swipe left':
            self.system_connector.left_swipe_screen(gui, element, show)
        elif action['Action'].lower() == 'long press':
            self.system_connector.long_press_screen(gui, element, show)
        elif action['Action'].lower() == 'input':
            self.system_connector.input_text(action['Input Text'])
        else:
            raise ValueError(f"No expected action returned from model, returned action: {action['Action']}")
        time.sleep(waiting_time)