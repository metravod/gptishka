import openai

from settings.gpt_config import GPT_API_KEY


class GPTConnector:

    def __init__(self, talk: list):
        self._talk = talk

    def run(self) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            api_key=GPT_API_KEY,
            messages=self._talk
        )
        return response['choices'][0]['message']['content']
