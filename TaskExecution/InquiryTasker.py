from ModelManagement import ModelManager


class InquiryTasker:
    def __init__(self, system_prompt=None, **kwargs):
        # self.event_manager = event_manager
        # self.event_manager.trigger_event("initialize_llm_model", identifier='inquiry_tasker_model',
        #                            system_prompt=system_prompt, **kwargs)
        #
        self.__model_manager = ModelManager()
        self.__model_manager.initialize_llm_model("inquiry_tasker_model", system_prompt=system_prompt, **kwargs)

    def execute_inquiry_task(self, conversation):
        # Create a new conversation message and send it to the llmModel
        try:
            answer = self.__model_manager.create_llm_conversation("inquiry_tasker_model", conversation)
            history = self.__model_manager.get_llm_conversations("inquiry_tasker_model")
            return {'answer': answer, 'history': history}
        except Exception as e:
            print('error:', e)
            return False

        # answer = self.event_manager.trigger_event("create_llm_conversation", identifier='inquiry_tasker_model',
        #         #                                     conversation=conversation)
        #         # history = self.event_manager.trigger_event("get_llm_conversations", identifier='inquiry_tasker_model')
        #         # return {'answer': answer, 'history': history}

    def reset_inquiry_tasker(self):
        # reset conversation history
        self.__model_manager.reset_llm_conversations("inquiry_tasker_model")
        # self.event_manager.trigger_event("reset_llm_conversations", identifier='inquiry_tasker_model')

