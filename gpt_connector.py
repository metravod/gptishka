from typing import Tuple

import openai

from settings.gpt_config import GPT_API_KEY


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
