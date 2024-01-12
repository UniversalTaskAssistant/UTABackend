import json
from uta.DataStructures import *
from uta.config import *
from uta.TaskExecution import _TaskUIChecker


class TaskExecutor:
    def __init__(self, model_manager):
        """
        Initialize TaskExecutor object.
        """
        self.__model_manager = model_manager
        self.__task_ui_checker = _TaskUIChecker(model_manager)

    def execute_inquiry_task(self, task, user_message, printlog=False):
        """
        Execute inquiry type task.
        Args:
            task (Task): Task object containing historical inquiry steps.
            user_message (str): User's question.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM's response.
        """
        try:
            step.user_conversation = {'role': 'user', 'content': user_message}
            inquiry_history_list = [one_conv for step_index, one_step in enumerate(task.steps) if
                                    isinstance(one_step, InquiryStep) for one_conv in
                                    task.conversation_automation[step_index]]
            inquiry_history_list.append(step.user_conversation)

            resp = self.__model_manager.send_fm_conversation(inquiry_history_list, printlog=printlog)
            step.llm_conversation = resp
            task.conversation_automation.append([step.user_conversation, step.llm_conversation])
            return json.loads(resp)
        except Exception as e:
            print('error:', e)
            raise e

    def execute_app_system_task(self, ui_data, task, printlog=False):
        # Check ui task relation
        self.check_relation(ui_data, task, printlog)
        # [Complete] => Finish
        if 'complete' in task.res_relation_check['Relation'].lower():
            action = {"Action": "Complete", "Reason": task.res_relation_check['Relation']['Reason']}
            task.actions.append(action)
        # [Unrelated UI] => check go back for related app, or find related app
        elif 'unrelated' in task.res_relation_check['Relation'].lower():
            # 1. Check if it can go back to a related gui
            go_back = self.check_go_back_availability(ui_data, task, printlog)
            if 'yes' in go_back['Can'].lower():
                action = {"Action": "Click", "Element": go_back['Element'], "Description": go_back['Description']}
            # 2. Check if it can find another related app
            else:
                find_app = self.find_related_app()
                if find_app:
                    action = {"Action": "Launch", "App": find_app['App'], "Description": "Launch app"}
                else:
                    action = {"Action": "Infeasible", "Description": "Infeasible task"}
        # [Related UI] => fulfil task
        else:
            action = self.check_action(ui_data, task, printlog)
        return action

    def check_relation(self, ui_data, task, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Relation":, "Reason":}
        """
        return self.__task_ui_checker.check_relation(ui_data, task, printlog)

    def check_action(self, ui_data, task, printlog=False):
        """
        Determines the appropriate action and target element in the UI for a given task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Action":"Input", "Element":3, "Description":, "Reason":, "Input Text": "Download Trump"}
        """
        return self.__task_ui_checker.check_action(ui_data, task, printlog)

    def check_go_back_availability(self, ui_data, task, printlog=False):
        """
        Checks if there is an element in the UI that can be clicked to navigate back in relation to a given task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Can":"Yes", "Element": 2, "Reason":, "Description":"Click on the "go back" element"}
        """
        return self.__task_ui_checker.check_go_back_availability(ui_data, task, printlog)
