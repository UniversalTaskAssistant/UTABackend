from ModelManagement import _TextModel, _AssistantModel, _VisionModel


class ModelManager:
    def __init__(self):
        self.__vision_model = _VisionModel()
        self.__text_model = _TextModel()
        self.__assistant_model = _AssistantModel()

    # Vision model relevant functions below

    def detect_ocr(self, ctxt):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            ctxt (str): The base64 encoded string of the image.
        Returns:
            The detected text annotations or None if no text is found.
        """
        return self.__vision_model.detect_ocr(ctxt)

    def predict_images(self, imgs):
        """
        Predict the class of the given images.
        Args:
            imgs (list): List of images in numpy array format.
        Returns:
            List of predictions with class names and probabilities.
        """
        return self.__vision_model.predict_images(imgs)

    # Text model relevant functions below

    def initialize_text_model(self, **kwargs):
        """
        Initialize the Text Model with provided configurations.
        Args:
            kwargs: Key-value pairs for model configuration.
        """
        self.__text_model = _TextModel(**kwargs)

    def create_text_conversation(self, conversation, **kwargs):
        """
        Create a conversation using the Text Model.
        Args:
            conversation: Conversation context.
            printlog: Whether to print input conversation
            runtime: Whether to calculate running time
            kwargs: Additional configurations.
        Returns:
            Response from the Text Model.
        """
        return self.__text_model.create_conversation(conversation=conversation, **kwargs)

    def get_text_conversations(self, **kwargs):
        """
        Retrieve the historical conversations from the Text Model.
        Returns:
            List: Historical conversations.
        """
        return self.__text_model.get_conversations(**kwargs)

    def reset_text_conversations(self):
        """
        Clear historical conversations in the Text Model.
        """
        self.__text_model.reset_conversations()

    def count_token_size(self, string):
        """
        Count the token size of a given string to the gpt models.
        Args:
            string (str): String to calculate token size.
        Returns:
            int: Token size.
        """
        return self.__text_model.count_token_size(string)

    # Assistant model relevant functions below

    def initialize_asistant_model(self, **kwargs):
        """
        Initialize the Assistant Model with provided configurations.
        Args:
            kwargs: Key-value pairs for model configuration.
        """
        self.__assistant_model = _AssistantModel(**kwargs)

    def create_assistant_conversation(self, task_id, conversation, **kwargs):
        """
        Create a conversation using the Assistant Model.
        Args:
           task_id: Identifier for the specific task.
           conversation: Conversation context.
           kwargs: Additional configurations.
        Returns:
           Response from the Assistant Model.
        """
        return self.__assistant_model.create_conversation(task_id=task_id, conversation=conversation, **kwargs)

    def get_assistant_conversations(self, task_id):
        """
        Retrieve historical conversations for a specific task from the Assistant Model.
        Args:
            task_id: Identifier for the specific task.
        Returns:
            List: Historical conversations for the task.
        """
        return self.__assistant_model.get_conversations(task_id=task_id)

    def reset_assistant_conversations(self, task_id):
        """
        Clear historical conversations for a specific task in the Assistant Model.
        Args:
            task_id: Identifier for the specific task.
        """
        return self.__assistant_model.reset_conversations(task_id=task_id)