from ._TaskClarifier import _TaskClarifier
from ._TaskClassifier import _TaskClassifier
from ._TaskDecomposer import _TaskDecomposer


class TaskDeclarator:
    def __init__(self):
        self.task_clarifier_dict = dict()
        self.task_classifier_dict = dict()
        self.task_decomposer_dict = dict()

    def initialize_task_clarifier(self, clarifier_identifier, model_manager):
        """
        Initialize the task clarifier with provided llm Model.
        Args:
            clarifier_identifier: name of the new initialized task clarifier.
            model_manager: ModelManager.
        """
        assert clarifier_identifier not in self.task_clarifier_dict
        self.task_clarifier_dict[clarifier_identifier] = _TaskClarifier(clarifier_identifier, model_manager)

    def initialize_task_classifier(self, classifier_identifier, model_manager):
        """
        Initialize the task classifier with provided llm Model.
        Args:
            classifier_identifier: name of the new initialized task classifier.
            model_manager: ModelManager.
        """
        assert classifier_identifier not in self.task_classifier_dict
        self.task_classifier_dict[classifier_identifier] = _TaskClassifier(classifier_identifier, model_manager)

    def initialize_task_decomposer(self, decomposer_identifier, model_manager):
        """
        Initialize the task decomposer with provided llm Model.
        Args:
            decomposer_identifier: name of the new initialized task decomposer.
            model_manager: ModelManager.
        """
        assert decomposer_identifier not in self.task_decomposer_dict
        self.task_decomposer_dict[decomposer_identifier] = _TaskDecomposer(decomposer_identifier, model_manager)

    def clarify_task(self, clarifier_identifier, org_task, user_message=None, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            clarifier_identifier: identifier of initialized clarifier
            org_task (string): The user's task
            user_message (string): The user's feedback
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None"}
        '''
        self.task_clarifier_dict[clarifier_identifier].clarify_task(task=org_task, user_message=user_message, printlog=printlog)

    def classify_task(self, classifier_identifier, task, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            classifier_identifier: identifier of initialized classifier
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        '''
        self.task_classifier_dict[classifier_identifier].classify_task(task=task, printlog=printlog)

    def decompose_task(self, decomposer_identifier, task, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            decomposer_identifier: identifier of initialized decomposer
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        '''
        self.task_decomposer_dict[decomposer_identifier].decompose_task(task=task, printlog=printlog)
