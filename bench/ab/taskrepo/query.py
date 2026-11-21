"""A tiny filter language. See TASKS.md, task 4, for the grammar."""


class ParseError(ValueError):
    def __init__(self, message, pos):
        super().__init__(f"{message} at {pos}")
        self.pos = pos


def parse(text):
    raise NotImplementedError


def matches(text, record):
    raise NotImplementedError
