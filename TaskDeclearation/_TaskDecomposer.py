import json


class _TaskDecomposer:
    def __init__(self, model_identifier, model_manager):
        self.__model_identifier = model_identifier
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

    def initialize_agent(self):
        """
            Initialize llm model in model manager.
        """
        if self.is_agent_initialized():
            self.delete_agent()
        self.__model_manager.initialize_llm_model(identifier=self.__model_identifier)

    def is_agent_initialized(self):
        """
        Check whether agent is initialized.
        """
        return self.__model_manager.is_llm_model_initialized(identifier=self.__model_identifier)

    def delete_agent(self):
        """
        Remove llm model in model manager.
        """
        self.__model_manager.delete_llm_model(identifier=self.__model_identifier)

    def decompose_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        """
        try:
            self.__model_manager.reset_llm_conversations(self.__model_identifier)
            message = self.__base_prompt.format(task=task)
            decomposition = self.__model_manager.create_llm_conversation(self.__model_identifier, message,
                                                                         printlog=printlog)['content']
            decomposition = json.loads(decomposition)
            print(decomposition)
            return decomposition
        except Exception as e:
            raise e


if __name__ == '__main__':
    from ModelManagement import ModelManager
    model_mg = ModelManager()
    model_mg.initialize_llm_model(identifier='task_decomposer')

    task = 'Open wechat and send my mom a message'
    task_decompo = _TaskDecomposer('task_decomposer', model_manager=model_mg)
    task_decompo.decompose_task(task=task, printlog=True)
