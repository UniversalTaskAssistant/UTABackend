import json


class _TaskClassifier:
    def __init__(self, model_identifier, model_manager):
        self.__model_identifier = model_identifier
        self.__model_manager = model_manager

        self.__base_prompt = 'We categorize the user tasks on the smartphone into three types:' \
                             '1. General Inquiry: Some general questions that have nothing to do with the system or app functions and can be answered through searching on the Internet, such as "What is the weather of today?"' \
                             '2. System Function: Tasks related to system-level functions, such as "Turn up the brightness", "Set an alarm at 2pm".' \
                             '3. App Related Task: Tasks that need to be done through certain apps, such as "Take an uber to my home", "Watch movie on Youtube".' \
                             'What is the type of the given task "{task}"?' \
                             'Output you answer in JSON format with two factors: 1. Task Type; 2. Short explanation.' \
                             'Example: {{"Task Type": "1. General Inquiry", "Explanation": "The task is an inquiry that has nothing to do with the system or app functions and can be answered through searching on the Internet"}}'

    def initialize_agent(self):
        """
            Initialize llm model in model manager.
        """
        self.__model_manager.initialize_llm_model(identifier=self.__model_identifier)

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
