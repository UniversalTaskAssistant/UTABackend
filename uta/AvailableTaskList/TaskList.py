import json
import re


class TaskList:
    def __init__(self, model_manager):
        self.available_task_list = ['Manage the pin for the device', 'Connect to Wi-Fi', 'Clean the cache of the phone',
                                    'Change the font size of the phone', 'Adjust screen brightness', 'Change wallpapers for my device',
                                    'Send text messages with Whatsapp', 'Make video calls with Whatsapp', 'Create a new group in Whatsapp',
                                    'Change privacy settings of Whatsapp', 'Change ringtone of Whatsapp', 'Block unwanted contacts in Whatsapp',
                                    'Host a meeting with Zoom', 'Join a meeting with Zoom', 'Schedule a meeting with Zoom',
                                    'Share the screen of the Android device during a Zoom meeting', 'Turn on/off the camera during a Zoom meeting', 'Turn on/off the microphone during a meeting',
                                    'Watch videos with YouTube', 'Subscribe to YouTube channels', 'Like/dislike videos in YouTube',
                                    'Comment on videos in YouTube', 'Adjust video quality in YouTube', 'Create a Playlist in YouTube',
                                    'Find products with Temu', 'Check product’s customer reviews with Temu', 'Check carts in Temu',
                                    'Save favourite items for future view in Temu', 'Check out in Temu', 'Contact customer service in Temu']
        self.task_info_list = [('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Infeasible'),
                               ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Communications', 'Infeasible'), ('Communications', 'Infeasible'), ('Communications', 'Infeasible'),
                               ('Communications', 'Feasible'), ('Communications', 'Feasible'), ('Communications', 'Feasible'),
                               ('Business', 'Feasible'), ('Business', 'Feasible'), ('Business', 'Feasible'),
                               ('Business', 'Infeasible'), ('Business', 'Infeasible'), ('Business', 'Infeasible'),
                               ('Media & Video', 'Infeasible'), ('Media & Video', 'Infeasible'), ('Media & Video', 'Infeasible'),
                               ('Media & Video', 'Infeasible'), ('Media & Video', 'Infeasible'), ('Media & Video', 'Infeasible'),
                               ('Shopping', 'Infeasible'), ('Shopping', 'Infeasible'), ('Shopping', 'Infeasible'),
                               ('Shopping', 'Infeasible'), ('Shopping', 'Infeasible'), ('Shopping', 'Infeasible')]


        self.app_list = ['Android Settings'] * 6 + ['Whatsapp'] * 6 + ['Zoom'] * 6 + ['Youtube'] * 6 + ['Temu'] * 6
        self.step_list = ["Tap search bar TextView > search Lock > Tap Lock screen password Textview with \"Password & security\" > Tap Lock screen password Textview > when you see Numeric TextView, the task is Almost Completed and STOP THE TASK.",
                          "Tap Wi-Fi TextView > when you see Wi-Fi Switch, the task is Almost Completed and STOP THE TASK, and you should mention user to open the Wi-Fi switch to enable and select Wi-Fi user wants.",
                          "",
                          "Tap search bar TextView > search Font > Tap Font Textview with \"Display & brightness\" breadcrumb > when you see a seekbar for adjusting the font size, you should mention user to slide the Font size slide bar to adjust font size, and the task is Almost Completed and STOP THE TASK.",
                          "Tap search bar TextView > search brightness > Tap Brightness Textview with \"Display & brightness\" breadcrumb > when you see Light mode with a Radio button, you should mention user to slide the Brightness slide bar to adjust brightness, and the task is Almost Completed and STOP THE TASK.",
                          "Tap Wallpapers & style TextView > Tap Wallpapers > Tap wallpaper thumbnail1 > when you see Apply Button, you should mention user to choose wanted wallpaper and apply, and the task is Almost Completed and STOP THE TASK.",

                          "",
                          "",
                          "Tap the more options ImageView > Tap New group Textview > Wait users to select group members > Tap Next button > when you see Group Name (optional) TextView, the task is Almost Completed and STOP THE TASK.",
                          "Tap the more options ImageView > Tap Settings Textview > Tap Privacy Textview > when you see Last seen and online TextView, the task is Almost Completed and STOP THE TASK.",
                          "Tap the more options ImageView > Tap Settings Textview > Tap Notifications Textview > Scroll down > Tap Ringtone Textview > when you see on this device TextView, you should mention user to choose ringtone wanted, and the task is Almost Completed and STOP THE TASK.",
                          "Tap the more options ImageView > Tap Settings Textview > Tap Privacy Textview > Scroll down (DO NOT Click on 'Last seen and online') > Tap Blocked contacts Textview > Tap Add Textview > when you see Select contact, you should mention user to choose contact wanted, and the task is Almost Completed and STOP THE TASK.",

                          "Tap New Meeting ImageView > when you see Start a meeting button, the task is Almost Completed and STOP THE TASK.",
                          "Tap Join ImageView > when you see Join button, the task is Almost Completed and STOP THE TASK.",
                          "Tap Schedule ImageView > when you see Done Button, you let the user to schedule the meeting,  the task is Almost Completed and STOP THE TASK.",
                          "",
                          "",
                          "",

                          "",
                          "",
                          "",
                          "",
                          "",
                          "",

                          "",
                          "",
                          "",
                          "",
                          "",
                          "",]


        self.__system_prompt_task_match = 'You are an Android mobile assistant, you can only perform the following list of tasks:\n' + str(self.available_task_list) + '\n'\
                                          'Given a user intention, try to select 3 most related tasks that match the user intention.\n' \
                                          '!!!Cases:' \
                                          '1. If successfully match related tasks, respond in the JSON format:{{"State": "Match", "RelatedTasks": ["<task from the list>"], "Reason": "<one-sentence reason>"}}\n' \
                                          '2. If the task is related to the tasks in the list but you need more details to make selection, respond in the JSON format:{{"State": "Related", "Question":"<Question>", "Options":["<sample answers>"]}}\n' \
                                          '3. If the task is totally unrelated to any of the tasks in the list, respond in the JSON format:{{"State": "Unrelated"}}'

        self.__model_manager = model_manager
        self.__base_prompt_task_match = 'User intention: {task}.'

        self.__system_prompt_app_match = 'You are an Android mobile assistant. ' \
                                         'Given an app list, and an app name needed by a phone user, please select the most relevant app package name from the app list.' \
                                         '!!!Note:\n' \
                                         '1. ONLY use this JSON format to provide your answer: {{"AppPackage": "<selected app package from the app list>", "Reason": "<one-sentence reason for selection>"}}' \
                                         '2. If no app package in the app list directly matches the given app name, select the one that seems most relevant as "AppPackage".' \
                                         '3. The result must contains "AppPackage" key. \n' \
                                         '!!!Example:\n' \
                                         '1. {{"AppPackage": "com.android.settings", "Reason": "The app name Android Settings is related to the app package com.android.settings."}}\n' \
                                         '2. {{"AppPackage": "com.android.camera2", "Reason": "The app name Camera is related to the app package com.android.camera2."}}'
        self.__base_prompt_app_match = 'App list: {app_list}\n App name: {app_name}'

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
        if task.clarification_user_msg is not None and len(task.clarification_user_msg) > 0:
            prompt += '\nUser\'s answer for the last question: ' + task.clarification_user_msg + '.\n'
        return prompt

    def match_task_to_list(self, task):
        """
        Try to find 0-3 related tasks in the available task list for the given user task
        Args:
            task (Task): Task object
        Return:
            task_match (dict): {"RelatedTasks": [] or "None", "Reason":}
        """
        try:
            if len(task.conversation_tasklist) == 0:
                task.conversation_tasklist = [{'role': 'system', 'content': self.__system_prompt_task_match}]
            prompt = self.__base_prompt_task_match.format(task=task.task_description)
            prompt += self.wrap_task_info(task)
            task.conversation_tasklist.append({"role": "user", "content": prompt})
            resp = self.__model_manager.send_fm_conversation(task.conversation_tasklist)
            task.conversation_tasklist.append(resp)
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
            prompt = self.__base_prompt_app_match.format(app_name=task.involved_app, app_list=app_list)
            conversation = [{'role': 'system', 'content': self.__system_prompt_app_match},
                            {"role": "user", "content": prompt}]
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
