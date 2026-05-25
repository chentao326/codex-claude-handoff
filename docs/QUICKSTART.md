# Codex + Claude Code 一分钟上手

## 三个命令记住全流程

```bash
# 1. 用 Claude 设计 (在项目目录下)
claude
> 帮我设计 [功能名]，写 specs/[功能名].md 并生成 handoff/plan-ready.json

# 2. 用 Codex 实现 (同目录，Claude 结束后)
codex
> 读取 specs/ 和 handoff/plan-ready.json，逐项实现，写 handoff/build-done.json

# 3. 用 Claude 审查 (Codex 结束后)
claude
> 审查 git diff，对照 spec 检查，写 handoff/review-notes.md
```

## 状态机速记

```
plan-ready.json  →  Codex 开始编码
build-done.json  →  Claude 开始审查
review-passed.json → 可以提交了
review-fixes.json →  切回 Codex 修
polish-done.json  →  再跑一次 Review
```

## 一句话规则

> **Claude 想，Codex 做，文件握手，Git 交接。**
