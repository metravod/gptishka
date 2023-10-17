import os
from typing import Tuple

import openai

from tools.message_formater import forming_message

gpt_token = os.getenv('GPT_API_KEY')
context_for_naming = os.getenv('CONTEXT_FOR_NAMING')


class GPTConnector:

    def __init__(self, talk: list):
        self._talk = talk

    def run(self) -> Tuple[str, int]:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            api_key=gpt_token,
            messages=self._talk
        )
        content = response['choices'][0]['message']['content']
        tokens = response['usage']['total_tokens']
        return content, tokens


def define_name_chat(message: str) -> str:
    chat_for_naming = context_for_naming.copy()
    chat_for_naming.append(forming_message('user', message))
    name_chat, _ = GPTConnector(chat_for_naming).run()
    return name_chat
