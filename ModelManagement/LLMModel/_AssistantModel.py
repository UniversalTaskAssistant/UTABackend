from ._OpenAI import _OpenAI
import time
import json
import logging
import openai


class _AssistantModel(_OpenAI):
    def __init__(self, instructions="NOT_GIVEN", **kwargs):
        super().__init__(**kwargs)

        # Initialize the AssistantModel with default settings, and override with any provided kwargs
        self._default_config = {
            'model': 'gpt-4-1106-preview',
            'tools': [{'type': 'code_interpreter'}, {'type': 'retrieval'}],  # coding and searching tools are enabled
            # for the model
            'instructions': instructions  # following OpenAI default definition, instructions by default is "NOT_GIVEN"
        }
        self._default_config.update(kwargs)

        # Create an assistant with the specified configuration
        self.__assistant = openai.beta.assistants.create(**self._default_config)

        # Dictionaries to manage task-to-thread mapping and conversations by thread
        self.__task_to_thread = dict()
        self.__conversations_by_thread = dict()

    def create_conversation(self, task_id, conversation, printlog=False, runtime=False):
        # Create a conversation with GPT-4 based on the input and configuration
        start = time.time()
        thread = self.__create_thread(task_id)

        if printlog:
            logging.info('Asking: %s', conversation)

        # Add the new conversation message to the history
        self.__conversations_by_thread[thread.id].append({'role': 'user', 'content': conversation})

        try:
            # Call the OpenAI API to get a response
            resp = self.__run_gpts(thread, conversation)
            if printlog:
                print('\n*** Answer ***\n', resp, '\n')

            msg = {'content': resp}
            if runtime:
                msg['content'] = json.loads(msg['content'])
                msg['content']['Runtime'] = '{:.3f}s'.format(time.time() - start)
                msg['content'] = json.dumps(msg['content'])

            # Append the processed response to conversation history
            self.__conversations_by_thread[thread.id].append({'role': "assistant", 'content': msg['content']})
            return msg
        except Exception as e:
            logging.error('Error in creating assistant conversation: %s', e)
            raise e

    def __run_gpts(self, thread, content):
        """
        Run the GPT-4 model to generate responses for a given thread and content.
        """
        try:
            # Create a message in the thread as the user
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=content
            )

            # Start the GPT-4 model run
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.__assistant.id,
            )

            status = ""

            # Poll for the run status until completion, cancellation, failure, or expiration
            while not status in {"completed", "cancelled", "failed", "expired"}:
                time.sleep(1)
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

                status = run_status.status

            # Handle the completed status by fetching the response
            if status == "completed":
                messages = openai.beta.threads.messages.list(
                    thread_id=thread.id
                )

                return messages.data[0].content[0].text.value
            else:
                raise RuntimeError(f"Run did not complete successfully, status: {status}")
        except Exception as e:
            logging.error('Error in creating assistant conversation: %s', e)
            raise e

    def __create_thread(self, task_id):
        """
        Create or retrieve a thread for a given task ID.
        """
        try:
            # Create a new thread if it does not exist for the task
            if self.__task_to_thread.get(task_id) is None:
                thread = openai.beta.threads.create()
                self.__task_to_thread[task_id] = thread
                self.__conversations_by_thread[thread.id] = []
                return thread
            else:
                return self.__task_to_thread[task_id]
        except Exception as e:
            raise e

    def get_thread_id(self, task_id):
        """
        Get the thread ID for a given task ID, raising an error if the task has not been created.
        """
        if not self.__task_to_thread.get(task_id) is None:
            return self.__task_to_thread[task_id].id
        else:
            raise ValueError(f"Task with ID {task_id} has not been created.")

    def get_conversations(self, task_id):
        if not self.__task_to_thread.get(task_id) is None:
            return self.__conversations_by_thread[self.__task_to_thread[task_id].id]
        else:
            raise ValueError(f"Task with ID {task_id} has not been created.")

    def reset_conversations(self, task_id):
        if not self.__task_to_thread.get(task_id) is None:
            self.__conversations_by_thread[self.__task_to_thread[task_id].id] = []
        else:
            raise ValueError(f"Task with ID {task_id} has not been created.")
