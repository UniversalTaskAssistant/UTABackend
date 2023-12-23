import json


class _TaskClarifier:
    def __init__(self, model_identifier, model_manager):
        self.__model_identifier = model_identifier
        self.__model_manager = model_manager

        self.__base_prompt = 'Assess the user task "{task}" to determine if it is sufficiently clear for execution '\
                             'on a smartphone. Given that seniors often provide vague or incomplete task descriptions, ' \
                             'identify the most crucial piece of missing information. Ask a single, focused question ' \
                             'that is most likely to clarify the task effectively. Return your analysis in JSON format, comprising: '\
                             '1. "Clear": a boolean indicating if the task is clear enough as is, '\
                             '2. "Question": a single question to obtain the most essential missing detail for task clarification. '\
                             'Example response for a clear task: {{"IsClear": "True", "Question": ""}} '\
                             'Example response for an unclear task: {{"Clear": "False", "Question": "What is the ' \
                             'full name of the person you want to contact?"}} or {{"IsClear": "False", "Question": ' \
                             '"Which app would you prefer to use for this communication?"}}'

    def initialize_agent(self):
        """
            Initialize llm model in model manager.
        """
        self.__model_manager.initialize_llm_model(identifier=self.__model_identifier)

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
            return clear
        except Exception as e:
            raise e


if __name__ == '__main__':
    from ModelManagement import ModelManager
    model_mg = ModelManager()
    model_mg.initialize_llm_model(identifier='task_decomposer')

    task = 'Open wechat and send my mom a message'
    task_decompo = _TaskClarifier('task_decomposer', model_manager=model_mg)
    task_decompo.clarify_task(task=task, printlog=True)
