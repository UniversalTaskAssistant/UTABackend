from uta.config import *
import json


class _UIChecker:
    """
    Check the special content and state of the UI
    """
    def __init__(self, model_manager):
        self.__model_manager = model_manager
        self.__base_prompt = 'Given this UI, check if it contains any of the following components that require user decisions:\n' \
                             '1. UI Modal: A window or dialog box overlaying on the top of main content, such as Alerts, Confirmations and Instructions.\n' \
                             '2. User Permission: Asking for user permission to perform app functionalities.\n' \
                             '3. Login Page: Requiring for account login before using app.\n' \
                             '4. Form: Requiring user to fill in data.\n' \
                             '!!!Respond to the following points:\n' \
                             '1. "Component": if the UI contains any of the given components, if not, answer "None".\n' \
                             '2. "Explanation": one-sentence explanation of your decision. \n' \
                             '!!!Note:\n' \
                             'ONLY use this JSON format to provide your answer: {{"Component": "<Component>", "Explanation": "<Explanation>"}}\n' \
                             '!!!Example:\n' \
                             '1. {{"Component": "User Permission", "Explanation": "This UI asks user permission to access photo"}}\n' \
                             '2. {{"Component": "None", "Explanation": "No mentioned components in this UI"}}'

    def check_ui_decision_page(self, ui_data):
        """
        Check if the UI contain any following special components that require user intervention:
        1. UI Modal; 2. User Permission; 3. Login; 4. Form;
        Args:
            ui_data (UIData)
        Returns:
            response (dict): {"Component", "Explanation"}
        """
        try:
            conversation = [{'role': 'user', 'content': f'This is a view hierarchy of a UI '
                                                        f'containing various UI blocks and elements:\n'
                                                        f'{str(ui_data.element_tree)}\n'},
                            {'role': 'user', 'content': self.__base_prompt}]
            resp = self.__model_manager.send_fm_conversation(conversation)
            special_compo = json.loads(resp['content'])
            print(special_compo)
            return special_compo
        except Exception as e:
            print(resp)
            raise e
