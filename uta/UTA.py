from os.path import join as pjoin

from uta.DataStructures import *
from uta.ModelManagement import ModelManager
from uta.SystemConnection import SystemConnector
from uta.TaskDeclearation import TaskDeclarator
from uta.TaskAction import TaskActionChecker
from uta.ThirdPartyAppManagement import ThirdPartyAppManager
from uta.UIProcessing import UIProcessor
from uta.config import *


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
                task.conversation_clarification.append({'role': 'user', 'content': "Response to the Question: " + user_msg})
                task.user_clarify.append(user_msg)
        self.cur_user = user
        self.cur_task = task
        return user, task

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
        print('\n*** Declare task ***')
        user, task = self.instantiate_user_task(user_id, task_id, user_msg)
        clarify = self.clarify_task(task)
        if clarify['Clear'] == 'True' or clarify['Clear'] == True:
            self.classify_task(task)
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
        print('* Clarify task *')
        return self.task_declarator.clarify_task(task=task, printlog=printlog)

    def classify_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        """
        print('* Classify task *')
        return self.task_declarator.classify_task(task=task, printlog=printlog)

    def decompose_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        """
        print('* Decompose task *')
        return self.task_declarator.decompose_task(task=task, printlog=printlog)

    '''
    ***********************
    *** Task Automation ***
    ***********************
    '''
    def automate_task(self, user_id, task_id, ui_img_file, ui_xml_file,
                      package_name=None, activity_name=None, printlog=False):
        """
        Identify the action on the current ui to automate the task
        Args:
            user_id (str): ui id
            task_id (str): task id
            ui_img_file (path): Screenshot image path
            ui_xml_file (path): VH xml file path
            package_name (str): Current app name
            activity_name (str): Current page name
            printlog (bool): If True, enables logging of outputs.
        Returns:
            ui (UIData)
            Action (dict): {"Action": }
        """
        # 0. retrieve task info
        user, task = self.instantiate_user_task(user_id, task_id)
        task.cur_package = package_name
        task.cur_activity = activity_name
        # 1. process ui
        ui = UIData(screenshot_file=ui_img_file, xml_file=ui_xml_file, ui_resize=user.device_resolution)
        self.ui_processor.process_ui(ui)
        self.system_connector.save_ui_data(ui, output_dir=pjoin(DATA_PATH, user_id, task_id))
        # 2. act based on task type
        task_type = task.task_type.lower()
        if 'general' in task_type:
            self.task_action_checker.action_inquiry(ui, task)
        elif 'system' in task_type or 'app' in task_type:
            task.conversation_automation = []   # clear up the conversation of previous ui
            # check action on the UI by checking the relation and target elements
            action = self.task_action_checker.action_on_ui(ui, task, printlog)
            # if the current UI is unrelated, search for other apps
            if action['Action'] == 'Other App':
                related_app = self.app_recommender.check_related_apps(task=task, app_list=user.app_list)
                if 'None' not in related_app['App']:
                    task.related_app = related_app['App']
                    action = {"Action": "Launch", "App": related_app['App'], "Description": "Launch app"}
                else:
                    action = {"Action": "Infeasible", "Description": "No related app installed."}
            self.system_connector.save_task(task)
            return ui, action


if __name__ == '__main__':
    uta = UTA()
    resp = uta.declare_task(user_id='1', task_id='1', user_msg='Send a message to my mom')
    resp = uta.declare_task(user_id='1', task_id='1', user_msg='Send it in whats app')
