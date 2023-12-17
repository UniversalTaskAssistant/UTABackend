import json


class _TaskClassifier:
    def __init__(self, model_manager, system_prompt=None, **kwargs):
        self.__model_manager = model_manager
        self.__model_manager.initialize_llm_model("task_classifier", system_prompt=system_prompt, **kwargs)

        self.__base_prompt = 'We categorize the user tasks on the smartphone into three types:' \
                             '1. General Inquiry: Some general questions that have nothing to do with the system or app functions and can be answered through searching on the Internet, such as "What is the weather of today?"' \
                             '2. System Function: Tasks related to system-level functions, such as "Turn up the brightness", "Set an alarm at 2pm".' \
                             '3. App Related Task: Tasks that need to be done through certain apps, such as "Take an uber to my home", "Watch movie on Youtube".' \
                             'What is the type of the given task "{task}"?' \
                             'Output you answer in JSON format with two factors: 1. Task Type; 2. Short explanation.' \
                             'Example: {"Task Type": "1. General Inquiry", "Explanation": "The task is an inquiry that has nothing to do with the system or app functions and can be answered through searching on the Internet"}'

    def classify_task(self, task, printlog=False):
        try:
            self.__model_manager.reset_llm_conversations("task_classifier")
            message = self.__base_prompt.format(task=task)
            cls = self.__model_manager.create_llm_conversation("task_classifier", message, printlog=printlog)['content']
            cls = json.loads(cls)
            print(cls)
        except Exception as e:
            raise e
