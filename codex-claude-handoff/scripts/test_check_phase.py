#!/usr/bin/env python3
"""Tests for check_phase.py."""
import json
import os
import sys
import tempfile
import time
import unittest

# Allow running from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_phase import detect_phase, HANDOFF_DIR


class TestDetectPhase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.handoff = os.path.join(self.tmpdir.name, "handoff")

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write(self, filename, content=None):
        path = os.path.join(self.handoff, filename)
        if content is None:
            content = {}
        with open(path, "w") as f:
            json.dump(content, f)
        return path

    def test_no_handoff_dir(self):
        result = detect_phase(handoff_dir="/nonexistent/path")
        self.assertEqual(result["phase"], "init")
        self.assertIn("No handoff directory", result["message"])

    def test_empty_handoff_dir(self):
        os.makedirs(self.handoff)
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "init")
        self.assertIn("no signal files", result["message"])

    def test_plan_ready(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json", {"stage": "plan-ready"})
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "plan-ready")
        self.assertEqual(result["actor"], "codex")

    def test_build_done(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json")
        self._write("build-done.json", {"stage": "build-done"})
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "build-done")
        self.assertEqual(result["actor"], "claude")

    def test_review_fixes(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json")
        self._write("build-done.json")
        self._write("review-fixes.json", {"stage": "review-fixes"})
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "review-fixes")
        self.assertEqual(result["actor"], "codex")

    def test_review_passed(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json")
        self._write("build-done.json")
        self._write("review-passed.json", {"stage": "review-passed"})
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "review-passed")
        self.assertEqual(result["actor"], "either")

    def test_committed(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json")
        self._write("build-done.json")
        self._write("review-passed.json")
        self._write("committed.json", {"stage": "committed"})
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "done")
        self.assertEqual(result["actor"], "none")

    def test_polish_done_newer_than_review_passed(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json")
        self._write("build-done.json")
        self._write("review-fixes.json")
        self._write("review-passed.json")
        self._write("polish-done.json")

        # Make polish-done newer than review-passed
        time.sleep(0.01)
        os.utime(
            os.path.join(self.handoff, "polish-done.json"),
            (time.time(), time.time() + 10),
        )

        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "polish-done")
        self.assertEqual(result["actor"], "claude")

    def test_review_passed_newer_than_polish_done(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json")
        self._write("build-done.json")
        self._write("review-fixes.json")
        self._write("polish-done.json")
        self._write("review-passed.json")

        # Make review-passed newer than polish-done
        time.sleep(0.01)
        os.utime(
            os.path.join(self.handoff, "review-passed.json"),
            (time.time(), time.time() + 10),
        )

        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "review-passed")
        self.assertEqual(result["actor"], "either")

    def test_signal_files_included(self):
        os.makedirs(self.handoff)
        self._write("plan-ready.json")
        self._write("build-done.json")
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["signal_files"], ["plan-ready.json", "build-done.json"])

    def test_unknown_state_with_unexpected_file(self):
        os.makedirs(self.handoff)
        # Write a file not in PHASE_ORDER
        with open(os.path.join(self.handoff, "garbage.json"), "w") as f:
            f.write("{}")
        result = detect_phase(handoff_dir=self.handoff)
        self.assertEqual(result["phase"], "init")


if __name__ == "__main__":
    unittest.main()
