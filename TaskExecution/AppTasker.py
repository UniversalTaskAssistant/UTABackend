from .AutoTasker import _TaskUIActionChecker, _TaskUIRelationChecker


class AppTasker:
    def __init__(self, model_manager):
        """
        Initializes the AppTasker.
        Args:
            model_manager: ModelManager
        """
        self.__model_manager = model_manager
        self.__relation_checker_identifier = 'app_analyser'
        self.__action_checker_identifier = 'action checker'

        self.__relation_checker = _TaskUIRelationChecker(model_identifier=self.__relation_checker_identifier,
                                                         model_manager=self.__model_manager)
        self.__action_checker = _TaskUIActionChecker(model_identifier=self.__action_checker_identifier,
                                                         model_manager=self.__model_manager)

    def initialize_agents(self):
        """
            Initialize all agents.
        """
        self.__relation_checker.initialize_agent()
        self.__action_checker.initialize_agent()

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
        return self.__relation_checker.check_relation(ui=ui_data, task=task,
                                                                except_elements=except_elements, printlog=printlog)

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
        return self.__action_checker.check_action(ui=ui_data, task=task,
                                                            except_elements=except_elements, printlog=printlog)

    def analyze_ui_task(self, ui_data, task, except_elements=None, printlog=False):
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
        relation = self.check_task_ui_relation(ui_data=ui_data,
                                               task=task, except_elements=except_elements, printlog=printlog)
        # If the task is unrelated to this UI, return unrelated status to try to launch related app
        if relation.relation == 'Unrelated':
            return 0
        # If the task is already completed, return complete status
        elif relation.relation == 'Completed':
            return 1
        # If the task is related to this UI, check UI action
        else:
            # 2. check the ui action
            action = self.check_ui_action(ui_data=ui_data,
                                          task=task, except_elements=except_elements, printlog=printlog)
            return 2, action
