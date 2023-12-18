import json


class _TaskDecomposer:
    def __init__(self, model_manager, system_prompt=None, **kwargs):
        self.__model_manager = model_manager
        self.__model_manager.initialize_llm_model("task_decomposer", system_prompt=system_prompt, **kwargs)

        self.__base_prompt = 'Some user tasks may actually contain multiple sub-tasks and cannot be completed straightforward.' \
                             'For example, "Login Facebook and send message to my dad." is actually composed of two independent tasks and should be decomposed to "Login to Facebook" and "Send message to my dad on Facebook".' \
                             'Does the given task "{task}" need to be decomposed into multiple independent tasks?' \
                             'Output you answer in JSON format with two factors: 1. Need to be decomposed? (bool); 2. List of sub-tasks if decomposed, otherwise None; 3. Short explanation.' \
                             'Example: {"Decompose": "True", "Sub-tasks":["Login to Facebook", "Send message to my dad on Facebook"], "Explanation": "This given task contains two independent subtasks that should be completed one by one."}'

    def decompose_task(self, task, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        '''
        try:
            self.__model_manager.reset_llm_conversations("task_decomposer")
            message = self.__base_prompt.format(task=task)
            decomposition = self.__model_manager.create_llm_conversation("task_decomposer", message, printlog=printlog)['content']
            decomposition = json.loads(decomposition)
            print(decomposition)
        except Exception as e:
            raise e
