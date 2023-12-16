from SystemConnection import SystemConnector
from ModelManagement import ModelManager
import json


class _AppAvailabilityChecker:
    def __init__(self, system_prompt=None, **kwargs):
        """
        Initializes the AppAvailabilityChecker.
        Creates instances of SystemConnector and ModelManager.
        Sets up a base prompt template for checking app relevance.
        """
        self.__system_connector = SystemConnector()

        self.__model_manager = ModelManager()
        self.__model_manager.initialize_llm_model("app_availability_checker_model", system_prompt=system_prompt,
                                                  **kwargs)

        # Initialize the base prompt template
        self.__base_prompt = 'Identify the app related to the task "{task}". Consider the following apps: ' \
                             '[{app_list}]. \n' \
                             'Note: Exclude apps that cannot be launched or have been launched already: ' \
                             '[{exp_apps}]. \n' \
                             'Respond in JSON format with (1) the app package name if related, or "None" ' \
                             'if unrelated, and (2) a brief reason. \n' \
                             'Format: {{"App": "<app_package_or_None>", "Reason": "<explanation>"}}. \n' \
                             'Example: {{"App": "com.example.app", "Reason": "Directly performs the task"}} or ' \
                             '{{"App": "None", "Reason": "No app is related"}}.'

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
            self.__model_manager.reset_llm_conversations("app_availability_checker_model")

            if app_list is None:
                app_list = self.get_available_apps()

            # Provide a default empty list if except_apps is None
            except_apps_str = '; '.join(except_apps) if except_apps else ''

            print('--- Check Related App ---')
            # Format the prompt with specific task and app list
            conversation = self.__base_prompt.format(task=task, app_list='; '.join(app_list),
                                                     exp_apps=except_apps_str)

            related_apps = self.__model_manager.create_llm_conversation("app_availability_checker_model", conversation,
                                                                        printlog=printlog)['content']
            related_apps = json.loads(related_apps)
            print(related_apps)
            return related_apps
        except Exception as e:
            raise e