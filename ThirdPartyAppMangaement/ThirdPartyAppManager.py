from . import _ThirdPartyAppAnalyser, _ThirdPartyAppAvailabilityChecker, _ThirdPartyAppSearcher


class ThirdPartyAppManager:
    def __init__(self, model_manager):
        self.__model_manager = model_manager
        self.__app_analyser_dict = dict()
        self.__app_checker_dict = dict()
        self.__app_searcher = None

    def initialize_app_analyser(self, analyser_identifier):
        """
        Initialize the app analyser with provided llm Model.
        Args:
            analyser_identifier: name of the new initialized app analyser.
        """
        assert analyser_identifier not in self.__app_analyser_dict
        self.__model_manager.initialize_llm_model(identifier=analyser_identifier)
        self.__app_analyser_dict[analyser_identifier] = _ThirdPartyAppAnalyser(analyser_identifier, self.__model_manager)

    def initialize_app_checker(self, checker_identifier, system_connector):
        """
        Initialize the app checker with provided llm Model and SystemConnector.
        Args:
            checker_identifier: name of the new initialized app checker.
            system_connector: SystemConnector.
        """
        assert checker_identifier not in self.__app_checker_dict
        self.__model_manager.initialize_llm_model(identifier=checker_identifier)
        self.__app_checker_dict[checker_identifier] = _ThirdPartyAppAvailabilityChecker(checker_identifier, self.__model_manager, system_connector)

    def initialize_app_searcher(self):
        """
        Initialize app searcher.
        """
        self.__app_searcher = _ThirdPartyAppSearcher()

    def search_app_by_name(self, app_name):
        """
        Searches for an app by its name on the Google Play store.
        Args:
            app_name (str): The name of the app to search for.
        Returns:
            The most relevant app's information if found, otherwise None.
        """
        if not self.__app_searcher:
            self.initialize_app_searcher()
        return self.__app_searcher.search_app_by_name(app_name)

    def search_apps_fuzzy(self, disp):
        """
        Performs a fuzzy search for apps on the Google Play store.
        Args:
            disp (str): The display term to search for.
        Returns:
            A list of apps that are related to the search term.
        """
        if not self.__app_searcher:
            self.initialize_app_searcher()
        return self.__app_searcher.search_apps_fuzzy(disp)

    def get_available_apps(self, checker_identifier):
        """
        Retrieves a list of available applications on the device.
        Returns:
            List of app package names.
        """
        assert checker_identifier in self.__app_checker_dict
        return self.__app_checker_dict[checker_identifier].get_available_apps()

    def get_package_name(self, checker_identifier):
        """
        Retrieves the package name of the currently active app on the device.
        Returns:
            Package name of the current app.
        """
        assert checker_identifier in self.__app_checker_dict
        return self.__app_checker_dict[checker_identifier].get_package_name()

    def check_related_apps(self, checker_identifier, task, app_list=None, except_apps=None, printlog=False):
        """
        Checks for apps related to a given task.
        Args:
            checker_identifier: identifier of initialized checker
            task (str): The task for which related apps are to be found.
            app_list (list, optional): A list of apps to consider. If None, fetches from the device.
            except_apps (list, optional): Apps to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            JSON data with related app information.
        """
        assert checker_identifier in self.__app_checker_dict
        return self.__app_checker_dict[checker_identifier].check_related_apps(task, app_list, except_apps, printlog)

    def conclude_app_functionality(self, analyser_identifier, tar_app, printlog=False):
        """
        Conclude the functionality of given app.
        Args:
            analyser_identifier: identifier of initialized analyser
            tar_app: target app to be analyzed.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Functionality of given app.
        """
        assert analyser_identifier in self.__app_analyser_dict
        return self.__app_analyser_dict[analyser_identifier].conclude_app_functionality(tar_app, printlog)

    def recommend_apps(self, analyser_identifier, search_tar, fuzzy=False, max_return=5):
        """
        Recommends apps based on a search term and summarizes their functionalities.

        Args:
            analyser_identifier: identifier of initialized analyser
            search_tar (str): The search term or target app name.
            fuzzy (bool): If True, performs a fuzzy search, returning multiple related apps.
            max_return (int): The maximum number of apps to return in a fuzzy search.

        Returns:
            A list of dictionaries with app titles and their summarized functionalities.
        """
        assert analyser_identifier in self.__app_analyser_dict
        assert self.__app_searcher is not None
        
        try:
            if fuzzy:
                app_list = self.search_apps_fuzzy(search_tar)[:max_return]
                app_functions = [self.conclude_app_functionality(analyser_identifier, one_app) for one_app in app_list]
                return [{'title': app_list[idx]['title'], 'function': one_func} for idx, one_func in app_functions]
            else:
                tar_app = self.search_app_by_name(search_tar)
                app_function = self.conclude_app_functionality(analyser_identifier, tar_app)
                return [{'title': tar_app['title'], 'function': app_function}]
        except Exception as e:
            raise e

    def download_app(self, app_link):
        # need further discussion
        pass


if __name__ == '__main__':
    from ModelManagement import ModelManager
    model_mg = ModelManager()

    app_mg = ThirdPartyAppManager(model_manager=model_mg)
