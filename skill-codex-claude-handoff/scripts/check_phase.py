#!/usr/bin/env python3
"""Detect the current handoff phase by checking signal files."""
import json
import os
import sys
from datetime import datetime, timezone

HANDOFF_DIR = "handoff"

PHASE_ORDER = [
    "plan-ready.json",
    "build-done.json",
    "review-fixes.json",
    "polish-done.json",
    "review-passed.json",
    "committed.json",
]

def detect_phase():
    if not os.path.isdir(HANDOFF_DIR):
        return {"phase": "init", "message": "No handoff directory. Claude Code should write specs first."}

    found = []
    for f in PHASE_ORDER:
        path = os.path.join(HANDOFF_DIR, f)
        if os.path.exists(path):
            found.append(f)

    if not found:
        return {"phase": "init", "message": "handoff/ directory exists but no signal files found."}

    # Determine phase from the latest signal file
    latest = found[-1]

    phase_map = {
        "plan-ready.json": {"phase": "plan-ready", "actor": "codex", "action": "Build: read spec and implement tasks"},
        "build-done.json": {"phase": "build-done", "actor": "claude", "action": "Review: check git diff against spec"},
        "review-fixes.json": {"phase": "review-fixes", "actor": "codex", "action": "Polish: fix review issues"},
        "polish-done.json": {"phase": "polish-done", "actor": "claude", "action": "Re-review: verify fixes"},
        "review-passed.json": {"phase": "review-passed", "actor": "either", "action": "Commit: generate message and commit"},
        "committed.json": {"phase": "done", "actor": "none", "action": "Complete. No action needed."},
    }

    # Special case: polish-done + review-passed both exist
    if "polish-done.json" in found and "review-passed.json" in found:
        polish_time = os.path.getmtime(os.path.join(HANDOFF_DIR, "polish-done.json"))
        review_time = os.path.getmtime(os.path.join(HANDOFF_DIR, "review-passed.json"))
        if polish_time > review_time:
            return {"phase": "polish-done", "actor": "claude", "action": "Re-review: verify fixes"}

    result = phase_map.get(latest, {"phase": "unknown", "actor": "unknown", "action": "Unknown state"})
    result["signal_files"] = found
    return result


if __name__ == "__main__":
    phase = detect_phase()
    print(json.dumps(phase, indent=2))
