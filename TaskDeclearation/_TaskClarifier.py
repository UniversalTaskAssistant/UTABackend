import json


class _TaskClarifier:
    def __init__(self, model_manager, system_prompt=None, **kwargs):
        self.__model_manager = model_manager
        self.__model_manager.initialize_llm_model("task_clarify", system_prompt=system_prompt, **kwargs)

        self.__base_prompt = 'Do you think this user task "{task}" is clear enough to be completed on the smartphone?' \
                             'If the task is not clear enough, ask further question to gather more info and make the task clearly executable.' \
                             'Return your answer in JSON format to include 1. Clear (bool) and 2. Further question.' \
                             'Example: {"Clear": "True", "Question": "None"} or {"Clear": "False", "Question": "Do you want to search for answers on the browser or through certain app?"}'

    def clarify_task(self, task, user_message=None, printlog=False):
        try:
            if not user_message:
                self.__model_manager.reset_llm_conversations("task_interpreter")
                message = self.__base_prompt.format(task=task)
            else:
                message = user_message
            clear = self.__model_manager.create_llm_conversation("task_interpreter", message, printlog=printlog)['content']
            clear = json.loads(clear)
            print(clear)
        except Exception as e:
            raise e
