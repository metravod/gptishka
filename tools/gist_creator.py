import requests
import json

from settings.github_config import GITHUB_API_TOKEN, gists_url


class GistCreator:

    def __init__(self, content: str):
        self._headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
        self._params = {'scope': 'gist'}
        self._payload = {
            "description": "GPT generated code",
            "public": False,
            "files": {
                "answer.py": {
                    "content": content
                }
            }
        }

    def post(self) -> str:
        res = requests.post(
            gists_url,
            headers=self._headers,
            params=self._params,
            data=json.dumps(self._payload)
        )
        return res.url
