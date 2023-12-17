from ._TaskClarifier import _TaskClarifier
from ._TaskClassifier import _TaskClassifier
from ._TaskDecomposer import _TaskDecomposer


class TaskDeclarator:
    def __init__(self, model_manager, system_prompt=None, **kwargs):
        self.task_clarifier = _TaskClarifier(model_manager, system_prompt, **kwargs)
        self.task_classifier = _TaskClassifier(model_manager, system_prompt, **kwargs)
        self.task_decomposer = _TaskDecomposer(model_manager, system_prompt, **kwargs)

    def clarify_task(self, org_task):
        self.task_clarifier.clarify_task(task=org_task)

    def classify_task(self, task):
        self.task_classifier.classify_task(task=task)

    def decompose_task(self, task):
        self.task_decomposer.decompose_task(task=task)
