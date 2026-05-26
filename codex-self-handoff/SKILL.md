---
name: codex-self-handoff
description: Codex self-collaboration handoff protocol. Enforces a disciplined 6-phase workflow (Spec→Plan→Build→Review→Polish→Commit) where Codex acts as both Architect and Builder with file-based signal handshakes. Use when the user mentions "self-handoff", "自交接", "自己走全流程", "self workflow", "codex solo", "独自完成", "自审查", or when a handoff/*.json signal file exists and the user wants single-tool discipline.
---

# Codex Self Handoff

## Overview

Enable Codex to follow a disciplined 6-phase workflow entirely on its own. Codex switches between Architect mode (design, plan, review) and Builder mode (implement, fix). Signal files in `handoff/` enforce phase discipline and prevent skipping steps.

## Workflow

```
Spec ──→ Plan ──→ Build ──→ Review ──→ Polish ──→ Commit
Architect Architect Builder  Architect   Builder    任一
```

All roles are filled by Codex. The signal files enforce that you complete each phase before moving to the next.

## Phase Detection

Always detect the current phase before acting:

```bash
python3 <skill_dir>/scripts/check_phase.py
```

| Signal File | Phase | Mode | Action |
|------------|-------|------|--------|
| (none) | Init | Architect | Write spec to `specs/<feature>.md`, then write `handoff/plan-ready.json` |
| `plan-ready.json` | Plan Ready | — | Tell user plan is ready. Proceed only when user confirms. |
| `build-done.json` | Build Done | Architect | Review `git diff` against spec. Write `review-notes.md` + `review-passed.json` or `review-fixes.json` |
| `review-fixes.json` | Fixes Needed | Builder | Fix issues from `review-notes.md`, write `polish-done.json` |
| `polish-done.json` | Polish Done | Architect | Re-review fixes. Write `review-passed.json` or `review-fixes.json` |
| `review-passed.json` | Ready | Builder | Generate commit message and commit. Write `committed.json` |
| `committed.json` | Done | — | Announce completion. |

Full signal file schemas: `references/protocol.md`.

## Mode Switching

You switch between two modes depending on the current phase:

### Architect Mode
- Design specs and write acceptance criteria
- Decompose features into ordered tasks with dependencies
- Review code against specs
- Grade issues P0 (blocking) / P1 (should fix) / P2 (style)
- Do NOT write implementation code in this mode

### Builder Mode
- Execute tasks from `plan-ready.json` in dependency order
- Fix issues from `review-notes.md` by priority
- Write implementation code, tests, and documentation
- Do NOT redesign architecture or rewrite specs in this mode

## Phase Instructions

### Phase 0: Init (Architect mode)

1. Write spec to `specs/<feature-name>.md` with:
   - User stories
   - Acceptance criteria (checkbox format)
   - Technical constraints
   - Edge cases
2. After spec, decompose into `handoff/plan-ready.json`:
```json
{
  "feature": "name",
  "stage": "plan-ready",
  "timestamp": "<ISO8601>",
  "spec_file": "specs/<name>.md",
  "task_count": 3,
  "tasks": [
    {"id": 1, "desc": "...", "files": ["..."], "status": "pending", "depends_on": []}
  ]
}
```
3. Tell user: "Plan ready. Say '开始编码' to proceed with build."

### Phase 1: Plan Ready → Build (Builder mode, on user confirmation)

Do NOT auto-start building. After user confirms:
1. Read spec from `specs/` and tasks from `handoff/plan-ready.json`
2. Execute tasks in dependency order
3. After each task, update `plan-ready.json`: set `status` to `"completed"`
4. After all tasks, write `handoff/build-done.json`:
```json
{
  "stage": "build-done",
  "timestamp": "<ISO 8601>",
  "completed_tasks": [1, 2, ...],
  "files_changed": ["file1.ts", "file2.ts"]
}
```

### Phase 2: Build Done → Review (Architect mode)

1. Run `git diff --stat` then `git diff`
2. Read spec from `specs/`
3. Check each acceptance criterion
4. Write `handoff/review-notes.md`:
```markdown
# Review Notes: <feature>
## P0 - Blocking
- `file:line`: issue
## P1 - Should Fix
- `file:line`: issue
## P2 - Style
- `file:line`: issue
```
5. No P0 → `handoff/review-passed.json`. Has P0 → `handoff/review-fixes.json`.

### Phase 3: Fixes Needed → Polish (Builder mode)

1. Read `handoff/review-notes.md`
2. Fix all P0 first, then P1, optionally P2
3. Write `handoff/polish-done.json`:
```json
{
  "stage": "polish-done",
  "timestamp": "<ISO 8601>",
  "fixes_applied": ["P0-xxx", "P1-xxx"]
}
```

### Phase 5: Ready to Commit (Builder mode)

1. Generate a conventional commit message
2. Run `git add` and `git commit`
3. Write `handoff/committed.json`

## Quick Triggers

- "自交接" / "self-handoff" / "自己走全流程" — start full 6-phase workflow from Init
- "直接开始编码" / "just build it" — skip to Build phase (assume plan-ready)
- "直接审查" / "just review" — skip to Review phase (assume build-done)
- "查看状态" / "what phase" — only detect and report phase, do not act

## Critical Rules

- NEVER skip phases. Always check handoff files before acting.
- Switch modes explicitly. Do not design in Builder mode, do not code in Architect mode.
- Spec is authority. If spec and code conflict, spec wins.
- `handoff/` is in `.gitignore` — never commit signal files.
- `specs/` IS committed — specs are project assets.
- After writing a signal file, re-check the phase to confirm state transition.
