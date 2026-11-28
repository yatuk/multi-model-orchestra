"""Errors the command line turns into exit codes. See cli/output.py for the codes."""


class RoombookError(Exception):
    exit_code = 1


class UsageError(RoombookError):
    exit_code = 2


class NotFound(RoombookError):
    exit_code = 3


class PermissionDenied(RoombookError):
    exit_code = 4


class Refused(RoombookError):
    """A booking broke one or more rules. verdicts holds every error, not only the first."""
    exit_code = 1

    def __init__(self, verdicts):
        self.verdicts = list(verdicts)
        super().__init__("; ".join(v.message for v in self.verdicts))


class RestoreError(RoombookError):
    exit_code = 1
