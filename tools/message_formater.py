import re
from functools import reduce
from typing import Tuple


class MessageFormatter:

    def __init__(self, msg: str):
        self._input_msg = msg
        self._tag_python = '```python'

    def formating(self) -> Tuple[str, bool]:
        self._check_of_this_is_code()
        if self.its_a_code:
            self._remove_python_tag()

        return self.format_msg, self.its_a_code

    def _check_of_this_is_code(self) -> None:
        self.its_a_code = True if self._tag_python not in self._input_msg else False

    def _remove_python_tag(self) -> None:
        """Телега умеет в форматирование только если нет уточнения что это за язык"""
        self.format_msg = self._input_msg.replace(self._tag_python, '```')


def extracting_code(msg: str) -> str:
    find_code_regex = "\```(.*?)\```/g"
    snipets = re.findall(find_code_regex, msg)
    full_code = reduce(lambda x, y: x + f'\n# next snipet \n' + y, snipets)
    return full_code
