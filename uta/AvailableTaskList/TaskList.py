import json
import re


class TaskList:
    def __init__(self, model_manager):
        self.available_task_list = ['Create a pin for the device', 'Change the pin for the device', 'Create the fingerprint for device', 'Change the fingerprint for device',
                                    'Turn on/off the haptics', 'Increase/decrease the volume', 'Change the ringtone', 'Turn on/off vibration for text',
                                    'Turn on/off vibration for calls', 'Turn on/off lock screen sound', 'Turn on/off the text sound',
                                    'View the notifications', 'Make the text size of device bigger/smaller', 'Change the date', 'Change the time',
                                    'Hide/show name when calling', 'Stop my phone from receiving calls, texts, or emails', 'Add contact information to the lock screen',
                                    'Block/unblock a number', 'Take a photo using Camera',
                                    'Use a photo as background', 'View a photo using Google Photo', 'Delete a photo using Google Photo', 'Edit a photo using Google Photo', 'Share a photo using Google Photo',
                                    'Access Gmail App', 'Open and view files', 'Share a file from Files app', 'Start a new meeting using Zoom', 'Join a meeting using Zoom', 'Schedule a meeting using Zoom',
                                    'Send greetings to my friend Mulong via Whatsapp']
        self.task_info_list = [('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Communications', 'Feasible'), ('Photography', 'Feasible'),
                               ('Photography', 'Feasible'), ('Photography', 'Feasible'), ('Photography', 'Feasible'), ('Photography', 'Feasible'), ('Photography', 'Feasible'),
                               ('Business', 'Feasible'), ('Tools', 'Feasible'), ('Tools', 'Feasible'), ('Business', 'Feasible'), ('Business', 'Feasible'), ('Business', 'Feasible'),
                               ('Social', 'Feasible'),]

        self.app_list = ['Android Settings'] * 18 + ['Dialer'] + ["Phone Camera"] + ["Google Photo"] * 5 + ["Gmail"] + ["Android documents"] * 2 + ["Zoom"] * 3 + ["Whatsapp"]
        self.step_list = ["Open Settings > search Lock > tap Screen lock option > tap Screen lock > tap PIN > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search Lock > tap Screen lock option > tap Screen lock > tap PIN > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search Fingerprint > tap related option > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search Fingerprint > tap related option > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search and select Vibration & haptics > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search volume > click search key in the input keyboard > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search Ringtone > tap Ringtone option > click Ringtone > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search and select Vibration & haptics TextView > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search and select Vibration & haptics TextView > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search vibration > tap Sound & vibration TextView > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > search vibration > tap Sound & vibration TextView > Default notification sound > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > tap Notifications > the task is Almost Completed and STOP THE TASK.",
                          "Open Settings > Search Font size > Tap Font size option > the task is Almost Completed and STOP THE TASK.",
                          "open Settings > search Date > Tap Date & time TextView > Tap Date & time > the task is Almost Completed and STOP THE TASK.",
                          "open Settings > search Time > Tap Time option > the task is Almost Completed and STOP THE TASK.",
                          "open Settings > search Caller ID > select Caller ID related TextView > the task is Almost Completed and STOP THE TASK.",
                          "open Settings > search vibration > select Sound & vibration option > Select Do Not Disturb > the task is Almost Completed and STOP THE TASK.",
                          "open Settings > click searching bar > search Display > Tap display > Tap Lock screen > tap add text on lock screen > the task is Almost Completed and STOP THE TASK.",
                          "Open Phone app > Tap the three dots in the top-right > Tap Settings > tap Blocked numbers > the task is Almost Completed and STOP THE TASK.",
                          "Open the Camera",
                          "Open up your phone's Gallery app > Find the photo you want to use and open it (open the photo but not \"recently highlight\" and others) > Tap the three dots in the top-right > tap use as > the task is Almost Completed and STOP THE TASK.",
                          "Open Google Photos",
                          "Open Google Photos > Click the photo you want to delete (click the photo but not \"recently highlight\" and others) > the task is Almost Completed and STOP THE TASK.",
                          "Select an image in Google Photos (click the photo but not \"recently highlight\" and others) > tap the Edit button > the task is Almost Completed and STOP THE TASK.",
                          "Open Google Photos app  > Sign in to your Google Account > Select a photo, album or video > the task is Almost Completed and STOP THE TASK.",
                          "Open Gmail",
                          "Open Files",
                          "Open Files > click the File > Tap the more options > the task is Almost Completed and STOP THE TASK.",
                          "Open Zoom > sign in/sign up if needed > click New Meeting ImageView > click Start a meeting > the task is Almost Completed and STOP THE TASK.",
                          "Open Zoom > sign in/sign up if needed > click Join ImageView > click Join button > the task is Almost Completed and STOP THE TASK.",
                          "Open Zoom > sign in/sign up if needed > click Schedule ImageView > click Done > the task is Almost Completed and STOP THE TASK.",
                          "Open Whatsapp > sign in/sign up if needed > Tap New chat Imageview > Select Mulong TextView > Select message EditText > input some greetings > click enter key in the keyboard > the task is Almost Completed and STOP THE TASK."]

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
