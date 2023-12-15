# from ModelManagement import ModelManager


class InquiryTasker:
    def __init__(self, event_manager, system_prompt=None, **kwargs):
        self.event_manager = event_manager
        self.event_manager.trigger_event("initialize_text_model", identifier='inquiry_tasker_model',
                                   system_prompt=system_prompt, **kwargs)

        # self.__model_manager = ModelManager()
        # self.__model_manager.initialize_text_model(system_prompt=system_prompt, **kwargs)

    def execute_inquiry_task(self, conversation):
        # Create a new conversation message and send it to the TextModel
        # try:
        #     answer = self.__model_manager.create_text_conversation(conversation)
        #     history = self.__model_manager.get_text_conversations()
        #     return {'answer': answer, 'history': history}
        # except Exception as e:
        #     raise e

        answer = self.event_manager.trigger_event("create_text_conversation", identifier='inquiry_tasker_model',
                                            conversation=conversation)
        history = self.event_manager.trigger_event("get_text_conversations", identifier='inquiry_tasker_model')
        return {'answer': answer, 'history': history}

    def reset_inquiry_tasker(self):
        # reset conversation history
        # self.__model_manager.reset_text_conversations()
        self.event_manager.trigger_event("reset_text_conversations", identifier='inquiry_tasker_model')

