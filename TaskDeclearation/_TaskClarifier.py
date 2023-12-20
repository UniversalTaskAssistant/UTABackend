import json


class _TaskClarifier:
    def __init__(self, model_identifier, model_manager):
        self.__model_identifier = model_identifier
        self.__model_manager = model_manager

        self.__base_prompt = 'Do you think this user task "{task}" is clear enough to be completed on the smartphone?' \
                             'If the task is not clear enough, ask further question to gather more info and make the task clearly executable.' \
                             'Return your answer in JSON format to include 1. Clear (bool) and 2. Further question.' \
                             'Example: {{"Clear": "True", "Question": "None"}} or {{"Clear": "False", "Question": "Do you want to search for answers on the browser or through certain app?"}}'

    def clarify_task(self, task, user_message=None, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            user_message (string): The user's feedback
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None"}
        '''
        try:
            if not user_message:
                self.__model_manager.reset_llm_conversations(self.__model_identifier)
                message = self.__base_prompt.format(task=task)
            else:
                message = user_message
            clear = self.__model_manager.create_llm_conversation(self.__model_identifier, message, printlog=printlog)['content']
            clear = json.loads(clear)
            print(clear)
        except Exception as e:
            raise e


if __name__ == '__main__':
    from ModelManagement import ModelManager
    model_mg = ModelManager()
    model_mg.initialize_llm_model(identifier='task_decomposer')

    task = 'Open wechat and send my mom a message'
    task_decompo = _TaskClarifier('task_decomposer', model_manager=model_mg)
    task_decompo.clarify_task(task=task, printlog=True)
