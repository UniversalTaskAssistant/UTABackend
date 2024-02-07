from uta.TaskAction._TaskUIChecker import _TaskUIChecker


class TaskActionChecker:
    def __init__(self, model_manager):
        """
        Initialize TaskActionChecker object.
        """
        self.__model_manager = model_manager
        self.__task_ui_checker = _TaskUIChecker(model_manager)

    def action_inquiry(self, task, printlog=False):
        """
        Execute inquiry type task.
        Args:
            task (Task): Task object containing historical inquiry steps.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM's response.
        """
        try:
            action = {"Action": "Search", "Content": task.task_description}
            task.actions.append(action)
            task.res_action_check = action
            return action
        except Exception as e:
            print('error:', e)
            raise e

    def action_on_ui(self, ui_data, task, printlog=False):
        """
        Check the action in the UI to complete the task
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action (dict): {"Action":, "Element Id":, "Reason":, "Description":, "Input Text":}
        """
        print('\n*** Check Action on UI *** ')
        # Check ui task relation
        relation = self.check_ui_relation(ui_data, task, printlog)
        task.relations.append(relation)
        # [Complete] => Finish
        if 'complete' in task.res_relation_check['Relation'].lower():
            action = {"Action": "Complete", **task.res_relation_check}
        # [Unrelated UI] => Check whether the ui can go back or check other app
        elif 'unrelated' in task.res_relation_check['Relation'].lower():
            # 1. Check if it can go back to a related gui
            go_back = self.check_ui_go_back_availability(ui_data, task, printlog)
            if 'yes' in go_back['Can'].lower():
                action = {"Action": "Click", **go_back}  # avoid to directly refer the key in response as not stable
            # 2. Check if it can find another related app
            else:
                action = {"Action": "Other App", **go_back}
        # [Related UI] => Check action
        else:
            action = self.check_element_action(ui_data, task, printlog)
            try:
                bounds = ui_data.elements[int(action['Element Id'])]['bounds']
                centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
                action['Coordinate'] = centroid
                action['ElementBounds'] = bounds
            except Exception as e:
                print(action)
                raise e
        task.actions.append(action)
        return action

    def check_ui_relation(self, ui_data, task, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Relation":, "Reason":}
        """
        return self.__task_ui_checker.check_ui_relation(ui_data, task, printlog)

    def check_element_action(self, ui_data, task, printlog=False):
        """
        Determines the appropriate action and target element in the UI for a given task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Action":"Input", "Element Id":3, "Description":, "Reason":, "Input Text": "Download Trump"}
        """
        return self.__task_ui_checker.check_element_action(ui_data, task, printlog)

    def check_ui_go_back_availability(self, ui_data, task, printlog=False):
        """
        Checks if there is an element in the UI that can be clicked to navigate back in relation to a given task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Can":"Yes", "Element Id": 2, "Reason":, "Description":"Click on the "go back" element"}
        """
        return self.__task_ui_checker.check_ui_go_back_availability(ui_data, task, printlog)
