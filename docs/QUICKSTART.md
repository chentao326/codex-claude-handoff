# Codex Handoff 一分钟上手

## Codex + Claude Code 协同

```bash
# 1. 用 Claude Code 设计
claude
> 帮我设计 [功能名]，写 specs/[功能名].md 并生成 handoff/plan-ready.json

# 2. 用 Codex 实现
codex
> 交接 — 自动检测 plan-ready.json，逐项实现

# 3. 用 Claude Code 审查
claude
> 交接 — 审查 git diff，写 review-notes.md
```

## Codex 自协同

```bash
codex
> 自交接 — 设计并实现 [功能名]，走 6 阶段全流程
```

## 状态机速记

```
plan-ready.json  →  Builder 开始编码
build-done.json  →  Architect 开始审查
review-passed.json → 可以提交了
review-fixes.json →  切回 Builder 修复
polish-done.json  →  Architect 重审
```

## 一句话规则

> **文件握手，Git 交接，说"交接"或"自交接"即可。**
