import json


class _TaskClassifier:
    def __init__(self, model_identifier, model_manager):
        self.__model_identifier = model_identifier
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

    def classify_task(self, task, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        '''
        try:
            self.__model_manager.reset_llm_conversations(self.__model_identifier)
            message = self.__base_prompt.format(task=task)
            cls = self.__model_manager.create_llm_conversation(self.__model_identifier, message, printlog=printlog)['content']
            cls = json.loads(cls)
            print(cls)
            return cls
        except Exception as e:
            raise e


if __name__ == '__main__':
    from ModelManagement import ModelManager
    model_mg = ModelManager()
    model_mg.initialize_llm_model(identifier='task_decomposer')

    task = 'Open wechat and send my mom a message'
    task_decompo = _TaskClassifier('task_decomposer', model_manager=model_mg)
    task_decompo.classify_task(task=task, printlog=True)
