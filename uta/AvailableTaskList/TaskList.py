import json
import re
from uta.config import *


class TaskList:
    def __init__(self, model_manager):
        self.available_task_list = ['Create a pin for the device', 'Change the pin for the device', 'Create the fingerprint for device', 'Change the fingerprint for device',
                                    'Turn on/off the haptics', 'Increase/decrease the volume', 'Change the ringtone', 'Change the tesxtone', 'Turn on/off vibration for text',
                                    'Turn on/off vibration for calls', 'Turn on/off lock screen sound', 'Turn on/off the text sound',
                                    'View the notifications', 'Delete notifications', 'Make the text size of device bigger/smaller', 'Change the date', 'Change the time',
                                    'Hide/show name when calling', 'Block/unblock a number', 'Stop my phone from receiving calls, texts, or emails', 'Add contact information to the lock screen',
                                    'Use a photo as background',
                                    'Take a photo using Camera', 'View a photo using Google Photo', 'Delete a photo using Google Photo', 'Edit a photo using Google Photo', 'Share a photo using Google Photo',
                                    'Access Gmail App', 'Open and view files ', 'Share a file from Files app', 'Delete a file from Files app']
        self.app_list = ['Android Settings'] * 22 + ["Phone Camera"] + ["Google Photo"] * 4 + ["Gmail"] + ["Android File"] * 3

        self.__system_prompt = 'You are an Android mobile assistant, you can only perform the following list of tasks:\n' + str(self.available_task_list) + '\n'\
                               'Given a user intention, try to select 3 most related tasks that match the user intention.\n' \
                               '!!!Cases:' \
                               '1. If successfully match related tasks, respond in the JSON format:{{"State": "Match", "RelatedTasks": ["<task from the list>"], "Reason": "<one-sentence reason>"}}\n' \
                               '2. If the task is related to the tasks in the list but you need more details to make selection,  respond in the JSON format:{{"State": "Related", "Question":"<Question>", "Options":["<sample answers>"]}}\n' \
                               '3. If the task is totally unrelated to any of the tasks in the list, respond in the JSON format:{{"State": "Unrelated"}}'

        self.__model_manager = model_manager
        self.__base_prompt_task_match = 'User intention: {task}.'

        self.__base_prompt_app_match = 'Given an app list {app_list}, and an app name {app_name} needed by a phone user, please select the most relevant app package name from the app list.' \
                                       '!!!Note:\n' \
                                       '1. ONLY use this JSON format to provide your answer: {{"AppPackage": "<selected app package from the app list>", "Reason": "<one-sentence reason for selection>"}}' \
                                       '2. If no app package in the app list directly matches the given app name, select the one that seems most relevant as "AppPackage".' \
                                       '3. The result must contains "AppPackage" key. \n' \
                                       '!!!Example:\n' \
                                       '1. {{"AppPackage": "com.android.settings", "Reason": "The app name Android Settings is related to the app package com.android.settings."}}\n' \
                                       '2. {{"AppPackage": "com.android.camera2", "Reason": "The app name Camera is related to the app package com.android.camera2."}}'

    @staticmethod
    def wrap_task_info(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = ''
        if len(task.user_clarify) > 0:
            prompt += '!!!Context:\n'
            prompt += '(Historical information for the task clarification:' + str(task.conversation_pure_clarification) + ')\n'
        return prompt

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
            prompt = self.wrap_task_info(task)
            prompt += self.__base_prompt_task_match.format(task=task.task_description)
            conversation = [{'role': 'system', 'content': self.__system_prompt},
                            {"role": "user", "content": prompt}]
            resp = self.__model_manager.send_fm_conversation(conversation)
            task.res_task_match = self.transfer_to_dict(resp)
            task.res_task_match['Proc'] = 'TaskMatch'
            print(task.res_task_match)
            return task.res_task_match
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
            app_match['Proc'] = 'AppMatch'
            task.involved_app_package = app_match['AppPackage']
            print(app_match)
            return app_match
        except Exception as e:
            print(resp)
            raise e


if __name__ == '__main__':
    task_list = TaskList(None)
