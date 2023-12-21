from TaskDeclearation._TaskClarifier import _TaskClarifier
from TaskDeclearation._TaskClassifier import _TaskClassifier
from TaskDeclearation._TaskDecomposer import _TaskDecomposer


class TaskDeclarator:
    def __init__(self, model_manager):
        self.__model_manager = model_manager
        self.task_clarifier_dict = dict()
        self.task_classifier_dict = dict()
        self.task_decomposer_dict = dict()

    def initialize_task_clarifier(self, clarifier_identifier):
        """
        Initialize the task clarifier with provided llm Model.
        Args:
            clarifier_identifier: name of the new initialized task clarifier.
        """
        assert clarifier_identifier not in self.task_clarifier_dict
        self.__model_manager.initialize_llm_model(identifier=clarifier_identifier)
        self.task_clarifier_dict[clarifier_identifier] = _TaskClarifier(model_identifier=clarifier_identifier, model_manager=self.__model_manager)

    def initialize_task_classifier(self, classifier_identifier):
        """
        Initialize the task classifier with provided llm Model.
        Args:
            classifier_identifier: name of the new initialized task classifier.
        """
        assert classifier_identifier not in self.task_classifier_dict
        self.__model_manager.initialize_llm_model(identifier=classifier_identifier)
        self.task_classifier_dict[classifier_identifier] = _TaskClassifier(model_identifier=classifier_identifier, model_manager=self.__model_manager)

    def initialize_task_decomposer(self, decomposer_identifier):
        """
        Initialize the task decomposer with provided llm Model.
        Args:
            decomposer_identifier: name of the new initialized task decomposer.
            model_manager: ModelManager.
        """
        assert decomposer_identifier not in self.task_decomposer_dict
        self.__model_manager.initialize_llm_model(identifier=decomposer_identifier)
        self.task_decomposer_dict[decomposer_identifier] = _TaskDecomposer(model_identifier=decomposer_identifier, model_manager=self.__model_manager)

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
        return self.task_clarifier_dict[clarifier_identifier].clarify_task(task=org_task, user_message=user_message, printlog=printlog)

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
        return self.task_classifier_dict[classifier_identifier].classify_task(task=task, printlog=printlog)

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
        return self.task_decomposer_dict[decomposer_identifier].decompose_task(task=task, printlog=printlog)


if __name__ == '__main__':
    task = 'Open wechat and send my mom a message'

    from ModelManagement import ModelManager
    model_mg = ModelManager()
    model_mg.initialize_llm_model(identifier='task_decomposer')

    task_declarator = TaskDeclarator(model_manager=model_mg)
    task_declarator.initialize_task_clarifier('task_clarifier1')
    task_declarator.clarify_task(clarifier_identifier='task_clarifier1', org_task=task)
    task_declarator.initialize_task_decomposer('task_dec1')
    task_declarator.decompose_task(decomposer_identifier='task_dec1', task=task)
    task_declarator.initialize_task_classifier('task_cls1')
    task_declarator.classify_task(classifier_identifier='task_cls1', task=task)

