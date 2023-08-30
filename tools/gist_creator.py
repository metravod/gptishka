import requests
import json

from settings.github_config import GITHUB_API_TOKEN, gists_url


class GistCreator:

    def __init__(self, content: str):
        self._headers = {'Authorization': f'token {GITHUB_API_TOKEN}',
                         'Accept': 'application/vnd.github+json',
                         'X-GitHub-Api-Version': '2022-11-28'}
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
        url = json.loads(res.content)['html_url']
        return url
