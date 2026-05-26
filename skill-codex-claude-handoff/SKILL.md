---
name: codex-claude-handoff
description: |
  Codex + Claude Code collaborative handoff protocol. Automates the 6-phase workflow
  (Spec→Plan→Build→Review→Polish→Commit) between the two tools. Use when the user
  mentions "handoff", "交接", "下一阶段", "next phase", "开始编码", "start build",
  "开始审查", "start review", "协同", "collaborate", "Codex和Claude", "切换工具",
  or when a handoff/*.json signal file exists in the project.
---

# Codex + Claude Code Handoff Skill

You are operating in a collaborative workflow with another AI coding tool.
Read the project's `handoff/` directory to determine the current phase and proceed.

## Role Definition

| Tool | You Are | Core Responsibility |
|------|---------|---------------------|
| **Codex** | 建造师 (Builder) | Execute coding tasks, fix bugs, write tests |
| **Claude Code** | 架构师 (Architect) | Design, plan, review, spec writing |

If you are Codex: DO NOT design architecture or write specs. Execute the plan.
If you are Claude Code: DO NOT write implementation code unless reviewing/planning.

## Phase Detection

Run this command to detect the current phase:

```bash
ls handoff/*.json 2>/dev/null | tail -1 | xargs cat 2>/dev/null || echo "NO_HANDOFF_DIR"
```

Determine phase by checking file existence in order:

| Signal File Exists | Phase | Your Action |
|-------------------|-------|-------------|
| (none) | Phase 0: Init | Claude Code writes spec. Codex asks user to run Claude first. |
| `plan-ready.json` | Phase 1: Plan Ready | **Codex**: read spec + plan, build all tasks, mark complete, write `build-done.json`. **Claude**: wait, your job is done for now. |
| `build-done.json` | Phase 2: Build Done | **Claude Code**: review git diff against spec, write `review-notes.md` + `review-passed.json` or `review-fixes.json`. **Codex**: wait. |
| `review-fixes.json` | Phase 3: Fixes Needed | **Codex**: read `review-notes.md`, fix issues, write `polish-done.json`. **Claude**: wait. |
| `review-passed.json` | Phase 4: Ready to Commit | Either tool: generate commit message and commit. Write `committed.json`. |
| `polish-done.json` (no `review-passed.json`) | Phase 3b: Re-review | **Claude Code**: re-review the fixes, write `review-passed.json` or `review-fixes.json`. |
| `committed.json` | Done | Announce completion. |

## Phase-Specific Instructions

### If you are Codex and phase is "Plan Ready"

1. Read `specs/` directory for the feature spec
2. Read `handoff/plan-ready.json` for the task list
3. Execute tasks in dependency order
4. After EACH task, update `plan-ready.json`: set that task's status to `"completed"`
5. After ALL tasks, write `handoff/build-done.json`:
```json
{
  "stage": "build-done",
  "timestamp": "<ISO 8601>",
  "completed_tasks": [1, 2, ...],
  "files_changed": ["file1.ts", "file2.ts"]
}
```

### If you are Claude Code and phase is "Build Done"

1. Run `git diff --stat` and `git diff` to see all changes
2. Read the spec from `specs/`
3. Check each acceptance criterion against the implementation
4. Write `handoff/review-notes.md` with issues graded P0/P1/P2
5. If no P0 issues: write `handoff/review-passed.json`
6. If P0 issues exist: write `handoff/review-fixes.json`

### If you are Codex and phase is "Fixes Needed"

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

### If phase is "Ready to Commit"

1. Generate a conventional commit message based on spec + changes
2. Run the commit
3. Write `handoff/committed.json`

## Critical Rules

- **NEVER skip phases**: always check handoff files before acting
- **One tool at a time**: if a phase belongs to the other tool, stop and tell the user
- **Spec is authority**: if spec and code conflict, spec wins; flag it in review
- **handoff/ is NOT committed**: the directory is in .gitignore
- **specs/ IS committed**: specs are project assets

## Quick Triggers

Users can short-circuit phase detection with these phrases:
- "直接开始编码" / "just build it" → skip spec, assume plan-ready, start building
- "直接审查" / "just review" → skip build, assume build-done, start reviewing
- "查看状态" / "what phase" → only detect and report phase, don't act
