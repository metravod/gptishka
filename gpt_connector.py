from typing import Tuple

import openai

from settings.common import forming_message
from settings.gpt_config import GPT_API_KEY, context_for_naming


class GPTConnector:

    def __init__(self, talk: list):
        self._talk = talk

    def run(self) -> Tuple[str, int]:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            api_key=GPT_API_KEY,
            messages=self._talk
        )
        content = response['choices'][0]['message']['content']
        tokens = response['usage']['total_tokens']
        return content, tokens


def define_name_chat(message: str) -> str:
    chat_for_naming = context_for_naming.copy()
    chat_for_naming.append(forming_message('user', message))
    name_chat, _ = GPTConnector(chat_for_naming).run()
    print('#####', name_chat)
    return name_chat
