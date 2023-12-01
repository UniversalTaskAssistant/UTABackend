from ModelManagement._OpenAI import _OpenAI
import time
import json
import logging
import openai


class AssistantModel(_OpenAI):
    def __init__(self, **kwargs):
        # Initialize the AssistantModel with default settings, and override with any provided kwargs
        self.default_config = {
            'model': 'gpt-4-1106-preview',
            'seed': 42,
            'temperature': 0.0,
            'tools': [{'type': 'code_interpreter'}, {'type': 'retrieval'}]
        }
        self.default_config.update(kwargs)
        super().__init__(**self.default_config)

        self.assistant = openai.beta.assistants.create(**self.default_config)
        self.session_to_thread = dict()
        self.conversations_by_thread = dict()

    def create_conversation(self, session_id, conversation, printlog=False, runtime=False, **kwargs):
        # Create a conversation with GPT-4 based on the input and configuration
        start = time.time()
        thread = self.create_thread(session_id)

        conversation = {'role': 'user', 'content': conversation}

        if printlog:
            logging.info('Asking: %s', conversation)

        # Add the new conversation message to the history
        self.conversations_by_thread[thread.id].append(conversation)

        # Prepare configuration for OpenAI API call
        conversation_config = {**self.default_config, **{'messages': self.conversations}, **kwargs}

        try:
            # Call the OpenAI API to get a response
            resp = openai.chat.completions.create(**conversation_config)
            if printlog:
                print('\n*** Answer ***\n', resp.choices[0].message, '\n')

            msg = dict(resp.choices[0].message)
            if runtime:
                msg['content'] = json.loads(msg['content'])
                msg['content']['Runtime'] = '{:.3f}s'.format(time.time() - start)
                msg['content'] = json.dumps(msg['content'])


            # Append the processed response to conversation history
            self.conversations.append({'role': msg['role'], 'content': msg['content']})
            return msg
        except Exception as e:
            logging.error('Error in creating conversation: %s', e)
            raise e

    def create_thread(self, session_id):
        try:
            if not self.session_to_thread.get(session_id) is None:
                thread = openai.beta.threads.create()
                self.session_to_thread[session_id] = thread
                self.conversations_by_thread[thread.id] = []
                return thread
            else:
                return self.session_to_thread[session_id]
        except Exception as e:
            raise e

    def get_thread_id(self, session_id):
        if not self.session_to_thread.get(session_id) is None:
            return self.session_to_thread[session_id].id
        else:
            return self.create_thread(session_id).id