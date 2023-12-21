from ThirdPartyAppManagement import _ThirdPartyAppAnalyser, _ThirdPartyAppAvailabilityChecker, _ThirdPartyAppSearcher


class ThirdPartyAppManager:
    def __init__(self, model_manager):
        self.__model_manager = model_manager
        self.__app_analyser_identifier = 'app_analyser'
        self.__app_checker_identifier = 'app_checker'
        self.__model_manager.initialize_llm_model(identifier=self.__app_analyser_identifier)
        self.__model_manager.initialize_llm_model(identifier=self.__app_checker_identifier)

        self.__app_analyser_dict = _ThirdPartyAppAnalyser(self.__app_analyser_identifier, self.__model_manager)
        self.__app_checker_dict = _ThirdPartyAppAvailabilityChecker(self.__app_checker_identifier, self.__model_manager)
        self.__app_searcher = _ThirdPartyAppSearcher()

    def search_app_by_name(self, app_name):
        """
        Searches for an app by its name on the Google Play store.
        Args:
            app_name (str): The name of the app to search for.
        Returns:
            The most relevant app's information if found, otherwise None.
        """
        return self.__app_searcher.search_app_by_name(app_name)

    def search_apps_fuzzy(self, disp):
        """
        Performs a fuzzy search for apps on the Google Play store.
        Args:
            disp (str): The display term to search for.
        Returns:
            A list of apps that are related to the search term.
        """
        return self.__app_searcher.search_apps_fuzzy(disp)

    def check_related_apps(self, task, app_list, except_apps=None, printlog=False):
        """
        Checks for apps related to a given task.
        Args:
            task (str): The task for which related apps are to be found.
            app_list (list): A list of apps to consider.
            except_apps (list, optional): Apps to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            JSON data with related app information.
        """
        return self.__app_checker_dict.check_related_apps(task, app_list, except_apps, printlog)

    def conclude_app_functionality(self, tar_app, printlog=False):
        """
        Conclude the functionality of given app.
        Args:
            tar_app (dict): App including description, collected from google play
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Functionality of given app.
        """
        return self.__app_analyser_dict.conclude_app_functionality(tar_app, printlog)

    def recommend_apps(self, search_tar, fuzzy=False, max_return=5):
        """
        Recommends apps based on a search term and summarizes their functionalities.
        Args:
            search_tar (str): The search term or target app name.
            fuzzy (bool): If True, performs a fuzzy search, returning multiple related apps.
            max_return (int): The maximum number of apps to return in a fuzzy search.

        Returns:
            A list of dictionaries with app titles and their summarized functionalities.
        """
        try:
            if fuzzy:
                app_list = self.search_apps_fuzzy(search_tar)[:max_return]
                app_functions = [self.conclude_app_functionality(one_app) for one_app in app_list]
                return [{'title': app_list[idx]['title'], 'function': one_func} for idx, one_func in app_functions]
            else:
                tar_app = self.search_app_by_name(search_tar)
                app_function = self.conclude_app_functionality(tar_app)
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
    apps = app_mg.search_apps_fuzzy('chinese food')
    print(app_mg.conclude_app_functionality(apps[0]))
