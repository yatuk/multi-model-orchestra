"""Tests for the sub-agent model guard hook. Offline; install tests use a temp settings file, never the real one.

  python -m pytest skills/orchestra/scripts/test_mmo_model_guard.py -q
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "mmo_model_guard.py")


def run_hook(event, mode=None):
    env = dict(os.environ)
    env.pop("MMO_MODEL_GUARD", None)
    if mode is not None:
        env["MMO_MODEL_GUARD"] = mode
    p = subprocess.run([sys.executable, SCRIPT, "hook"], input=json.dumps(event).encode(),
                       capture_output=True, env=env, timeout=30)
    assert p.returncode == 0, p.stderr
    out = p.stdout.decode().strip()
    return json.loads(out) if out else None


def agent(tool="Agent", **tool_input):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}


def decision(out):
    return (out or {}).get("hookSpecificOutput", {}).get("permissionDecision")


class HookTests(unittest.TestCase):
    def test_missing_model_denied(self):
        for tool in ("Agent", "Task"):
            out = run_hook(agent(tool, prompt="do it"))
            self.assertEqual(decision(out), "deny", tool)
            self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")
            self.assertIn("model", out["hookSpecificOutput"]["permissionDecisionReason"])

    def test_empty_model_denied(self):
        self.assertEqual(decision(run_hook(agent(prompt="x", model=""))), "deny")
        self.assertEqual(decision(run_hook(agent(prompt="x", model="  "))), "deny")

    def test_model_present_allowed(self):
        self.assertIsNone(run_hook(agent(prompt="x", model="sonnet")))

    def test_fork_allowed(self):
        self.assertIsNone(run_hook(agent(prompt="x", subagent_type="fork")))

    def test_warn_mode_allows_with_warning(self):
        out = run_hook(agent(prompt="x"), mode="warn")
        self.assertNotEqual(decision(out), "deny")
        self.assertIn("warn", out["hookSpecificOutput"]["additionalContext"])

    def test_off_mode(self):
        self.assertIsNone(run_hook(agent(prompt="x"), mode="off"))

    def test_other_tools_ignored(self):
        self.assertIsNone(run_hook({"tool_name": "Bash", "tool_input": {"command": "ls"}}))

    def test_bad_stdin_is_silent(self):
        p = subprocess.run([sys.executable, SCRIPT, "hook"], input=b"not json", capture_output=True, timeout=30)
        self.assertEqual((p.returncode, p.stdout), (0, b""))


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "settings.json")

    def tearDown(self):
        self.dir.cleanup()

    def cli(self, cmd):
        subprocess.run([sys.executable, SCRIPT, cmd, "--settings", self.path], check=True,
                       capture_output=True, timeout=30)

    def load(self):
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def test_install_twice_is_one_entry(self):
        self.cli("install")
        self.cli("install")
        entries = self.load()["hooks"]["PreToolUse"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["matcher"], "Agent|Task")
        self.assertIn("mmo_model_guard.py", entries[0]["hooks"][0]["command"])

    def test_uninstall_leaves_other_hooks(self):
        other = {"matcher": "Bash", "hooks": [{"type": "command", "command": "other-tool check"}]}
        stop = {"hooks": [{"type": "command", "command": "notify"}]}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"model": "x", "hooks": {"PreToolUse": [other], "Stop": [stop]}}, f)
        self.cli("install")
        self.assertEqual(len(self.load()["hooks"]["PreToolUse"]), 2)
        self.cli("uninstall")
        data = self.load()
        self.assertEqual(data["hooks"]["PreToolUse"], [other])
        self.assertEqual(data["hooks"]["Stop"], [stop])
        self.assertEqual(data["model"], "x")

    def test_uninstall_when_alone_removes_empty_hooks(self):
        self.cli("install")
        self.cli("uninstall")
        self.assertEqual(self.load(), {})

    def test_uninstall_without_file_creates_nothing(self):
        self.cli("uninstall")
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
