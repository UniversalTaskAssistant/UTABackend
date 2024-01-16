import json
from uta.DataStructures import *
from uta.config import *
from uta.TaskAction._TaskUIChecker import _TaskUIChecker


class TaskActionChecker:
    def __init__(self, model_manager):
        """
        Initialize TaskActionChecker object.
        """
        self.__model_manager = model_manager
        self.__task_ui_checker = _TaskUIChecker(model_manager)

    def action_inquiry(self, task, user_message, printlog=False):
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

    def action_on_ui(self, ui_data, task, printlog=False):
        """
        Check the action in the UI to complete the task
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action (dict): {"Action":, "Element":, "Reason":, "Description":, "Input Text":}
        """
        print('\n*** Check Action on UI *** ')
        # Check ui task relation
        self.check_ui_relation(ui_data, task, printlog)
        # [Complete] => Finish
        if 'complete' in task.res_relation_check['Relation'].lower():
            action = {"Action": "Complete", "Reason": task.res_relation_check['Relation']['Reason']}
        # [Unrelated UI] => Check whether the ui can go back or check other app
        elif 'unrelated' in task.res_relation_check['Relation'].lower():
            # 1. Check if it can go back to a related gui
            go_back = self.check_ui_go_back_availability(ui_data, task, printlog)
            if 'yes' in go_back['Can'].lower():
                action = {"Action": "Click", "Element": go_back['Element'], "Description": go_back['Description']}
            # 2. Check if it can find another related app
            else:
                action = {"Action": "Other App"}
        # [Related UI] => Check action
        else:
            action = self.check_element_action(ui_data, task, printlog)
            try:
                action['Coordinate'] = ui_data.elements[int(action['Element'])]
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
            FM response (dict): {"Action":"Input", "Element":3, "Description":, "Reason":, "Input Text": "Download Trump"}
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
            FM response (dict): {"Can":"Yes", "Element": 2, "Reason":, "Description":"Click on the "go back" element"}
        """
        return self.__task_ui_checker.check_ui_go_back_availability(ui_data, task, printlog)
