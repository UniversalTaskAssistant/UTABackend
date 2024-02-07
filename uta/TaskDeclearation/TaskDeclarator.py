import json
import re

from uta.config import *


class TaskDeclarator:
    def __init__(self, model_manager):
        """
        Initializes a TaskDeclarator instance with prompts.
        Args:
            model_manager: ModelManager use by the class.
        """
        self.__model_manager = model_manager

        self.__user_input_justify = 'As a mobile assistant, do you think the answer {user_msg} is related to the previous conversation? ' \
                                    'If it is not related, please point out the reason.' \
                                    '!!!Respond to the following points:\n' \
                                    '1. "Related": a boolean indicating if the answer is related.\n' \
                                    '2. "Explanation": a brief explanation of your decision. \n' \
                                    '3. "Question" (only include this attribute if \"Related\" is False): repeat the previous asked question again to user.\n' \
                                    '4. "Options"  (optional, only include this attribute if \"Related\" is False): repeat the previous asked options again to user.\n' \
                                    '!!!Note:\n' \
                                    'ONLY use this JSON format to provide your answer: {{"Related": "<True or False>", "Explanation": "<Explanation>", "Question": "<Question>", "Options": ["<Options>"]}}\n' \
                                    '!!!Examples:\n' \
                                    '1. {{"Related": "False", "Explanation": "The answer \"hello\" is greetings that is unrelated to previous proposed questions.", ' \
                                    '"Question": "Which app do you want to send your message?", "Options": ["Message", "WhatsApp", "Meta", "Phone Call"]}}.\n ' \
                                    '2. {{"Related": "True", "Explanation": "The answer answers previous proposed questions."}}.\n'

        self.__succeed_prompt_clarify = '!!!Respond to the following points:\n' \
                                        '1. "Clear": a boolean indicating if the task is clear enough.\n' \
                                        '2. "Question": a single question to ask the user to further clarify the task with missing essential details.\n' \
                                        '3. "Options" (optional): a list of up to 4 example options from {app_list} that may answers the question to give more missing details.' \
                                        '4. "InvolvedApp" (only include this attribute if "Clear" is true): the app used for task execution.' \
                                        '5. "InvolvedAppPackage" (only include this attribute if there is "InvolvedApp"): the full app package name corresponding to "InvolvedApp".' \
                                        '!!!Note:\n' \
                                        'ONLY use this JSON format to provide your answer: {{"Clear": "<True or False>", "Question": "<Question>", "Options": ["<Options>"]}}.\n' \
                                        '!!!Examples:\n' \
                                        '1. {{"Clear": "False", "Question": "Which app do you want to send your message?", "Options": ["Message", "WhatsApp", "Meta", "Phone Call"]}}.\n ' \
                                        '2. {{"Clear": "False", "Question": "What is your location?", "Options": []}}.\n' \
                                        '3. {{"Clear": "True", "InvolvedApp": "Message", "InvolvedAppPackage": "com.android.mms.service"}}\n'

        self.__base_prompt_clarify = 'Assess the user task "{task}" to determine if it is sufficiently clear for execution on a smartphone. ' \
                                     'If the task involves using a mobile app, then it can only be clear when it is also clear which specific app should be used. ' \
                                     'If it is not clear enough, provide a focused question with up to 4 selectable options to clarify the task.' \
                                     'If there are not enough selections, you can select less than 4 but larger than 1 selections. ' \
                                     'If the task involves using a mobile app, the selectable app options can only be from {app_list}, and you should show the understandable official app name rather than Android package name.\n' \
                                     '!!!Respond to the following points:\n' \
                                     '1. "Clear": a boolean indicating if the task is clear enough.\n' \
                                     '2. "Question": a single question to ask the user to further clarify the task with missing essential details.\n' \
                                     '3. "Options" (optional): a list of up to 4 example options from {app_list} that may answers the question to give more missing details.' \
                                     '4. "InvolvedApp" (only include this attribute if "Clear" is true): the app used for task execution.' \
                                     '5. "InvolvedAppPackage" (only include this attribute if there is "InvolvedApp"): the full app package name corresponding to "InvolvedApp".' \
                                     '!!!Note:\n' \
                                     'ONLY use this JSON format to provide your answer: {{"Clear": "<True or False>", "Question": "<Question>", "Options": ["<Options>"]}}.\n' \
                                     '!!!Examples:\n' \
                                     '1. {{"Clear": "False", "Question": "Which app do you want to send your message?", "Options": ["Message", "WhatsApp", "Meta", "Phone Call"]}}.\n ' \
                                     '2. {{"Clear": "False", "Question": "What is your location?", "Options": []}}.\n' \
                                     '3. {{"Clear": "True", "InvolvedApp": "Message", "InvolvedAppPackage": "com.android.mms.service"}}\n'

        self.__base_prompt_decompose = 'Analyze the user task "{task}" to determine if it comprises multiple, distinct sub-tasks.' \
                                       'Complex tasks often consist of several steps that need to be executed separately. ' \
                                       'For instance, the task "Login to Facebook and send a message to Sam" involves two separate actions: logging into Facebook and sending a message.\n' \
                                       '!!!Respond to the following points:\n' \
                                       '1. "Decompose": a boolean string indicating whether the task should be decomposed.\n ' \
                                       '2. "Sub-tasks": an array of the identified sub-tasks, or "None" if no decomposition is needed.\n ' \
                                       '3. "Explanation": a brief explanation of your decision. \n' \
                                       '!!!Note:\n' \
                                       'ONLY use this JSON format to provide your answer: {{"Decompose":"<True or False>", "Sub-tasks": ["<subtask>"], "Explanation": "<Explanation>"}}\n' \
                                       '!!!Example:\n' \
                                       '1. {{"Decompose": "True", "Sub-tasks": ["Login to Facebook", "Send message to Sam Wellson on Facebook"], ' \
                                       '"Explanation": "The task contains two independent actions that need to be completed sequentially."}}\n' \
                                       '2. {{"Decompose"： "False", "Sub-tasks": [], ' \
                                       '"Explanation": "This task is simple enough to be executed on the smartphone."}}\n'

        self.__base_prompt_classify = 'Classify the given user task "{task}" into one of three categories for smartphone usage:\n ' \
                                      '!!!Categories:' \
                                      '1. General Inquiry: This category includes tasks that are general questions not related to specific system or app functions. ' \
                                      'They can typically be answered through internet searches. Example: "What is the weather today?" \n' \
                                      '2. System Function: These are tasks that involve system-level functions of the smartphone.' \
                                      'Examples include adjusting settings or using built-in features. ' \
                                      'Example: "Turn up the brightness", "Enlarge the font size". \n' \
                                      '3. App-Related Task: Requiring the use of specific applications to accomplish the objective. ' \
                                      'Example: "Book a ride to my home using Uber", "Watch a movie on YouTube". \n' \
                                      '!!!Determine which category the task "{task}" falls into. Output your classification in JSON format with two elements: ' \
                                      '1. "Task Type" indicating the category;\n' \
                                      '2. "Explanation" providing a brief rationale for your classification. \n' \
                                      '!!!Examples:' \
                                      '1. {{"Task Type": "General Inquiry", "Explanation": "This task is a general query that can be resolved through an internet search,' \
                                      ' without the need for system-level access or specific apps."}}\n' \
                                      '2. {{"Task Type: "App-Related", "Explanation": "This task needs to be done through Uber app."}}\n'

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
        if task.involved_app and task.involved_app_package:
            prompt += f'The user task {task.task_description} will be executed via app ' \
                f'{task.involved_app} corresponding to app package {task.involved_app_package}.\n'
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

    def clarify_task(self, task, app_list, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): Task object
            app_list: list of user installed apps
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None", "Options":[]}
        """
        try:
            # set base prompt for new conv
            if len(task.conversation_clarification) == 0:
                task.conversation_clarification = [{'role': 'system', 'content': SYSTEM_PROMPT},
                                                   {"role": "user", "content": self.__base_prompt_clarify.format(task=task.task_description,
                                                                                                                 app_list=app_list)}]
            elif task.clarification_user_msg:
                task.conversation_clarification.append({'role': 'user', 'content': f"Response to the Question: {task.clarification_user_msg}.\n"
                                                                                   + self.__succeed_prompt_clarify})
                task.user_clarify.append(task.clarification_user_msg)
            else:
                raise ValueError("not initial clarification but not clarification_user_msg is stored.")
            # send conv to fm
            resp = self.__model_manager.send_fm_conversation(conversation=task.conversation_clarification, printlog=printlog)
            task.conversation_clarification.append(resp)
            task.res_clarification = self.transfer_to_dict(resp)
            task.res_clarification['Proc'] = 'Clarify'
            print(task.res_clarification)
            return task.res_clarification
        except Exception as e:
            print(resp)
            raise e

    def justify_user_message(self, task, printlog=False):
        """
        justify whether user message is related to the clarification question
        Args:
            task (Task): Task object
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None", "Options":[]}
        """
        try:
            if task.clarification_user_msg:
                task.conversation_clarification.append(
                    {'role': 'user', 'content': f"Response to the Question: {self.__user_input_justify.format(user_msg=task.clarification_user_msg)}.\n"})
                # send conv to fm
                resp = self.__model_manager.send_fm_conversation(conversation=task.conversation_clarification, printlog=printlog)
                task.conversation_clarification.append(resp)
                task.res_clarification = self.transfer_to_dict(resp)
                task.res_clarification['Proc'] = 'Clarify'
                print(task.res_clarification)
                return task.res_clarification
            else:
                raise ValueError("The clarification_user_msg is None in justification.")
        except Exception as e:
            print(resp)
            raise e

    def decompose_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): Task object
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        """
        try:
            prompt = self.wrap_task_info(task)
            prompt += self.__base_prompt_decompose.format(task=task.task_description)
            conversation = [{"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}]
            resp = self.__model_manager.send_fm_conversation(conversation=conversation, printlog=printlog)
            task.res_decomposition = self.transfer_to_dict(resp)
            task.subtasks = task.res_decomposition['Sub-tasks']
            task.res_decomposition['Proc'] = 'Decompose'
            print(task.res_decomposition)
            return task.res_decomposition
        except Exception as e:
            print(resp)
            raise e

    def classify_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): Task object
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        """
        try:
            prompt = self.wrap_task_info(task)
            prompt += self.__base_prompt_classify.format(task=task.task_description)
            conversation = [{"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}]
            resp = self.__model_manager.send_fm_conversation(conversation=conversation, printlog=printlog)
            task.res_classification = self.transfer_to_dict(resp)
            task.res_classification['Proc'] = 'Classify'
            task.task_type = task.res_classification["Task Type"]
            print(task.res_classification)
            return task.res_classification
        except Exception as e:
            print(resp)
            raise e


if __name__ == '__main__':
    from uta.ModelManagement import ModelManager
    model_mg = ModelManager()
    from uta.DataStructures.Task import Task
    tsk = Task(task_id="1", task_description='Open wechat and send my mom a message')

    task_declarer = TaskDeclarator(model_manager=model_mg)
    print(task_declarer.clarify_task(task=tsk))
    print(task_declarer.decompose_task(task=tsk))
    print(task_declarer.classify_task(task=tsk))
