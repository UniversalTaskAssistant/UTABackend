import json
from uta.config import *


class TaskList:
    def __init__(self, model_manager):
        self.available_task_list = ['Set up a pin for the device',
                                    'Change the pin for the device']

        self.__model_manager = model_manager
        self.__base_prompt_task_match = 'Given the task {task}, select 0 to 3 most related tasks from the available task list.\n' \
                                        '!!!Available task list:\n' + str(self.available_task_list) + \
                                        '!!!Note:\n' \
                                        '1. ONLY use this JSON format to provide your answer: {{"RelatedTasks": ["<task from the list>"], "Reason": "<one-sentence reason>"}}' \
                                        '2. If no task in the list is related to the given task, answer "None" for the "RelatedTasks".\n' \
                                        '!!!Example:\n' \
                                        '1. {{"RelatedTasks": ["Set up a pin for the device"], "Reason": "The given task is related to device pin."}}\n' \
                                        '2. {{"RelatedTasks": "None", "Reason": "No related task in the list to the given task."}}'

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
            task_match = json.loads(resp['content'])
            print(task_match)
            return task_match
        except Exception as e:
            print(resp)
            raise e


