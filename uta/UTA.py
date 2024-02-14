from os.path import join as pjoin
import traceback

from uta.DataStructures import *
from uta.ModelManagement import ModelManager
from uta.SystemConnection import SystemConnector
from uta.AvailableTaskList import TaskList
from uta.TaskAction import TaskActionChecker
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
        self.task_list = TaskList(self.model_manager)
        self.task_action_checker = TaskActionChecker(self.model_manager)
        self.app_recommender = ThirdPartyAppManager(self.model_manager)
        # current data
        self.cur_user = None  # User object, current user
        self.cur_task = None  # Task object, current task

    def setup_user(self, user_id, device_resolution, app_list):
        """
        Set up folders for user, and store user info into the user.json
        'data/user_id/user.json
        Args:
            user_id (str): Identifier for the user.
            device_resolution (tuple): Specify the size/resolution of the UI
            app_list (list): List of the names of installed apps
        """
        user = User(user_id=user_id, device_resolution=device_resolution, app_list=app_list)
        self.system_connector.save_user(user)
        self.cur_user = user
        return user

    def instantiate_user_task(self, user_id, task_id, user_msg=None):
        """
        Instantiate a User object to get the user info
        Instantiate a Task object by loading an existing one or creating a new one according to the given info
        Args:
            user_id (str): User id to identify the folder
            task_id (str): Task id to identify the file
            user_msg (str): User's input message. For new task, it is the task description. For existing task, append it to conversation.
        Returns:
            user (User): User object to store user info
            task (Task): Task object
        """
        user = self.system_connector.load_user(user_id=user_id)
        task = self.system_connector.load_task(user_id=user_id, task_id=task_id)
        # if the task does not exist, creat a new one within the user's folder
        if not task:
            task = Task(task_id=task_id, user_id=user_id)
            # set the user message as the task description for a new task
            if user_msg:
                task.task_description = user_msg
        else:
            if user_msg:
                if task.res_task_match.get('State') and 'related' in task.res_task_match['State'].lower() or \
                        task.res_task_match.get('State') is None and 'related' in str(task.res_task_match).lower():
                    task.clarification_user_msg = user_msg
                else:
                    task.selected_task = user_msg
                    task.involved_app = self.task_list.app_list[self.task_list.available_task_list.index(user_msg)]
                    task.step_hint = self.task_list.step_list[self.task_list.available_task_list.index(user_msg)]
        self.cur_user = user
        self.cur_task = task
        return user, task

    '''
    ************************
    *** Task Declaration ***
    ************************
    '''
    def fetch_available_task_list(self):
        """
        Fetch the current available task list
        Return:
            available_task_list (list): list of task descriptions (string)
        """
        return self.task_list.available_task_list

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
        try:
            print('\n*** Declare task ***')
            user, task = self.instantiate_user_task(user_id, task_id, user_msg)

            if task.involved_app is not None:
                match_app = self.task_list.match_app_to_applist(task, user.app_list)
                self.system_connector.save_task(task)
                return match_app

            declare_resp = self.task_list.match_task_to_list(task)
            self.system_connector.save_task(task)
            return declare_resp
        except Exception as e:
            error_trace = traceback.format_exc()
            action = {"Action": "Error at the backend.", "Exception": e, "Traceback": error_trace}
            print(action)
            return action

    '''
    ***********************
    *** Task Automation ***
    ***********************
    '''
    def process_ui_data(self, ui_img_file, ui_xml_file, device_resolution, show=False):
        """
        Process ui dato
        Args:
            ui_img_file (path): Screenshot image path
            ui_xml_file (path): VH xml file path
            device_resolution (tuple): Device resolution
            show (bool): True to show the detection result
        Return:
            ui (UIData): ui data with processing results
        """
        ui = UIData(screenshot_file=ui_img_file, xml_file=ui_xml_file, ui_resize=device_resolution)
        self.ui_processor.process_ui(ui, show=show)
        return ui

    def automate_task(self, user_id, task_id, ui_img_file, ui_xml_file,
                      package_name=None, activity_name=None, keyboard_active=False, printlog=False):
        """
        Identify the action on the current ui to automate the task
        Args:
            user_id (str): ui id
            task_id (str): task id
            ui_img_file (path): Screenshot image path
            ui_xml_file (path): VH xml file path
            package_name (str): Current app name
            activity_name (str): Current page name
            keyboard_active (bool): If the keyboard is active, can only input text when the keyboard is active
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action (dict): {"Action": }
        """
        try:
            # 0. retrieve task info
            user, task = self.instantiate_user_task(user_id, task_id)
            task.cur_package = package_name
            task.cur_activity = activity_name
            task.keyboard_active = keyboard_active

            # 1. process ui
            ui = self.process_ui_data(ui_img_file, ui_xml_file, user.device_resolution)
            self.system_connector.save_ui_data(ui, output_dir=pjoin(self.system_connector.user_data_root, user_id, task_id))

            # 2. act step
            task.conversation_automation = []  # clear up the conversation of previous ui
            # check action on the UI by checking the relation and target elements
            action = self.task_action_checker.action_on_ui(ui, task, printlog)
            # if not complete, check if the UI is user decision page
            if action['Action'] != 'Complete':
                # check user decision page
                ui_check = self.ui_processor.check_ui_decision_page(ui)
                if ui_check.get('Component') and 'none' not in ui_check['Component'].lower() or \
                        ui_check.get('Component') is None and 'none' not in str(ui_check).lower():
                    action = {"Action": "User Decision", **ui_check}
                    task.relations.append({"Relation": "None", "Element Id": "None", "Reason": "None"})
                    task.actions.append(action)
                    return ui, action
            # if the current UI is unrelated, search for other apps
            if action['Action'] == 'Other App':
                related_app = self.app_recommender.check_related_apps(task=task, app_list=user.app_list)
                if related_app.get('App') and 'none' not in related_app['App'].lower() or \
                        related_app.get('App') is None and 'none' not in str(related_app).lower():
                    task.related_app = related_app
                    action = {"Action": "Launch", "Description": "Launch app", **related_app}
                else:
                    action = {"Action": "Infeasible", "Description": "No related app installed.", **related_app}
                task.actions[-1] = action  # we record the launch action here to instead "other app"

            self.system_connector.save_task(task)
            return ui, action
        except Exception as e:
            error_trace = traceback.format_exc()
            action = {"Action": "Error at the backend.", "Exception": e, "Traceback": error_trace}
            print(action)
            return None, action


if __name__ == '__main__':
    uta = UTA()
    uta.automate_task('user1', 'task3', ui_img_file='../data/user1/task3/0.png',
                      ui_xml_file='../data/user1/task3/0.xml')
