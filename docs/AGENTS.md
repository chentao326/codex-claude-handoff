# Codex Handoff — 协同工作流

本项目提供两个 Codex skills，实现基于 6 阶段状态机的 AI 编码协同。

## 两个 Skills

### `codex-claude-handoff` — Codex + Claude Code 双工具协同

- Codex 担任建造师（Builder）：编码实现、修复 Bug、编写测试
- Claude Code 担任架构师（Architect）：需求分析、任务拆解、代码审查
- 安装后，在 Codex 中说 **"交接"** 即可触发

### `codex-self-handoff` — Codex 自协同

- Codex 独自完成全部 6 阶段（Spec→Plan→Build→Review→Polish→Commit）
- 在架构师模式和建造师模式间自动切换
- 安装后，在 Codex 中说 **"自交接"** 即可触发

## 项目初始化

```bash
cd your-project
mkdir -p specs handoff
echo 'handoff/' >> .gitignore
```

## 工作流 6 阶段

```
Spec ──→ Plan ──→ Build ──→ Review ──→ Polish ──→ Commit
```

详细信息见各 skill 的 `SKILL.md` 和 `references/protocol.md`。
