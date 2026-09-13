#!/usr/bin/env python3
"""Offline tests for mate (no LLM calls): parsing unit tests plus an
integration flow against a fake opencode binary.

Run from anywhere:  python3 -m unittest personal-tools/mate-cli/tests/test_mate.py
or:                 python3 personal-tools/mate-cli/tests/test_mate.py
"""

import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATE = HERE.parent / "mate"


def load_mate():
    loader = SourceFileLoader("mate_under_test", str(MATE))
    spec = importlib.util.spec_from_loader("mate_under_test", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class ExtractTextTest(unittest.TestCase):
    def setUp(self):
        self.mate = load_mate()

    def test_dedupe_keep_last_ordered_by_first_appearance(self):
        nd = "\n".join(
            [
                json.dumps({"type": "step_start", "sessionID": "s", "part": {"id": "p0"}}),
                json.dumps({"type": "text", "sessionID": "s", "part": {"id": "p1", "text": "partial", "time": {"start": 1}}}),
                json.dumps({"type": "text", "sessionID": "s", "part": {"id": "p1", "text": "final answer", "time": {"start": 1, "end": 2}}}),
                json.dumps({"type": "text", "sessionID": "s", "part": {"id": "p2", "text": "part two", "time": {"start": 1, "end": 2}}}),
                json.dumps({"type": "text", "sessionID": "s", "part": {"id": "p1", "text": "final answer", "time": {"start": 1, "end": 2}}}),
            ]
        )
        self.assertEqual(self.mate.extract_text(nd), "final answer\n\npart two")

    def test_empty(self):
        self.assertEqual(self.mate.extract_text(""), "")
        self.assertEqual(self.mate.extract_text("not json\n"), "")

    def test_first_session_id(self):
        line = json.dumps({"type": "text", "sessionID": "ses_9", "part": {"id": "p1"}})
        self.assertEqual(self.mate.first_session_id(line), "ses_9")
        self.assertEqual(self.mate.first_session_id(""), "")


class SplitReplyTest(unittest.TestCase):
    def setUp(self):
        self.mate = load_mate()

    def test_prose_block_trailing_dropped(self):
        reply = "intro\nsecond line\n```bash\ndu -sh |\nsort -h\n```\nafter prose"
        self.assertEqual(
            self.mate.split_reply(reply),
            ("intro\nsecond line", "du -sh |\nsort -h"),
        )

    def test_bare_fence(self):
        self.assertEqual(self.mate.split_reply("intro\n```\nls -la\n```"), ("intro", "ls -la"))

    def test_block_only(self):
        self.assertEqual(self.mate.split_reply("```bash\nls\n```"), ("", "ls"))

    def test_no_fence(self):
        self.assertEqual(self.mate.split_reply("just text"), ("just text", ""))

    def test_first_block_wins(self):
        reply = "```bash\nfirst\n```\ntext\n```bash\nsecond\n```"
        self.assertEqual(self.mate.split_reply(reply)[1], "first")


FAKE_OPENCODE = """#!/usr/bin/env bash
echo "ARGS: $*" >> "$FAKE_LOG"
[ -n "$FAKE_DRAIN_STDIN" ] && cat > /dev/null
prompt="${!#}"
sid=""; prev=""
for a in "$@"; do [[ "$prev" == "--session" ]] && sid="$a"; prev="$a"; done
if [[ "$sid" == "ses_dead" ]]; then echo "Session not found" >&2; exit 1; fi
case "$prompt" in
  "[DO]"*|"[REWORK]"*)
    printf '%s\\n' '{"type":"text","sessionID":"ses_fake123","part":{"id":"p1","text":"Prints a greeting from the fake command.\\n```bash\\necho hello-from-cmd\\n```","time":{"start":1,"end":2}}}' ;;
  "[RESULT]"*)
    printf '%s\\n' '{"type":"text","sessionID":"ses_fake123","part":{"id":"p1","text":"noted.","time":{"start":1,"end":2}}}' ;;
  *)
    printf '%s\\n' '{"type":"text","sessionID":"ses_fake123","part":{"id":"p1","text":"the answer is 42","time":{"start":1,"end":2}}}' ;;
esac
"""


@unittest.skipUnless(os.name == "posix", "fake opencode uses a bash shebang")
class WrapperIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.work)], check=False))
        fake = self.work / "opencode"
        fake.write_text(FAKE_OPENCODE)
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        self.fake_log = self.work / "fake.log"
        self.fake_log.write_text("")
        self.state = self.work / "state"
        self.env = dict(
            os.environ,
            OPENCODE_BIN=str(fake),
            MATE_STATE_DIR=str(self.state),
            MATE_DEBUG=str(self.work / "last.ndjson"),
            FAKE_LOG=str(self.fake_log),
        )
        self.home = os.environ["HOME"]

    def mate_cli(self, *args, input_text=None):
        return subprocess.run(
            [sys.executable, str(MATE), *args],
            input=input_text,
            capture_output=True,
            text=True,
            env=self.env,
        )

    def do_env(self):
        # Simulate a backend that drains inherited stdin (real opencode does);
        # the wrapper must keep its confirmation input for itself.
        env = dict(self.env, FAKE_DRAIN_STDIN="1")
        return env

    def mate_cli_drain(self, *args, input_text=None):
        return subprocess.run(
            [sys.executable, str(MATE), *args],
            input=input_text,
            capture_output=True,
            text=True,
            env=self.do_env(),
        )

    def run_lines(self):
        return [l for l in self.fake_log.read_text().splitlines() if l.startswith("ARGS: run")]

    def test_ask_creates_and_reuses_session(self):
        proc = self.mate_cli("ask", "hi")
        self.assertEqual(proc.stdout.strip(), "the answer is 42")
        self.assertEqual((self.state / "session.id").read_text().strip(), "ses_fake123")
        self.assertEqual(
            self.run_lines()[0],
            f"ARGS: run --format json --agent mate --dir {self.home} --title mate [ASK] hi",
        )

        proc = self.mate_cli("ask", "again")
        self.assertEqual(proc.stdout.strip(), "the answer is 42")
        self.assertEqual(
            self.run_lines()[1],
            f"ARGS: run --format json --agent mate --dir {self.home} --session ses_fake123 [ASK] again",
        )

    def test_do_flow_with_prose(self):
        proc = self.mate_cli_drain("do", "demo", input_text="Y\n")
        combined = proc.stdout + proc.stderr
        self.assertIn("─ explanation", combined)
        self.assertIn("Prints a greeting", combined)
        self.assertIn("─ command", combined)
        self.assertIn("hello-from-cmd", combined)
        self.assertIn("─ output", combined)
        self.assertIn("─ exit 0", combined)
        self.assertIn("mate: noted.", combined)
        self.assertIn(
            "[RESULT] exit=0; last output (tail): hello-from-cmd",
            self.fake_log.read_text(),
        )

    def test_dead_session_recreated(self):
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "session.id").write_text("ses_dead\n")
        proc = self.mate_cli("ask", "recover")
        self.assertEqual(proc.stdout.strip(), "the answer is 42")
        self.assertIn("stored session not found", proc.stderr)
        self.assertEqual((self.state / "session.id").read_text().strip(), "ses_fake123")

    def test_reset_clears_state(self):
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "session.id").write_text("ses_fake123\n")
        proc = self.mate_cli("reset")
        self.assertFalse((self.state / "session.id").exists())
        self.assertIn("session state cleared", proc.stdout)

    def test_lingo_is_one_shot_and_never_touches_session(self):
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "session.id").write_text("ses_keep\n")
        proc = self.mate_cli("lingo", "slump")
        self.assertEqual(proc.stdout.strip(), "the answer is 42")
        self.assertEqual(
            self.run_lines()[-1],
            f"ARGS: run --format json --agent lingo --dir {self.home} --title lingo slump",
        )
        # The shared mate session is neither consumed nor overwritten.
        self.assertEqual((self.state / "session.id").read_text(), "ses_keep\n")

    def test_lingo_reads_stdin_dash(self):
        proc = self.mate_cli("lingo", "-", input_text="piped text\n")
        self.assertIn("the answer is 42", proc.stdout)
        self.assertTrue(self.run_lines()[-1].endswith("piped text"))

    def test_lingo_reads_piped_stdin_without_args(self):
        proc = self.mate_cli("lingo", input_text="piped text\n")
        self.assertIn("the answer is 42", proc.stdout)
        self.assertTrue(self.run_lines()[-1].endswith("piped text"))

    def test_lingo_no_input_errors(self):
        proc = self.mate_cli("lingo")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("usage: mate lingo", proc.stderr)

    def test_no_args_prints_usage(self):
        proc = self.mate_cli()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("mate — personal assistant", proc.stdout)

    def test_unknown_subcommand(self):
        proc = self.mate_cli("frobnicate")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("unknown subcommand", proc.stderr)


if __name__ == "__main__":
    unittest.main()
