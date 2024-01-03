import json


class _ThirdPartyAppAvailabilityChecker:
    def __init__(self, model_identifier, model_manager):
        """
        Initializes the AppAvailabilityChecker.
        Needs instances of SystemConnector and Initialised ModelManager.
        """
        self.__model_identifier = model_identifier
        self.__model_manager = model_manager

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

    def initialize_agent(self):
        """
            Initialize llm model in model manager.
        """
        if self.is_agent_initialized():
            self.delete_agent()
        self.__model_manager.initialize_llm_model(identifier=self.__model_identifier)

    def is_agent_initialized(self):
        """
        Check whether agent is initialized.
        """
        return self.__model_manager.is_llm_model_initialized(identifier=self.__model_identifier)

    def delete_agent(self):
        """
        Remove llm model in model manager.
        """
        self.__model_manager.delete_llm_model(identifier=self.__model_identifier)

    def check_related_apps(self, task, app_list, except_apps=None, printlog=False):
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
            self.__model_manager.reset_llm_conversations(self.__model_identifier)

            # Provide a default empty list if except_apps is None
            except_apps_str = '; '.join(except_apps) if except_apps else ''

            print('--- Check Related App ---')
            # Format the prompt with specific task and app list
            conversation = self.__base_prompt.format(task=task, app_list='; '.join(app_list),
                                                     exp_apps=except_apps_str)

            related_apps = self.__model_manager.create_llm_conversation(self.__model_identifier, conversation,
                                                                        printlog=printlog)['content']
            related_apps = json.loads(related_apps)
            print(related_apps)
            return related_apps
        except Exception as e:
            raise e
