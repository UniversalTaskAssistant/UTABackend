from DataStructures import *


class HistoryManager:
    def __init__(self, user_id):
        """
        Initializes the HistoryManager with user-specific history dictionaries and user information.
        Args:
            user_id: Unique identifier for the user.
        """
        self.__auto_mode_step_dict = dict()
        self.__inquiry_step_dict = dict()
        self.__autonomic_task_dict = dict()
        self.__original_task_dict = dict()

        self.__user_id = user_id
        self.__user = User(self.__user_id)

    def initialize_storage(self):
        """
        Reinitializes all history storage dictionaries and user information.
        This method effectively resets the history state of the manager.
        """
        self.__auto_mode_step_dict = dict()
        self.__inquiry_step_dict = dict()
        self.__autonomic_task_dict = dict()
        self.__original_task_dict = dict()
        self.__user = User(self.__user_id)

    def store_inquiry_step(self, step_id, parent_id, user_conversation, llm_conversation):
        """
        Stores a step in the inquiry process.
        Args:
            step_id: Unique identifier for the step.
            parent_id: Identifier of the parent task.
            user_conversation: The conversation input from the user.
            llm_conversation: The response from the language model.
        """
        assert step_id not in self.__inquiry_step_dict
        assert parent_id in self.__autonomic_task_dict

        inquiry_step = InquiryStep(step_id=step_id, parent_id=parent_id,
                                   user_conversation={'role': 'user', 'content': user_conversation},
                                   llm_conversation={'role': 'assistant', 'content': llm_conversation})
        self.__inquiry_step_dict[step_id] = inquiry_step
        self.__autonomic_task_dict[parent_id].append_step(self.__inquiry_step_dict[step_id])
        self.__autonomic_task_dict[parent_id].set_attributes(execution_result="Finish")

    def store_auto_mode_step(self, step_id, parent_id, ui_data, relation, action, execution_result):
        """
        Stores a step in auto mode.
        Args:
            step_id: Unique identifier for the step.
            parent_id: Identifier of the parent task.
            ui_data: User interface data related to the step.
            relation: The relation to the parent task.
            action: Recommended action for the step.
            execution_result: The result of executing the step.
        """
        assert step_id not in self.__auto_mode_step_dict
        assert parent_id in self.__autonomic_task_dict

        auto_mode_step = AutoModeStep(step_id, parent_id=parent_id, ui_data=ui_data, relation=relation,
                                      execution_result=execution_result)
        if action:
            auto_mode_step.set_attributes(recommended_action=action)
            if execution_result == "Can go back, execute the back action.":
                auto_mode_step.set_attributes(is_go_back=True)

        self.__auto_mode_step_dict[step_id] = auto_mode_step
        self.__autonomic_task_dict[parent_id].append_step(self.__auto_mode_step_dict[step_id])
        if execution_result == "No related app can be found.":
            self.__autonomic_task_dict[parent_id].set_attributes(execution_result="Failed")
        elif execution_result == "Task is completed.":
            self.__autonomic_task_dict[parent_id].set_attributes(execution_result="Finish")

    def annotate_ui_openation(self, step_id):
        """
        Annotates a UI operation for the specified auto mode step.
        Args:
            step_id: Unique identifier of the step in the auto mode step dictionary.
        """
        assert step_id in self.__auto_mode_step_dict

        self.__auto_mode_step_dict[step_id].annotate_ui_openation()

    def store_autonomic_task(self, task_id, parent_id, task, task_type):
        """
        Stores an autonomic task in the history.
        Args:
            task_id: Unique identifier for the autonomic task.
            parent_id: Identifier of the parent task in the original task dictionary.
            task: The task object to be stored.
            task_type: The type of the autonomic task.
        """
        assert task_id not in self.__autonomic_task_dict
        assert parent_id in self.__original_task_dict

        new_task = AutonomicTask(task_id, parent_id=parent_id, task=task, task_type=task_type)
        self.__autonomic_task_dict[task_id] = new_task
        self.__original_task_dict[parent_id].append_autonomic_task(self.__autonomic_task_dict[task_id])

    def store_original_task(self, task_id, parent_id, task, conversation, clarified_result):
        """
        Stores an original task in the history.
        Args:
            task_id: Unique identifier for the original task.
            parent_id: Identifier of the parent task, which should be the user ID.
            task: The task object to be stored.
            conversation: Conversation related to the task clarification.
            clarified_result: The result of the clarification process.
        """
        assert parent_id == self.__user_id

        if task_id not in self.__original_task_dict:
            self.__original_task_dict[task_id] = OriginalTask(task_id, parent_id=parent_id, original_task=task)
            self.__user.append_user_task(self.__original_task_dict[task_id])

        self.__original_task_dict[task_id].append_clarifying_conversation(({'role': 'user', 'content': conversation},
                                                                           {'role': 'assistant', 'content':
                                                                               clarified_result}))
        self.__original_task_dict[task_id].set_attributes(clarifyed_task=clarified_result['content'])

    def get_user(self):
        """
        Retrieves the user object associated with the history manager.
        Returns:
            User: The user object.
        """
        return self.__user
