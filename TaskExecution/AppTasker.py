from .AutoTasker import _TaskUIActionChecker, _TaskUIRelationChecker


class AppTasker:
    def __init__(self, **kwargs):
        """
        Initializes the AppTasker with required paths and settings.
        Args:
            **kwargs: Keyword arguments containing paths and settings for task automation.
                      Required keys are 'ui_relation_checker', 'ui_action_checker', and 'model_manager'.
        """
        assert 'ui_relation_checker' in kwargs and 'ui_action_checker' in kwargs and 'model_manager' in kwargs
        self.relation_checker = _TaskUIRelationChecker(kwargs['ui_relation_checker'], kwargs['model_manager'])
        self.action_checker = _TaskUIActionChecker(kwargs['ui_action_checker'], kwargs['model_manager'])

    def check_task_ui_relation(self, ui_data, task, except_elements=None, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            ui_data (UIData): ui object to be analyzed.
            task (str): The task for which the relation is to be checked.
            except_elements (list, optional): List of elements to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Relation between the ui and the task.
        """
        return self.relation_checker.check_relation(ui=ui_data, task=task, except_elements=except_elements, printlog=printlog)

    def check_ui_action(self, ui_data, task, except_elements=None, printlog=False):
        """
        Determines the appropriate action and target element in the UI for a given task.
        Args:
            ui_data (UIData): ui object to be analyzed.
            task (str): The task to be completed using the UI.
            except_elements (list, optional): Elements to be excluded from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action with the determined action and target element.
        """
        return self.action_checker.check_action(ui=ui_data, task=task, except_elements=except_elements, printlog=printlog)

    def analyze_app_task(self, ui_data, task, except_elements=None, printlog=False):
        '''
        Identify the relation and action for the app-related task
        Args:
            ui_data (UIData): ui object to be analyzed.
            task (str): The task to be completed using the UI.
            except_elements (list, optional): Elements to be excluded from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Status (int, 0, 1, 2): 0 - unrelated; 1 - complete; 2 - related
            Action (Action): If related, UI action on the current UI
        '''
        # 1. check the relation between the UI and the task
        relation = self.check_task_ui_relation(ui_data=ui_data, task=task, except_elements=except_elements, printlog=printlog)
        # If the task is unrelated to this UI, return unrelated status to try to launch related app
        if relation['Relation'] == 'Unrelated':
            return 0
        # If the task is already completed, return complete status
        elif relation['Relation'] == 'Completed':
            return 1
        # If the task is related to this UI, check UI action
        else:
            # 2. check the ui action
            action = self.check_ui_action(ui_data=ui_data, task=task, except_elements=except_elements, printlog=printlog)
            return 2, action
