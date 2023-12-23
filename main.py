from DataStructures import *
from ModelManagement import ModelManager
from SystemConnection import SystemConnector
from TaskDeclearation import TaskDeclarator
from TaskExecution import AppTasker, InquiryTasker
from ThirdPartyAppManagement import ThirdPartyAppManager
from UIProcessing import UIProcessor


class UTA:
    def __init__(self):
        self.model_manager = ModelManager()
        self.task_declarator = TaskDeclarator(self.model_manager)

    def initialize_agents(self):
        self.task_declarator.initialize_agents()

    def clarify_task(self, task, printlog=False):
        '''
        Clarify task to be clear to complete
        Args:
            task (string): The user's task
            printlog (bool): True to print the intermediate log
        Returns:
            LLM answer (dict): {"Task Type": "1. General Inquiry", "Explanation":}
        '''
        return self.task_declarator.clarify_task(org_task=task, printlog=printlog)