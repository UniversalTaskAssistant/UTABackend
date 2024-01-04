

class InquiryTasker:
    def __init__(self, model_manager):
        self.__model_identifier = 'inquiry_tasker'
        self.__model_manager = model_manager

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

    def execute_inquiry_task(self, conversation):
        # Create a new conversation message and send it to the llmModel
        try:
            answer = self.__model_manager.create_llm_conversation(self.__model_identifier, conversation)['content']
            history = self.__model_manager.get_llm_conversations(self.__model_identifier)
            return {'answer': answer, 'history': history}
        except Exception as e:
            print('error:', e)
            return False

    def reset_inquiry_tasker(self):
        # reset conversation history
        self.__model_manager.reset_llm_conversations(self.__model_identifier)
