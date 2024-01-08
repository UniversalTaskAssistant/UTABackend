import json
from DataStructures.config import *


class TaskDeclarator:
    def __init__(self, model_manager):
        """
        Initializes a TaskDeclarator instance with prompts.
        Args:
            model_manager: ModelManager use by the class.
        """
        self.__model_manager = model_manager

        self.__base_prompt_clarify = 'Assess the user task "{task}" to determine if it is sufficiently clear for ' \
                                     'execution on a smartphone. Given that seniors often provide vague or ' \
                                     'incomplete task descriptions, identify the most crucial piece of missing ' \
                                     'information. Ask a single, focused question that is most likely to clarify the ' \
                                     'task effectively. Return your analysis in JSON format, comprising: ' \
                                     '1. "Clear": a boolean indicating if the task is clear enough as is, ' \
                                     '2. "Question": a single question to obtain the most essential missing detail ' \
                                     'for task clarification. ' \
                                     'Example response for a clear task: {{"Clear": "True", "Question": ""}} ' \
                                     'Example response for an unclear task: {{"Clear": "False", "Question": "What is ' \
                                     'the full name of the person you want to contact?"}} or {{"Clear": "False", ' \
                                     '"Question": "Which app would you prefer to use for this communication?"}}'

        self.__base_prompt_decompose = 'Analyze the user task "{task}" to determine if it comprises multiple, ' \
                                       'distinct sub-tasks. Complex tasks often consist of several steps that need ' \
                                       'to be executed separately. ' \
                                       'For instance, the task "Login to Facebook and send a message to Sam Wellson" ' \
                                       'involves two separate actions: logging into Facebook and sending a message. ' \
                                       'Identify if the given task requires decomposition and if so, break it down ' \
                                       'into its constituent sub-tasks. Provide your analysis in JSON format, ' \
                                       'including: ' \
                                       '1. "Decompose": a boolean string indicating whether the task should be ' \
                                       'decomposed, ' \
                                       '2. "Sub-tasks": an array of the identified sub-tasks, or "None" if no ' \
                                       'decomposition is needed, ' \
                                       '3. "Explanation": a brief explanation of your decision. ' \
                                       'Example: {{"Decompose": "True", "Sub-tasks": ["Login to Facebook", ' \
                                       '"Send message to Sam Wellson on Facebook"], "Explanation": "The task ' \
                                       'contains two independent actions that need to be completed sequentially."}}'

        self.__base_prompt_classify = 'Classify the given user task "{task}" into one of three categories for ' \
                                      'smartphone usage: ' \
                                      '1. General Inquiry: This category includes tasks that are general questions ' \
                                      'not related to specific system or app functions. They can typically be ' \
                                      'answered through internet searches. Example: "What is the weather today?" ' \
                                      '2. System Function: These are tasks that involve system-level functions of ' \
                                      'the smartphone. Examples include adjusting settings or using built-in ' \
                                      'features like alarms. ' \
                                      'Example: "Turn up the brightness", "Set an alarm at 2 pm". ' \
                                      '3. App-Related Task: Tasks in this category require the use of specific ' \
                                      'applications to accomplish the objective. Examples include using ride-sharing ' \
                                      'apps or streaming services. Example: "Book a ride to my home using Uber", ' \
                                      '"Watch a movie on YouTube". Determine which category the task "{task}" ' \
                                      'falls into. Output your classification in JSON format with two elements: ' \
                                      '1. "Task Type" indicating the category, and 2. "Explanation" providing a ' \
                                      'brief rationale for your classification. ' \
                                      'Example: {{"Task Type": "General Inquiry", "Explanation": "This task is a ' \
                                      'general query that can be resolved through an internet search, without the ' \
                                      'need for system-level access or specific apps."}}'

    def clarify_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (Task): Task object
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None"}
        """
        try:
            # set base prompt for new conv
            if len(task.conversation_clarification) == 1:
                task.conversation_clarification.append({'role': 'user', 'content': self.__base_prompt_clarify.
                                                       format(task=task.task_description)})
            # send conv to fm
            resp = self.__model_manager.send_fm_conversation(conversation=task.conversation_clarification,
                                                             printlog=printlog)
            task.res_clarification = json.loads(resp['content'])
            task.conversation_clarification.append(resp)
            return task.res_clarification
        except Exception as e:
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
            conversation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                            {'role': 'user', 'content':
                                self.__base_prompt_decompose.format(task=task.task_description)}]
            resp = self.__model_manager.send_fm_conversation(conversation=conversation, printlog=printlog)
            task.res_decomposition = json.loads(resp['content'])
            return task.res_decomposition
        except Exception as e:
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
            conversation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                            {'role': 'user', 'content': self.__base_prompt_classify.format(task=task.task_description)}]
            resp = self.__model_manager.send_fm_conversation(conversation=conversation, printlog=printlog)
            task.res_classification = json.loads(resp['content'])
            return task.res_classification
        except Exception as e:
            raise e


if __name__ == '__main__':
    from ModelManagement import ModelManager
    model_mg = ModelManager()
    from DataStructures.Task import Task
    tsk = Task(task_id="1", task_description='Open wechat and send my mom a message')

    task_declarer = TaskDeclarator(model_manager=model_mg)
    print(task_declarer.clarify_task(task=tsk))
    print(task_declarer.decompose_task(task=tsk))
    print(task_declarer.classify_task(task=tsk))
