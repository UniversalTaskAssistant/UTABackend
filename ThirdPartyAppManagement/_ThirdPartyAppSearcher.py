from . import _GooglePlay


class _ThirdPartyAppSearcher:
    def __init__(self):
        self.__googleplay = _GooglePlay()

    def search_app_by_name(self, app_name):
        """
        Searches for an app by its name on the Google Play store.
        Args:
            app_name (str): The name of the app to search for.
        Returns:
            The most relevant app's information if found, otherwise None.
        """
        return self.__googleplay.search_app_by_name(app_name)

    def search_apps_fuzzy(self, disp):
        """
        Performs a fuzzy search for apps on the Google Play store.
        Args:
            disp (str): The display term to search for.
        Returns:
            A list of apps that are related to the search term.
        """
        return self.__googleplay.search_apps_fuzzy(disp)
