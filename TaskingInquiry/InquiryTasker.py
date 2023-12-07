from ModelManagement import ModelManager


class InquiryTasker:
    def __init__(self, **kwargs):
        self.__model_manager = ModelManager()
        self.__model_manager.initialize_text_model(**kwargs)

    def execute_inquiry_task(self, conversation):
        # Create a new conversation message and send it to the TextModel
        try:
            answer = self.__model_manager.create_text_conversation(conversation)
            history = self.__model_manager.get_text_conversations()
            return {'answer': answer, 'history': history}
        except Exception as e:
            raise e
