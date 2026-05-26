---
name: codex-claude-handoff
description: Codex + Claude Code collaborative handoff protocol. Automates the 6-phase workflow (Spec→Plan→Build→Review→Polish→Commit) between Codex and Claude Code via file-based signal handshakes. Use when the user mentions "handoff", "交接", "下一阶段", "next phase", "开始编码", "start build", "开始审查", "start review", "协同", "collaborate", "Codex和Claude", "切换工具", or when a handoff/*.json signal file exists in the project.
---

# Codex + Claude Code Handoff

## Overview

Enable Codex and Claude Code to collaborate on the same project through a 6-phase state machine. Signal files in `handoff/` dictate which tool acts next. Codex handles Build and Polish phases; Claude Code handles Spec, Plan, and Review phases.

## Workflow

```
Spec ──→ Plan ──→ Build ──→ Review ──→ Polish ──→ Commit
Claude    Claude    Codex     Claude      Codex      任一
```

## Phase Detection

Always detect the current phase before acting. Run the detection script:

```bash
python3 <skill_dir>/scripts/check_phase.py
```

Or use `--plain` for phase name only. The script examines `handoff/` signal files in order.

| Signal File | Phase | Actor |
|------------|-------|-------|
| (none) | Init | Claude Code writes spec |
| `plan-ready.json` | Plan Ready | Codex builds |
| `build-done.json` | Build Done | Claude Code reviews |
| `review-fixes.json` | Fixes Needed | Codex fixes |
| `polish-done.json` | Polish Done | Claude Code re-reviews |
| `review-passed.json` | Ready | Either tool commits |
| `committed.json` | Done | Announce completion |

Full signal file schemas: `references/protocol.md`.

## Role Rules

- **You are Codex**: Execute coding tasks, fix bugs, write tests. Do NOT design architecture or write specs.
- **Claude Code**: Design, plan, review. Do NOT write implementation code.
- If the current phase belongs to the other tool, stop and tell the user to switch.

## Phase Instructions

### Phase 1: Plan Ready (Codex acts)

1. Read the spec from `specs/` and task list from `handoff/plan-ready.json`
2. Execute tasks in dependency order
3. After EACH task, update `plan-ready.json`: set that task's `status` to `"completed"`
4. After ALL tasks, write `handoff/build-done.json`:
```json
{
  "stage": "build-done",
  "timestamp": "<ISO 8601>",
  "completed_tasks": [1, 2, ...],
  "files_changed": ["file1.ts", "file2.ts"]
}
```

### Phase 3: Fixes Needed (Codex acts)

1. Read `handoff/review-notes.md`
2. Fix all P0 issues first, then P1, optionally P2
3. After each fix, append a `### Fix Applied` section to `review-notes.md`
4. Write `handoff/polish-done.json`:
```json
{
  "stage": "polish-done",
  "timestamp": "<ISO 8601>",
  "fixes_applied": ["P0-xxx", "P1-xxx"]
}
```

### Phase 2 & 4: Build Done / Polish Done (Claude Code acts)

Tell the user to switch to Claude Code for review.

### Phase 5: Ready to Commit (either tool)

1. Generate a conventional commit message based on spec + changes
2. Run `git add` and `git commit`
3. Write `handoff/committed.json`

## Quick Triggers

Users can bypass phase detection:
- "直接开始编码" / "just build it" — skip spec, assume plan-ready, start building
- "直接审查" / "just review" — skip build, assume build-done, start reviewing
- "查看状态" / "what phase" — only detect and report phase, do not act

## Critical Rules

- NEVER skip phases. Always check handoff files before acting.
- One tool edits code at a time. Signal files guarantee serial access.
- Spec is authority. If spec and code conflict, spec wins. Flag in review.
- `handoff/` is in `.gitignore` — never commit signal files.
- `specs/` IS committed — specs are project assets.
- Claude Code can act as Architect without this skill by placing `CLAUDE.md` in the project root (see `CLAUDE.md` in this skill directory).
