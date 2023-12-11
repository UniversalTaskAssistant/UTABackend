from SystemConnection import SystemConnector
from ModelManagement import ModelManager
import json


class _AppAvailabilityChecker:
    def __init__(self):
        """
        Initializes the AppAvailabilityChecker.
        Creates instances of SystemConnector and ModelManager.
        Sets up a base prompt template for checking app relevance.
        """
        self.__system_connector = SystemConnector()
        self.__model_manager = ModelManager()

        # Initialize the base prompt template
        self.__base_prompt = 'Which app is the related one to complete the task "{task}"? ' \
                             '@List of app package names (separated by ";"): [{app_list}]' \
                             'Answer the question in JSON format to give (1) App package name ' \
                             'selected from the given app list, if no related found, answer "None"; ' \
                             '(2) Reason in one sentence. ' \
                             'Format: {{"App":, "Reason":}}. Example: {{"App": "Package Name", "Reason":}} or ' \
                             '{{"App": "None", "Reason":}}. \n' \
                             'These packages cannot be launched or have been launched already, ' \
                             'except them in your selection: [{exp_apps}]. \n'

    def get_available_apps(self):
        """
        Retrieves a list of available applications on the device.
        Returns:
            List of app package names.
        """
        return self.__system_connector.get_app_list_on_the_device()

    def get_package_name(self):
        """
        Retrieves the package name of the currently active app on the device.
        Returns:
            Package name of the current app.
        """
        return self.__system_connector.get_current_package_and_activity_name()['package_name']

    def check_related_apps(self, task, app_list=None, except_apps=None, printlog=False):
        """
        Checks for apps related to a given task.
        Args:
            task (str): The task for which related apps are to be found.
            app_list (list, optional): A list of apps to consider. If None, fetches from the device.
            except_apps (list, optional): Apps to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            JSON data with related app information.
        """
        try:
            if app_list is None:
                app_list = self.get_available_apps()

            # Provide a default empty list if except_apps is None
            except_apps_str = '; '.join(except_apps) if except_apps else ''

            print('--- Check Related App ---')
            # Format the prompt with specific task and app list
            conversation = self.__base_prompt.format(task=task, app_list='; '.join(app_list),
                                                     exp_apps=except_apps_str)

            related_apps = self.__model_manager.create_text_conversation(conversation, printlog=printlog)['content']
            related_apps = json.loads(related_apps)
            print(related_apps)
            return related_apps
        except Exception as e:
            raise e