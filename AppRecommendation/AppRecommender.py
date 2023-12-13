from . import _AppAnalyser, _AppAvailabilityChecker, _AppSearcher


class AppRecommender:
    def __init__(self):
        self.analyser = _AppAnalyser()
        self.app_checker = _AppAvailabilityChecker()
        self.searcher = _AppSearcher()

    def search_app_by_name(self, app_name):
        """
        Searches for an app by its name on the Google Play store.
        Args:
            app_name (str): The name of the app to search for.
        Returns:
            The most relevant app's information if found, otherwise None.
        """
        return self.searcher.search_app_by_name(app_name)

    def search_apps_fuzzy(self, disp):
        """
        Performs a fuzzy search for apps on the Google Play store.
        Args:
            disp (str): The display term to search for.
        Returns:
            A list of apps that are related to the search term.
        """
        return self.searcher.search_apps_fuzzy(disp)

    def get_available_apps(self):
        """
        Retrieves a list of available applications on the device.
        Returns:
            List of app package names.
        """
        return self.app_checker.get_available_apps()

    def get_package_name(self):
        """
        Retrieves the package name of the currently active app on the device.
        Returns:
            Package name of the current app.
        """
        return self.app_checker.get_package_name()

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
        return self.app_checker.check_related_apps(task, app_list, except_apps, printlog)

    def conclude_app_functionality(self, tar_app, printlog=False):
        """
        Conclude the functionality of given app.
        Args:
            tar_app: target app to be analyzed.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Functionality of given app.
        """
        return self.analyser.conclude_app_functionality(tar_app, printlog)

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
        if fuzzy:
            app_list = self.search_apps_fuzzy(search_tar)[:max_return]
            app_functions = [self.conclude_app_functionality(one_app) for one_app in app_list]
            return [{'title': app_list[idx]['title'], 'function': one_func} for idx, one_func in app_functions]
        else:
            tar_app = self.search_app_by_name(search_tar)
            app_function = self.conclude_app_functionality(tar_app)
            return [{'title': tar_app['title'], 'function': app_function}]

    def download_app(self, app_link):
        # need further discussion
        pass