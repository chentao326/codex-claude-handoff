# Codex Handoff Skills

> 两个 Codex skills，让 AI 编码工具按 6 阶段协议协同工作 —— 文件握手，零手动切换成本。

## 包含的 Skills

### 1. `codex-claude-handoff` — Codex ⇄ Claude Code 协同

Codex（建造师）+ Claude Code（架构师）双工具协作。Claude Code 负责 Spec、Plan、Review，Codex 负责 Build、Polish。通过 `handoff/` 目录中的 JSON 信号文件自动切换角色。

触发词：**交接** / **handoff** / **下一阶段** / **next phase** / **开始编码** / **开始审查**

### 2. `codex-self-handoff` — Codex 自协同

Codex 独自走完 6 阶段全流程（Spec→Plan→Build→Review→Polish→Commit），在架构师模式和建造师模式间自动切换。适合没有 Claude Code 但想要 disciplined workflow 的场景。

触发词：**自交接** / **self-handoff** / **自己走全流程** / **codex solo**

## 工作流

```
Spec ──→ Plan ──→ Build ──→ Review ──→ Polish ──→ Commit
```

两个 skill 共享相同的 6 阶段状态机和信号文件协议，区别在于角色分配。

## 安装

### 前提条件

- 已安装 [Codex](https://github.com/openai/codex) CLI
- （仅 `codex-claude-handoff`）已安装 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI

### 方式 1：通过 skill-installer 安装（推荐）

```bash
# 在 Codex 中运行
codex

# 安装 codex-claude-handoff
> 安装 skill: https://github.com/chentao326/codex-claude-handoff/tree/main/codex-claude-handoff

# 安装 codex-self-handoff
> 安装 skill: https://github.com/chentao326/codex-claude-handoff/tree/main/codex-self-handoff
```

### 方式 2：手动安装

```bash
git clone https://github.com/chentao326/codex-claude-handoff.git
cd codex-claude-handoff
bash install.sh
```

### Claude Code 配置（仅 codex-claude-handoff 需要）

```bash
# 项目级（推荐）
cp ~/.codex/skills/codex-claude-handoff/CLAUDE.md ./CLAUDE.md

# 或全局
cp ~/.codex/skills/codex-claude-handoff/CLAUDE.md ~/.claude/CLAUDE.md
```

### 项目初始化

每个要使用 skill 的项目执行一次：

```bash
cd your-project
mkdir -p specs handoff
echo 'handoff/' >> .gitignore
```

## 快速开始

### Codex + Claude Code 协同

```bash
# 1. Claude Code 设计
claude
> 交接 — 设计用户认证功能，写 spec 和 plan

# 2. Codex 编码
codex
> 交接 — 自动检测 plan-ready.json，开始编码

# 3. Claude Code 审查
claude
> 交接 — 自动检测 build-done.json，审查代码
```

### Codex 自协同

```bash
codex
> 自交接 — 设计用户认证功能，走 6 阶段全流程
```

## 信号文件状态机

```
plan-ready.json  →  Builder 编码
build-done.json  →  Architect 审查
review-passed.json → 提交
review-fixes.json →  Builder 修复
polish-done.json  →  Architect 重审
committed.json   →  完成
```

完整 Schema 见各 skill 的 `references/protocol.md`。

## 手动查相位

```bash
# codex-claude-handoff
python3 ~/.codex/skills/codex-claude-handoff/scripts/check_phase.py

# codex-self-handoff
python3 ~/.codex/skills/codex-self-handoff/scripts/check_phase.py
```

## 项目结构

```
├── README.md
├── LICENSE
├── install.sh                    # 一键安装两个 skills
├── codex-claude-handoff/         # Skill 1: Codex + Claude Code
│   ├── SKILL.md
│   ├── CLAUDE.md                 # Claude Code 配置参考
│   ├── agents/openai.yaml
│   ├── scripts/
│   │   ├── check_phase.py
│   │   └── test_check_phase.py
│   └── references/
│       └── protocol.md
├── codex-self-handoff/           # Skill 2: Codex Self
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── scripts/
│   │   ├── check_phase.py
│   │   └── test_check_phase.py
│   └── references/
│       └── protocol.md
└── docs/
    ├── QUICKSTART.md
    └── WALKTHROUGH.md
```

## 黄金规则

- **一个时间只有一个工具在改代码** — 信号文件保证串行
- **spec 是宪法** — 分歧时以 spec 为准
- **handoff/ 不入 Git** — 仅作进程内信号，specs/ 入 Git
- **说"交接"或"自交接"即可** — skill 自动处理一切
- **Codex 和 Claude 各有分工** — 不让 Codex 设计架构，不让 Claude 写实现代码

## License

MIT
