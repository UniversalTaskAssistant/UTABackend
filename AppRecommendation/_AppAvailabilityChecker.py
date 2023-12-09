from SystemConnection import SystemConnector
from ModelManagement import ModelManager


class _AppAvailabilityChecker:
    def __init__(self):
        self.__system_connector = SystemConnector()
        self.__model_manager = ModelManager()
        self.__data_manager = None

    def get_available_apps(self):
        return self.__system_connector.get_app_list_on_the_device()

    def check_related_apps(self, task, app_list=None, except_apps=None, printlog=False):
        if app_list is None:
            app_list = self.get_available_apps()

        print('--- Check Related App ---')
        # add except apps
        exp_apps = self.__data_manager.modify_text(except_apps)

        conversation = 'Which app is the related one to complete the task "' + task + '"? ' \
                                                                                      '@List of app package names (separated by ";"): [' + \
                        '; '.join(app_list) + ']' + \
                        'Answer the question in JSON format to give (1) App package name selected from the given app list, if no related found, answer "None"; (2) Reason in one sentence' \
                        'Format: {"App":, "Reason":}. Example: {"App": "Package Name", "Reason":} or {"App": "None", "Reason":}. \n' \
                        + exp_apps
        related_apps = self.__model_manager.create_text_conversation(conversation)

        print(related_apps)
        return related_apps