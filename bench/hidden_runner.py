"""Run test modules in a clean directory and write each test's outcome as JSON.

    python -I hidden_runner.py DIR RESULT_JSON MODULE [MODULE ...]

Called by grade.py in a fresh directory that holds only the lane's package and the
grader's own copies of the tests. -I keeps the environment, user site-packages and this
script's folder out of sys.path; DIR is added by hand, after unittest is imported, so a
file the lane names unittest.py cannot replace it.
Also checks the names listed in each module's PUBLIC list (dotted paths) and records the
ones that do not resolve.
"""
import importlib
import json
import os
import sys
import unittest


def resolve(dotted):
    parts = dotted.split(".")
    for i in range(len(parts), 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:i]))
        except Exception:
            continue
        for name in parts[i:]:
            obj = getattr(obj, name)
        return obj
    raise ImportError(dotted)


class Recorder(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.outcome = {}

    def addSuccess(self, test):
        self.outcome.setdefault(test.id(), "pass")

    def addFailure(self, test, err):
        self.outcome[test.id()] = "fail"

    def addError(self, test, err):
        self.outcome[test.id()] = "error"

    def addSkip(self, test, reason):
        self.outcome[test.id()] = "skip"

    def addExpectedFailure(self, test, err):
        self.outcome[test.id()] = "fail"

    def addUnexpectedSuccess(self, test):
        self.outcome[test.id()] = "fail"

    def addSubTest(self, test, subtest, err):
        # A failing subtest fails its whole test; a passing one changes nothing.
        if err is not None:
            self.outcome[test.id()] = "fail"


def main():
    wd, result_path, modules = sys.argv[1], sys.argv[2], sys.argv[3:]
    sys.path.insert(0, wd)
    os.chdir(wd)
    rec = Recorder()
    missing = []
    for mod in modules:
        try:
            m = importlib.import_module(mod)
        except Exception as e:
            rec.outcome[f"{mod}:import"] = f"import error: {type(e).__name__}"
            continue
        for dotted in getattr(m, "PUBLIC", []):
            try:
                resolve(dotted)
            except Exception:
                missing.append(dotted)
        unittest.defaultTestLoader.loadTestsFromModule(m).run(rec)
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({"outcome": rec.outcome, "missing": missing}, f)


if __name__ == "__main__":
    main()
