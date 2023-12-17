from ModelManagement import ModelManager


class SystemTasker:
    def __init__(self, system_prompt=None, **kwargs):
        self.__model_manager = ModelManager()
        self.__model_manager.initialize_llm_model(system_prompt=system_prompt, **kwargs)

    def execute_system_task(self, task):
        return action

