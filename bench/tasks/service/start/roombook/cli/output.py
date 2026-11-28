"""Printing for the commands. Exit codes:

  0 done   1 refused by a rule (or a restore problem)   2 bad command line
  3 not found   4 not allowed
"""
import sys

OK = 0


class Out:
    def __init__(self, stdout=None, stderr=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def line(self, text=""):
        self.stdout.write(text + "\n")

    def lines(self, lines):
        for text in lines:
            self.line(text)

    def warn(self, text):
        self.stderr.write(f"warning: {text}\n")

    def note(self, text):
        self.stdout.write(f"note: {text}\n")

    def error(self, text):
        self.stderr.write(f"error: {text}\n")

    def refused(self, verdicts):
        for v in verdicts:
            self.stderr.write(f"refused: {v.message}\n")
