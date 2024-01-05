import json
from DataStructures.config import *


class _TaskDecomposer:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        self.__base_prompt = 'Analyze the user task "{task}" to determine if it comprises multiple, distinct sub-tasks. ' \
                             'Complex tasks often consist of several steps that need to be executed separately. ' \
                             'For instance, the task "Login to Facebook and send a message to Sam Wellson" involves ' \
                             'two separate actions: logging into Facebook and sending a message. ' \
                             'Identify if the given task requires decomposition and if so, break it down into its ' \
                             'constituent sub-tasks. Provide your analysis in JSON format, including: ' \
                             '1. "Decompose": a boolean string indicating whether the task should be decomposed, ' \
                             '2. "Sub-tasks": an array of the identified sub-tasks, or "None" if no decomposition is needed, ' \
                             '3. "Explanation": a brief explanation of your decision. ' \
                             'Example: {{"Decompose": "True", "Sub-tasks": ["Login to Facebook", ' \
                             '"Send message to Sam Wellson on Facebook"], "Explanation": "The task contains ' \
                             'two independent actions that need to be completed sequentially."}}'

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
            conversation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                            {'role': 'user', 'content': self.__base_prompt.format(task=task.task_description)}]
            resp = self.__model_manager.send_fm_conversation(conversation=conversation, printlog=printlog)
            task.res_decomposition = json.loads(resp['content'])
            return task.res_decomposition
        except Exception as e:
            raise e


