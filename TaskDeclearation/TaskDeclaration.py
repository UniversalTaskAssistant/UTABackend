from TaskDeclearation._TaskClarifier import _TaskClarifier
from TaskDeclearation._TaskClassifier import _TaskClassifier
from TaskDeclearation._TaskDecomposer import _TaskDecomposer


class TaskDeclarator:
    def __init__(self, model_manager):
        self.__model_manager = model_manager
        self.__clarifier_identifier = 'task clarifier'
        self.__classifier_identifier = 'task classifier'
        self.__decomposer_identifier = 'task decomposer'

        self.__task_clarifier = _TaskClarifier(self.__clarifier_identifier, self.__model_manager)
        self.__task_classifier = _TaskClassifier(self.__classifier_identifier, self.__model_manager)
        self.__task_decomposer = _TaskDecomposer(self.__decomposer_identifier, self.__model_manager)

    def initialize_agents(self):
        """
            Initialize all agents.
        """
        self.__task_clarifier.initialize_agent()
        self.__task_classifier.initialize_agent()
        self.__task_decomposer.initialize_agent()

    def clarify_task(self, org_task, user_message=None, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            org_task (string): The user's task
            user_message (string): The user's feedback
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None"}
        """
        return self.__task_clarifier.clarify_task(task=org_task, user_message=user_message, printlog=printlog)

    def classify_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        """
        return self.__task_classifier.classify_task(task=task, printlog=printlog)

    def decompose_task(self, task, printlog=False):
        """
        Clarify task to be clear to complete
        Args:\
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        """
        return self.__task_decomposer.decompose_task(task=task, printlog=printlog)


if __name__ == '__main__':
    task = 'Open wechat and send my mom a message'

    from ModelManagement import ModelManager
    model_mg = ModelManager()

    task_declarator = TaskDeclarator(model_manager=model_mg)
    task_declarator.initialize_agents()

    task_declarator.clarify_task(org_task=task)
    task_declarator.decompose_task(task=task)
    task_declarator.classify_task(task=task)

