from DataStructures import *
from Observer import Observer


class HistoryManager(Observer):
    def __init__(self):
        self.inquiry_step_dict = dict()
        self.autonomic_task_dict = dict()

    def notify(self, **kwargs):
        assert 'command' in kwargs

        if kwargs['command'] == 'Store InquiryStep':
            self.store_inquiry_step(kwargs['step_id'], kwargs['parent_id'], kwargs['user_conversation'],
                                    kwargs['llm_conversation'])

    def store_inquiry_step(self, step_id, parent_id, user_conversation, llm_conversation):
        assert step_id not in self.inquiry_step_dict
        assert parent_id in self.autonomic_task_dict

        inquiry_step = InquiryStep(step_id=step_id, parent_id=parent_id, user_conversation=user_conversation,
                                   llm_conversation=llm_conversation)
        self.inquiry_step_dict[step_id] = inquiry_step
        self.autonomic_task_dict[parent_id].append_step(inquiry_step)
        self.autonomic_task_dict[parent_id].set_attributes(execution_result="Finish")
