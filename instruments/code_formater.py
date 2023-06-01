class CodeFormatter:

    def __init__(self, msg: str):
        self.msg = msg
        self.tag_python = '```python'

    def run(self):
        if self._check_code():
            self._forming_message()

        return self.msg

    def _check_code(self) -> str | None:
        if self.tag_python not in self.msg:
            return None
        else:
            return "It's a code"

    def _forming_message(self) -> None:
        self.msg = self.msg.replace(self.tag_python, '```')
