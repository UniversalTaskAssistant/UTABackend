from ModelManagement import _AssistantModel


class InquiryTasker:
    def __init__(self):
        self.text_model = _AssistantModel()

    def fetch_answer(self, conversation):
        # Create a new conversation message and send it to the TextModel
        try:
            answer = self.text_model.create_conversation(conversation)
            history = self.text_model.get_conversations()
            return {'answer': answer, 'history': history}
        except Exception as e:
            raise e

    def execute_inquiry_task(self, task):
        return action
