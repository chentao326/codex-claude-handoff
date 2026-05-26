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

PHASE_MAP = {
    "plan-ready.json": {"phase": "plan-ready", "actor": "codex", "action": "Build: read spec and implement tasks"},
    "build-done.json": {"phase": "build-done", "actor": "claude", "action": "Review: check git diff against spec"},
    "review-fixes.json": {"phase": "review-fixes", "actor": "codex", "action": "Polish: fix review issues"},
    "polish-done.json": {"phase": "polish-done", "actor": "claude", "action": "Re-review: verify fixes"},
    "review-passed.json": {"phase": "review-passed", "actor": "either", "action": "Commit: generate message and commit"},
    "committed.json": {"phase": "done", "actor": "none", "action": "Complete. No action needed."},
}

HELP_TEXT = """\
Usage: check_phase.py [OPTIONS]

Detect the current handoff phase by checking signal files in the handoff/ directory.

Options:
  -h, --help    Show this help message and exit.
  -p, --plain   Output phase name only (no JSON).
  --handoff-dir PATH  Use PATH as the handoff directory (default: handoff).

Exit codes:
  0  Phase detected successfully.
  1  Error (e.g., directory not found, invalid state)."""


def detect_phase(handoff_dir=HANDOFF_DIR):
    if not os.path.isdir(handoff_dir):
        return {"phase": "init", "message": "No handoff directory. Claude Code should write specs first."}

    found = []
    for f in PHASE_ORDER:
        path = os.path.join(handoff_dir, f)
        if os.path.exists(path):
            found.append(f)

    if not found:
        return {"phase": "init", "message": "handoff/ directory exists but no signal files found."}

    latest = found[-1]

    # Special case: polish-done + review-passed both exist
    if "polish-done.json" in found and "review-passed.json" in found:
        polish_time = os.path.getmtime(os.path.join(handoff_dir, "polish-done.json"))
        review_time = os.path.getmtime(os.path.join(handoff_dir, "review-passed.json"))
        if polish_time > review_time:
            return {"phase": "polish-done", "actor": "claude", "action": "Re-review: verify fixes"}

    result = PHASE_MAP.get(latest, {"phase": "unknown", "actor": "unknown", "action": "Unknown state"})
    result["signal_files"] = found
    return result


def main():
    args = sys.argv[1:]
    handoff_dir = HANDOFF_DIR
    plain = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print(HELP_TEXT)
            return 0
        elif arg in ("-p", "--plain"):
            plain = True
        elif arg == "--handoff-dir":
            i += 1
            if i >= len(args):
                print("Error: --handoff-dir requires a path argument.", file=sys.stderr)
                return 1
            handoff_dir = args[i]
        else:
            print(f"Error: unknown option '{arg}'. Use -h for help.", file=sys.stderr)
            return 1
        i += 1

    try:
        phase = detect_phase(handoff_dir)
    except OSError as e:
        print(f"Error: cannot read handoff directory: {e}", file=sys.stderr)
        return 1

    if plain:
        print(phase.get("phase", "unknown"))
    else:
        print(json.dumps(phase, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
