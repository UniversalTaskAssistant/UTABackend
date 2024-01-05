import json
from DataStructures.config import *


class _TaskClarifier:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        self.__base_prompt = 'Assess the user task "{task}" to determine if it is sufficiently clear for execution '\
                             'on a smartphone. Given that seniors often provide vague or incomplete task descriptions, ' \
                             'identify the most crucial piece of missing information. Ask a single, focused question ' \
                             'that is most likely to clarify the task effectively. Return your analysis in JSON format, comprising: '\
                             '1. "Clear": a boolean indicating if the task is clear enough as is, '\
                             '2. "Question": a single question to obtain the most essential missing detail for task clarification. '\
                             'Example response for a clear task: {{"Clear": "True", "Question": ""}} '\
                             'Example response for an unclear task: {{"Clear": "False", "Question": "What is the ' \
                             'full name of the person you want to contact?"}} or {{"Clear": "False", "Question": ' \
                             '"Which app would you prefer to use for this communication?"}}'

    def clarify_task(self, task, user_message=None, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            user_message (string): The user's feedback
            task (Task): Task object
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None"}
        """
        try:
            # set base prompt for new conv
            if len(task.conversation_clarification) == 1:
                task.conversation_clarification.append({'role': 'user', 'content': self.__base_prompt.format(task=task.task_description)})
            # add user feedback
            if user_message:
                task.conversation_clarification.append({'role': 'user', 'content': user_message})
            # send conv to fm
            resp = self.__model_manager.send_fm_conversation(conversation=task.conversation_clarification, printlog=printlog)
            task.res_clarification = json.loads(resp['content'])
            task.conversation_clarification.append(resp)
            return task.res_clarification
        except Exception as e:
            raise e


if __name__ == '__main__':
    from ModelManagement import ModelManager
    model_mg = ModelManager()
    task_clr = _TaskClarifier(model_mg)

    from DataStructures.Task import Task
    tsk = Task(task_id=1, task_description='Open wechat and send my mom a message')
    task_clr.clarify_task(task=tsk, printlog=True)
