from .LLMModel import _LLMModel, _AssistantModel
from .VisionModel import _VisionModel


class ModelManager:
    def __init__(self):
        self.__vision_model = None
        self.__llm_model_dict = dict()
        self.__assistant_model_dict = dict()

    # Vision model relevant functions below

    def initialize_vision_model(self):
        """
        Initialize vision model.
        """
        self.__vision_model = _VisionModel()

    def detect_text_ocr(self, img_path):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            img_path (str): Image file path.
        Returns:
            The detected text annotations or None if no text is found.
        """
        assert self.__vision_model is not None
        return self.__vision_model.detect_text_ocr(img_path)

    def classify_icons(self, imgs):
        """
        Predict the class of the given icons images.
        Args:
            imgs (list): List of images in numpy array format.
        Returns:
            List of predictions with class names and probabilities.
        """
        assert self.__vision_model is not None
        return self.__vision_model.classify_icons(imgs)

    # LLM model relevant functions below

    def initialize_llm_model(self, identifier, **kwargs):
        """
        Initialize the llm Model with provided configurations.
        Args:
            identifier: name of the new initialized llm model.
            kwargs: Key-value pairs for model configuration.
        """
        assert identifier not in self.__llm_model_dict
        self.__llm_model_dict[identifier] = _LLMModel(**kwargs)

    def create_llm_conversation(self, identifier, conversation, **kwargs):
        """
        Create a conversation using the llm Model.
        Args:
            identifier: name of the llm model.
            conversation: Conversation context.
            printlog: Whether to print input conversation
            runtime: Whether to calculate running time
            kwargs: Additional configurations.
        Returns:
            Response from the Text Model.
        """
        assert identifier in self.__llm_model_dict
        return self.__llm_model_dict[identifier].create_conversation(conversation=conversation, **kwargs)

    def get_llm_conversations(self, identifier, **kwargs):
        """
        Retrieve the historical conversations from the llm Model.
        Args:
            identifier: name of the llm model.
        Returns:
            List: Historical conversations.
        """
        assert identifier in self.__llm_model_dict
        return self.__llm_model_dict[identifier].get_conversations(**kwargs)

    def reset_llm_conversations(self, identifier):
        """
        Clear historical conversations in the llm Model.
        Args:
            identifier: name of the llm model.
        """
        assert identifier in self.__llm_model_dict
        self.__llm_model_dict[identifier].reset_conversations()

    def set_llm_conversations(self, identifier, messages):
        """
        Set historical conversations in the llm Model.
        Args:
            identifier: name of the llm model.
            messages: new historical conversations.
        """
        assert identifier in self.__llm_model_dict
        self.__llm_model_dict[identifier].set_conversations(messages)

    @staticmethod
    def count_token_size(string):
        """
        Count the token size of a given string to the gpt models.
        Args:
            string (str): String to calculate token size.
        Returns:
            int: Token size.
        """
        return _LLMModel().count_token_size(string)

    # Assistant model relevant functions below

    def initialize_assistant_model(self, identifier, **kwargs):
        """
        Initialize the Assistant Model with provided configurations.
        Args:
            identifier: name of the new initialized assistant model.
            kwargs: Key-value pairs for model configuration.
        """
        assert identifier not in self.__assistant_model_dict
        self.__assistant_model_dict[identifier] = _AssistantModel(**kwargs)

    def create_assistant_conversation(self, identifier, task_id, conversation, **kwargs):
        """
        Create a conversation using the Assistant Model.
        Args:
           identifier: name of the assistant model.
           task_id: Identifier for the specific task.
           conversation: Conversation context.
           kwargs: Additional configurations.
        Returns:
           Response from the Assistant Model.
        """
        assert identifier in self.__assistant_model_dict
        return self.__assistant_model_dict[identifier].create_conversation(task_id=task_id, conversation=conversation,
                                                                           **kwargs)

    def get_assistant_conversations(self, identifier, task_id):
        """
        Retrieve historical conversations for a specific task from the Assistant Model.
        Args:
            identifier: name of the assistant model.
            task_id: Identifier for the specific task.
        Returns:
            List: Historical conversations for the task.
        """
        assert identifier in self.__assistant_model_dict
        return self.__assistant_model_dict[identifier].get_conversations(task_id=task_id)

    def reset_assistant_conversations(self, identifier, task_id):
        """
        Clear historical conversations for a specific task in the Assistant Model.
        Args:
            identifier: name of the assistant model.
            task_id: Identifier for the specific task.
        """
        assert identifier in self.__assistant_model_dict
        return self.__assistant_model_dict[identifier].reset_conversations(task_id=task_id)
