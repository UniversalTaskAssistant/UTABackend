from .AutoTasker import _AutoTasker
from ._Task import _Task


class SystemTasker:
    def __init__(self, **kwargs):
        """
        Initializes the SystemTasker with required paths and settings.
        Args:
            **kwargs: Keyword arguments containing paths and settings for task automation.
                      Required keys are 'img_path', 'xml_path', 'ui_resize', and 'output_dir'.
        """
        self.__img_path = kwargs['img_path']
        self.__xml_path = kwargs['xml_path']
        self.__ui_resize = kwargs['ui_resize']
        self.__output_dir = kwargs['output_dir']

        self.auto_tasker = _AutoTasker(self.__img_path, self.__xml_path, self.__ui_resize, self.__output_dir)

    def execute_system_task(self, task_id, task, printlog=False, show_operation=False, max_try=100):
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
        Resets the internal state of the auto_tasker, including its model agents.
        """
        self.auto_tasker.reset_model_agents()

