from ModelManagement import ModelManager


class _AppAnalyser:
    def __init__(self, system_prompt=None, **kwargs):
        """
        Initializes the AppAnalyser.
        Args:
            system_prompt (str, optional): Custom system prompt for the text model.
            **kwargs: Additional keyword arguments for text model initialization.
        """
        self.__model_manager = ModelManager()
        self.__model_manager.initialize_llm_model("app_analyser_model", system_prompt=system_prompt, **kwargs)

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
            self.__model_manager.reset_llm_conversations("app_analyser_model")

            conversation = self.__base_prompt.format(title=tar_app['title'], description=tar_app['description'],
                                                     printlog=printlog)

            task_list = self.__model_manager.create_llm_conversation("app_analyser_model", conversation,
                                                                     printlog=printlog)['content']
            task_list = task_list.replace('\n', '').split(';')
            task_list = task_list[:-1] if len(task_list[-1]) == 0 else task_list
            task_list = [t.replace('\n', '').replace(' -', '-') for t in task_list]

            return task_list
        except Exception as e:
            raise e