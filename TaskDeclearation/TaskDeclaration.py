from ._TaskClarifier import _TaskClarifier
from ._TaskClassifier import _TaskClassifier
from ._TaskDecomposer import _TaskDecomposer


class TaskDeclarator:
    def __init__(self, model_manager, system_prompt=None, **kwargs):
        self.task_clarifier = _TaskClarifier(model_manager, system_prompt, **kwargs)
        self.task_classifier = _TaskClassifier(model_manager, system_prompt, **kwargs)
        self.task_decomposer = _TaskDecomposer(model_manager, system_prompt, **kwargs)

    def clarify_task(self, org_task, user_message=None, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            org_task (string): The user's task
            user_message (string): The user's feedback
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Clear": "True", "Question": "None"}
        '''
        self.task_clarifier.clarify_task(task=org_task, user_message=user_message, printlog=printlog)

    def classify_task(self, task, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        '''
        self.task_classifier.classify_task(task=task, printlog=printlog)

    def decompose_task(self, task):
        self.task_decomposer.decompose_task(task=task)
