# Handoff Protocol Reference

## State Machine

```
[Init] ──Claude──→ [plan-ready] ──Codex──→ [build-done]
                                                 │
                                          ┌──────┴──────┐
                                          ↓              ↓
                                   [review-passed]  [review-fixes]
                                          │              │
                                          ↓              ↓
                                      [Commit]    ──Codex──→ [polish-done]
                                                               │
                                                         ┌─────┴─────┐
                                                         ↓           ↓
                                                  [review-passed] [review-fixes]
```

## Signal File Schemas

All files are JSON. Timestamps in ISO 8601 with timezone.

### plan-ready.json
```json
{
  "feature": "string",
  "stage": "plan-ready",
  "timestamp": "ISO8601",
  "spec_file": "string",
  "task_count": "number",
  "tasks": [
    {
      "id": "number",
      "desc": "string",
      "files": ["string"],
      "status": "pending | completed",
      "depends_on": ["number"]
    }
  ]
}
```

### build-done.json
```json
{
  "stage": "build-done",
  "timestamp": "ISO8601",
  "completed_tasks": ["number"],
  "files_changed": ["string"],
  "notes": "string (optional)"
}
```

### review-notes.md (Markdown, not JSON)
```markdown
# Review Notes: <feature>

## P0 - Blocking
- `file:line`: issue description

## P1 - Should Fix
- `file:line`: issue description

## P2 - Style
- `file:line`: issue description
```

### review-passed.json
```json
{
  "stage": "review-passed",
  "timestamp": "ISO8601",
  "reviewer": "claude-code"
}
```

### review-fixes.json
```json
{
  "stage": "review-fixes",
  "timestamp": "ISO8601",
  "has_p0": "boolean",
  "fixes": ["string references to review-notes.md sections"]
}
```

### polish-done.json
```json
{
  "stage": "polish-done",
  "timestamp": "ISO8601",
  "fixes_applied": ["string"]
}
```

### committed.json
```json
{
  "stage": "committed",
  "timestamp": "ISO8601",
  "commit_hash": "string",
  "commit_message": "string"
}
```
