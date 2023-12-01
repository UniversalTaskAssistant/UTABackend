import openai
import tiktoken


class OpenAI:
    def __init__(self, **kwargs):
        # Initialize the Model with default settings, and override with any provided kwargs
        openai.api_key = open('ModelManagement/openaikey.txt', 'r').readline()
        self.default_config = {
            'model': 'gpt-4',
            'seed': 42,
            'temperature': 0.0
        }
        self.default_config.update(kwargs)
        self.conversations = []

    def create_conversation(self, **kwargs):
        # Create a conversation with GPT-4 based on the input and configuration, need to be implemented by the inheritor
        pass

    @staticmethod
    def count_token_size(string):
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(enc.encode(string))

    def reset_conversations(self):
        self.conversations = []

    def get_conversations(self):
        return self.conversations
