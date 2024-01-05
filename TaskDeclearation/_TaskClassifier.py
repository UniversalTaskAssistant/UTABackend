import json
from DataStructures.config import *


class _TaskClassifier:
    def __init__(self, model_manager):
        self.__model_manager = model_manager
        self.__base_prompt = 'Classify the given user task "{task}" into one of three categories for smartphone usage: ' \
                             '1. General Inquiry: This category includes tasks that are general questions not related ' \
                             'to specific system or app functions. They can typically be answered through internet ' \
                             'searches. Example: "What is the weather today?" ' \
                             '2. System Function: These are tasks that involve system-level functions of the ' \
                             'smartphone. Examples include adjusting settings or using built-in features like alarms. ' \
                             'Example: "Turn up the brightness", "Set an alarm at 2 pm". ' \
                             '3. App-Related Task: Tasks in this category require the use of specific applications to ' \
                             'accomplish the objective. Examples include using ride-sharing apps or streaming ' \
                             'services. Example: "Book a ride to my home using Uber", "Watch a movie on YouTube". ' \
                             'Determine which category the task "{task}" falls into. ' \
                             'Output your classification in JSON format with two elements: 1. "Task Type" indicating ' \
                             'the category, and 2. "Explanation" providing a brief rationale for your classification. '\
                             'Example: {{"Task Type": "General Inquiry", "Explanation": "This task is a general query ' \
                             'that can be resolved through an internet search, without the need for system-level ' \
                             'access or specific apps."}}'

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
            conversation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                            {'role': 'user', 'content': self.__base_prompt.format(task=task.task_description)}]
            resp = self.__model_manager.send_fm_conversation(conversation=conversation, printlog=printlog)
            task.res_classification = json.loads(resp['content'])
            return task.res_classification
        except Exception as e:
            raise e

