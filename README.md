# Codex ⇄ Claude Code Handoff

> 让 Codex（OpenAI）和 Claude Code（Anthropic）在同一个项目里自动协同 —— 一个设计，一个编码，文件握手，零手动切换成本。

## 为什么需要这个？

Codex 和 Claude Code 各有优势：Claude Code 擅长架构设计和代码审查，Codex 擅长快速编码和执行。但它们没有原生协作机制 —— 你只能手动判断"现在该用哪个"、"该读什么文件"。

这个 skill 提供了一套**6 阶段状态机 + 文件握手协议**，让两个工具自动感知当前阶段并执行对应动作。

## 工作流

```
Spec ──→ Plan ──→ Build ──→ Review ──→ Polish ──→ Commit
Claude    Claude    Codex     Claude      Codex      任一
```

## 快速开始

```bash
# 1. 安装 skill（同时装到 Codex 和 Claude Code）
cd skill-codex-claude-handoff && bash install.sh

# 2. 在项目里初始化
mkdir -p specs handoff && echo 'handoff/' >> .gitignore

# 3. Claude Code 写设计
claude
> 交接 — 设计用户认证功能

# 4. Codex 编码
codex
> 交接 — 自动检测 plan-ready.json，开始编码

# 5. Claude Code 审查
claude
> 交接 — 自动检测 build-done.json，开始审查
```

只需说"交接"，工具自动判断当前阶段。

## 怎么做到的？

项目 `handoff/` 目录里是一串 JSON 信号文件，构成状态机：

```
plan-ready.json  →  Codex 开始编码
build-done.json  →  Claude 开始审查
review-passed.json → 准备提交
review-fixes.json →  Codex 修复问题
polish-done.json  →  再跑一次审查
committed.json   →  完成
```

每完成一个阶段，工具写入下一个信号文件。另一个工具启动时读取信号文件，就知道该做什么。

## 项目结构

```
skill-codex-claude-handoff/
├── SKILL.md              # Codex skill 定义
├── CLAUDE.md             # Claude Code 等效配置
├── install.sh            # 一键安装
├── agents/openai.yaml    # UI 元数据
├── references/protocol.md # 协议详细参考
├── scripts/check_phase.py # 相位检测脚本
├── docs/
│   ├── AGENTS.md         # 协同规范（可放入项目根目录）
│   ├── WALKTHROUGH.md    # 完整演练示例
│   └── QUICKSTART.md     # 一分钟速查
├── README.md
└── .gitignore
```

## 手动查相位

```bash
python3 ~/.codex/skills/codex-claude-handoff/scripts/check_phase.py
```

## 黄金规则

- **一个时间只有一个工具在改代码** — 信号文件保证串行
- **spec 是宪法** — 分歧时以 spec 为准
- **handoff/ 不入 Git** — 仅作进程内信号，specs/ 入 Git
- **说"交接"就好** — skill 自动处理一切

## License

MIT
