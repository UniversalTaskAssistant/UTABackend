

class _ThirdPartyAppAnalyser:
    def __init__(self, model_identifier, model_manager):
        """
        Initializes the AppAnalyser.
        Args:
            model_identifier: Name of the text model.
            model_manager: Initialised ModelManager used by this class.
        """
        self.__model_identifier = model_identifier
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__base_prompt = 'Summarize the main tasks that the app {title} can perform for senior users ' \
                             'who are not familiar with it. ' \
                             'Review the app description: "{description}". \n' \
                             'Focus on specific functionality, presenting them as simple, user-friendly tasks. ' \
                             'Each task should be distinct and cover only one aspect of the app. ' \
                             'List the tasks in a format accessible to seniors, using clear examples where possible. ' \
                             'End each task with a semicolon and start with a dash. \n' \
                             'Example: \n' \
                             '- Watch music videos and stay updated with trends; \n' \
                             '- Subscribe to favorite channels for personalized content; \n' \
                             '...and so on.'

    def conclude_app_functionality(self, tar_app, printlog=False):
        """
        Conclude the functionality of given app.
        Args:
            tar_app: target app to be analyzed.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Functionality of given app.
        """
        try:
            self.__model_manager.reset_llm_conversations(self.__model_identifier)

            conversation = self.__base_prompt.format(title=tar_app['title'], description=tar_app['description'],
                                                     printlog=printlog)

            task_list = self.__model_manager.create_llm_conversation(self.__model_identifier, conversation,
                                                                     printlog=printlog)['content']
            task_list = task_list.replace('\n', '').split(';')
            task_list = task_list[:-1] if len(task_list[-1]) == 0 else task_list
            task_list = [t.replace('\n', '').replace(' -', '-') for t in task_list]

            return task_list
        except Exception as e:
            raise e