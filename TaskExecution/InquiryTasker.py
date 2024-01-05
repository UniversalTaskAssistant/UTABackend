import json


class InquiryTasker:
    def __init__(self, model_manager):
        """
        Initialize InquiryTasker object.
        """
        self.__model_manager = model_manager

    def execute_inquiry_task(self, task, user_message, printlog=False):
        try:
            task.conversation_automation.append({'role': 'user', 'content': user_message})
            resp = self.__model_manager.send_fm_conversation(task.conversation_automation, printlog=printlog)
            task.conversation_automation.append(resp)
            return json.loads(resp)
        except Exception as e:
            print('error:', e)
            return False
