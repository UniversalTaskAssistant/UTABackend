from .AutoTasker import _TaskUIActionChecker, _TaskUIRelationChecker


class SystemTasker:
    def __init__(self, **kwargs):
        """
        Initializes the SystemTasker with required paths and settings.
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
            _Relation between the ui and the task.
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
            _Action with the determined action and target element.
        """
        return self.action_checker.check_action(ui=ui_data, task=task, except_elements=except_elements, printlog=printlog)

    def system_tasking(self, ui_data, task, printlog=False, show_operation=False):
        """
        Executes a system task, automating UI interactions based on the task description.
        Args:
            task_id (int): Identifier for the task.
            task (str): Description of the task.
            printlog (bool): If True, enables logging.
            show_operation (bool): If True, shows UI operations.
            max_try (int): Maximum number of steps to attempt for the task.
        Returns:
            _Task: Task information.
        """
        print('\n\n*** Task Automation For:', task, '***')
        task_record = _Task(task_id, task)

        step_id = 0
        while step_id < max_try:
            try:
                step_id += 1
                print('\nStep :', step_id)

                step_record = self.auto_tasker.automate_task(step_id, task, printlog=printlog,
                                                            show_operation=show_operation)
                task_record.append(step_record)
                execution_result = step_record.execution_result
                print(execution_result)

                if execution_result == "Task is completed.":
                    task_record.set_attributes(execution_result=execution_result)
                    return task_record
                elif execution_result == "Enter next turn.":
                    continue
                else:
                    task_record.set_attributes(execution_result=execution_result)
                    return task_record

            except Exception as e:
                task_record.set_attributes(execution_result=str(e))
                print('error:', e)
                return task_record

        execution_result = 'Over the max tries.'
        print(execution_result)
        task_record.set_attributes(execution_result=execution_result)
        return False

    def reset_system_tasker(self):
        """
        Resets the internal state of the model agents.
        """
        self.relation_checker.reset_ui_relation_checker()
        self.action_checker.reset_ui_action_checker()

