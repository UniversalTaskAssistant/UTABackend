import json
import re
from uta.config import *


class TaskList:
    def __init__(self, model_manager):
        self.available_task_list = ['Set up a pin for the device',
                                    'Change the pin for the device']
        self.app_list = ['Android Settings', 'Android Settings']

        self.__model_manager = model_manager
        self.__base_prompt_task_match = 'Given the task {task}, select 0 to 3 most related tasks from the available task list.\n' \
                                        '!!!Available task list:\n' + str(self.available_task_list) + \
                                        '!!!Note:\n' \
                                        '1. ONLY use this JSON format to provide your answer: {{"RelatedTasks": ["<task from the list>"], "Reason": "<one-sentence reason>"}}' \
                                        '2. If no task in the list is related to the given task, answer "None" for the "RelatedTasks".\n' \
                                        '!!!Example:\n' \
                                        '1. {{"RelatedTasks": ["Set up a pin for the device"], "Reason": "The given task is related to device pin."}}\n' \
                                        '2. {{"RelatedTasks": "None", "Reason": "No related task in the list to the given task."}}'

        self.__base_prompt_app_match = 'Given an app list {app_list}, and an app name {app_name} needed by a phone user, please select the most relevant app package name from the app list.' \
                                       '!!!Note:\n' \
                                       '1. ONLY use this JSON format to provide your answer: {{"AppPackage": ["<selected app package from the app list>"], "Reason": "<one-sentence reason for selection>"}}' \
                                       '2. If no app package in the app list directly matches the given app name, select the one that seems most relevant as "AppPackage".' \
                                       '3. The result must contains "AppPackage" key. \n' \
                                       '!!!Example:\n' \
                                       '1. {{"AppPackage": "com.android.settings", "Reason": "The app name Android Settings is related to the app package com.android.settings."}}\n' \
                                       '2. {{"AppPackage": "com.android.camera2", "Reason": "The app name Camera is related to the app package com.android.camera2."}}'

    @staticmethod
    def transfer_to_dict(resp):
        """
        Transfer string model returns to dict format
        Args:
            resp (dict): The model returns.
        Return:
            resp_dict (dict): The transferred dict.
        """
        try:
            return json.loads(resp['content'])
        except Exception as e:
            regex = r'"([A-Za-z ]+?)":\s*(".*?[^\\]"|\'.*?[^\\]\')|\'([A-Za-z ]+?)\':\s*(\'.*?[^\\]\'|".*?[^\\]")'
            attributes = re.findall(regex, resp['content'])
            resp_dict = {}
            for match in attributes:
                key = match[0] if match[0] else match[2]  # Select the correct group for the key
                value = match[1] if match[1] else match[3]  # Select the correct group for the value
                resp_dict[key] = value
            return resp_dict

    def match_task_to_list(self, task):
        """
        Try to find 0-3 related tasks in the available task list for the given user task
        Args:
            task (Task): Task object
        Return:
            task_match (dict): {"RelatedTasks": [] or "None", "Reason":}
        """
        try:
            conversation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                            {"role": "user", "content": self.__base_prompt_task_match.format(task=task.task_description)}]
            resp = self.__model_manager.send_fm_conversation(conversation)
            task_match = self.transfer_to_dict(resp)
            task.res_task_match = task_match
            print(task_match)
            return task_match
        except Exception as e:
            print(resp)
            raise e

    def match_app_to_applist(self, task, app_list):
        """
        Try to find 0-3 related tasks in the available task list for the given user task
        Args:
            task (Task): Task object
            app_list (list): app lists in user's phone
        Return:
            task_match (dict): {"RelatedTasks": [] or "None", "Reason":}
        """
        try:
            conversation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                            {"role": "user", "content": self.__base_prompt_app_match.format(app_name=task.involved_app,
                                                                                            app_list=app_list)}]
            resp = self.__model_manager.send_fm_conversation(conversation)
            app_match = self.transfer_to_dict(resp)
            task.involved_app_package = app_match['AppPackage']
            print(app_match)
            return app_match
        except Exception as e:
            print(resp)
            raise e
