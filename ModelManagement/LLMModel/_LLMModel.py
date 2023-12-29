from ._OpenAI import _OpenAI
import time
import logging
import openai


class _LLMModel(_OpenAI):
    def __init__(self, system_prompt=None, **kwargs):
        # Initialize the TextModel with default settings, and override with any provided kwargs
        super().__init__(system_prompt, **kwargs)

    def create_conversation(self, conversation, printlog=False, runtime=False, include_history=True, **kwargs):
        # Create a conversation with GPT-4 based on the input and configuration
        start = time.time()

        conversation = {'role': 'user', 'content': conversation}

        if printlog:
            logging.info('Asking: %s', conversation)

        # Add the new conversation message to the history
        self._conversations.append(conversation)

        # Prepare configuration for OpenAI API call
        if include_history:
            conversation_config = {**self._default_config, **{'messages': self._conversations}, **kwargs}
        else:
            conversation_config = {**self._default_config, **{'messages': conversation}, **kwargs}

        try:
            # Call the OpenAI API to get a response
            resp = openai.chat.completions.create(**conversation_config)
            if printlog:
                print('\n*** Answer ***\n', resp.choices[0].message, '\n')

            msg = dict(resp.choices[0].message)
            if runtime:
                msg['runtime'] = '{:.3f}s'.format(time.time() - start)

            # Append the processed response to conversation history
            self._conversations.append({'role': msg['role'], 'content': msg['content']})
            return msg
        except Exception as e:
            logging.error('Error in creating text conversation: %s', e)
            raise e
