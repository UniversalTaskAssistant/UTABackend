import time
import json
from DataStructures.config import *
from ._GooglePlay import _GooglePlay


class ThirdPartyAppManager:
    def __init__(self, model_manager):
        """
        Initialize ThirdPartyAppManager object.
        """
        self.__model_manager = model_manager
        self.__googleplay = _GooglePlay()

        self.__app_analyse_prompt = 'Summarize the main tasks that the app {title} can perform for senior users ' \
                                    'who are not familiar with it. ' \
                                    'Review the app description: "{description}". \n' \
                                    'Focus on specific functionality, presenting them as simple, user-friendly ' \
                                    'tasks. Each task should be distinct and cover only one aspect of the app. ' \
                                    'List the tasks in a format accessible to seniors, using clear examples where ' \
                                    'possible. End each task with a semicolon and start with a dash. \n' \
                                    'Example: \n' \
                                    '- Watch music videos and stay updated with trends; \n' \
                                    '- Subscribe to favorite channels for personalized content; \n' \
                                    '...and so on.'

        self.__apps_analysis_prompt = 'Analyze the list of apps and summarize the main tasks that each app can ' \
                                      'perform for senior users who are not familiar with them. Review each app\'s ' \
                                      'description and focus on specific functionality, presenting them as simple, ' \
                                      'user-friendly tasks. For each app, list its tasks in a format accessible to ' \
                                      'seniors, using clear examples where possible. Each task should be distinct and ' \
                                      'cover only one aspect of the app. List the tasks with a dash and end with a ' \
                                      'semicolon. Structure the output as a list of lists, where each inner list ' \
                                      'corresponds to the tasks of one app. \n' \
                                      'Example for a single app: \n' \
                                      '- Watch music videos and stay updated with trends; \n' \
                                      '- Subscribe to favorite channels for personalized content; \n' \
                                      '...and so on. \n\n' \
                                      'Apps to analyze: \n{app_details}'

        self.__availability_check_prompt = 'Identify the app related to the task "{task}". Consider the following' \
                                           ' apps: [{app_list}]. \n' \
                                           'Note: Exclude apps that cannot be launched or have been launched ' \
                                           'already: [{exp_apps}]. \n' \
                                           'Respond in JSON format with (1) the app package name if related, ' \
                                           'or "None" if unrelated, and (2) a brief reason. \n' \
                                           'Format: {{"App": "<app_package_or_None>", "Reason": "<explanation>"}}. \n' \
                                           'Example: {{"App": "com.example.app", "Reason": "Directly performs the ' \
                                           'task"}} or {{"App": "None", "Reason": "No app is related"}}.'

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

    def conclude_app_functionality(self, tar_app, printlog=False):
        """
        Conclude the functionality of given app.
        Args:
            tar_app (dict): App including description, collected from google play
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Functionality of given app.
        """
        try:
            start = time.time()
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            new_conversation = self.__app_analyse_prompt.format(title=tar_app['title'],
                                                                description=tar_app['description'], printlog=printlog)
            conversations.append({'role': 'user', 'content': new_conversation})

            task_list = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)['content']
            task_list = task_list.replace('\n', '').split(';')
            task_list = task_list[:-1] if len(task_list[-1]) == 0 else task_list
            task_list = [t.replace('\n', '').replace(' -', '-') for t in task_list]
            print('Running Time:%.3fs, ' % (time.time() - start))
            return task_list
        except Exception as e:
            raise e

    def conclude_multi_apps_functionalities(self, apps_list, printlog=False):
        """
        Conclude the functionality of a list of apps.
        Args:
            apps_list (list): List of apps, each including description, collected from Google Play.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            A list of lists, where each inner list contains the functionalities of a respective app.
        """
        try:
            start = time.time()
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            app_details = '\n'.join([f'- {app["title"]}: {app["description"]}' for app in apps_list])
            new_conversation = self.__apps_analysis_prompt.format(app_details=app_details, printlog=printlog)
            conversations.append({'role': 'user', 'content': new_conversation})

            response = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)['content']
            app_sections = response.split('\n\n')
            task_list = []
            for section in app_sections:
                # Remove any leading or trailing whitespace and split the section into tasks
                tasks = section.replace('\n', '').strip().split(';')
                # Remove empty strings and extra spaces, and reformat tasks
                tasks = [task.strip().replace('\n', '').replace(' -', '-') for task in tasks if task.strip()]
                task_list.append(tasks)

            print('Running Time:%.3fs, ' % (time.time() - start))
            return task_list
        except Exception as e:
            raise e

    def check_related_apps(self, step, task, app_list, except_apps=None, printlog=False):
        """
        Checks for apps related to a given task.
        Args:
            step (AutoModeStep): AutoModeStep object containing current relation.
            task (Task): The task for which related apps are to be found.
            app_list (list, optional): A list of apps to consider. If None, fetches from the device.
            except_apps (list, optional): Apps to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            JSON data with related app information.
        """
        try:
            print('--- Check Related App ---')
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]

            # Provide a default empty list if except_apps is None
            except_apps_str = '; '.join(except_apps) if except_apps else ''

            # Format the prompt with specific task and app list
            new_conversation = self.__availability_check_prompt.format(task=task.task_description,
                                                                       app_list='; '.join(app_list),
                                                                       exp_apps=except_apps_str)
            conversations.append({'role': 'user', 'content': new_conversation})

            related_apps = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)['content']
            step.related_app_check_result = related_apps

            related_apps = json.loads(related_apps)
            print(related_apps)
            return related_apps
        except Exception as e:
            raise e

    def recommend_apps(self, step, search_tar, fuzzy=False, max_return=5):
        """
        Recommends apps based on a search term and summarizes their functionalities.
        Args:
            step (AutoModeStep): AutoModeStep object containing current relation.
            search_tar (str): The search term or target app name.
            fuzzy (bool): If True, performs a fuzzy search, returning multiple related apps.
            max_return (int): The maximum number of apps to return in a fuzzy search.

        Returns:
            A list of dictionaries with app titles and their summarized functionalities.
        """
        try:
            if fuzzy:
                app_list = self.search_apps_fuzzy(search_tar)[:max_return]
                app_functions = self.conclude_multi_apps_functionalities(app_list)
                result = [{'title': app_list[idx]['title'], 'function': one_func} for idx, one_func in
                          enumerate(app_functions)]
            else:
                tar_app = self.search_app_by_name(search_tar)
                app_function = self.conclude_app_functionality(tar_app)
                result = [{'title': tar_app['title'], 'function': app_function}]
            step.app_recommendation_result = result
            return result
        except Exception as e:
            raise e

    def download_app(self, app_link):
        # need further discussion
        pass
