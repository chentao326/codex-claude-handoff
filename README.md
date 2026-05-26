# Codex ⇄ Claude Code Handoff

> 让 Codex（OpenAI）和 Claude Code（Anthropic）在同一个项目里自动协同 —— 一个设计，一个编码，文件握手，零手动切换成本。

## 为什么需要这个？

Codex 和 Claude Code 各有优势：Claude Code 擅长架构设计和代码审查，Codex 擅长快速编码和执行。但它们没有原生协作机制 —— 你只能手动判断"现在该用哪个"、"该读什么文件"。

这个 skill 提供了一套 **6 阶段状态机 + 文件握手协议**，让两个工具自动感知当前阶段并执行对应动作。

## 工作流

```
Spec ──→ Plan ──→ Build ──→ Review ──→ Polish ──→ Commit
Claude    Claude    Codex     Claude      Codex      任一
```

## 安装

### 前提条件

- 已安装 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- 已安装 [Codex](https://github.com/openai/codex) CLI
- 两个工具都能在你的项目目录下正常工作

### 一键安装

```bash
# 克隆仓库
git clone https://github.com/chentao326/codex-claude-handoff.git
cd codex-claude-handoff

# 安装 skill（自动部署到 Codex 和 Claude Code）
cd skill-codex-claude-handoff && bash install.sh
```

安装脚本会做三件事：

1. **Codex**：复制 `SKILL.md`、`references/`、`scripts/`、`agents/`、`CLAUDE.md` 到 `~/.codex/skills/codex-claude-handoff/`
2. **Claude Code**：输出配置指引（手动操作）
3. **项目初始化**：输出目录初始化指引

### 为 Claude Code 配置（二选一）

**方案 A — 项目级**（推荐，每个项目独立配置）：

```bash
cp ~/.codex/skills/codex-claude-handoff/CLAUDE.md ./CLAUDE.md
```

**方案 B — 全局**（所有项目生效）：

```bash
cp ~/.codex/skills/codex-claude-handoff/CLAUDE.md ~/.claude/CLAUDE.md
```

### 项目初始化

每个要使用该 skill 的项目，执行一次：

```bash
cd your-project
mkdir -p specs handoff
echo 'handoff/' >> .gitignore
cp ~/.codex/skills/codex-claude-handoff/docs/AGENTS.md ./AGENTS.md
```

## 快速开始

```bash
# 1. Claude Code 写设计
claude
> 交接 — 设计用户认证功能

# 2. Codex 编码
codex
> 交接 — 自动检测 plan-ready.json，开始编码

# 3. Claude Code 审查
claude
> 交接 — 自动检测 build-done.json，开始审查
```

只需说 **"交接"**，工具自动判断当前阶段。

## 详细教程

### 场景 1：新功能开发（标准全流程）

以「用户认证」功能为例，逐步演示。

---

#### Step 1: 启动 Claude Code，写 Spec

```bash
cd my-project
claude
```

在 Claude Code 中输入：

```
我需要做一个用户认证功能。请帮我写需求规格文档到 specs/user-auth.md。

要求：
- 用户故事（注册、登录、Token 刷新）
- 验收条件（可勾选的 checklist）
- 技术约束（Express + TypeScript + Prisma）
- 边界情况（重复注册、错误密码、过期 Token）
```

Claude Code 会输出 `specs/user-auth.md`，内容类似：

```markdown
# 用户认证功能

## 用户故事
- 作为新用户，我希望能用邮箱和密码注册
- 作为已注册用户，我希望能登录获取 Token
- 作为登录用户，我希望能访问受保护的 API

## 验收条件
- [ ] POST /api/auth/register 接收 email + password，返回 user + token
- [ ] POST /api/auth/login 接收 email + password，返回 user + token
- [ ] GET /api/me 需要 Bearer token，返回当前用户信息
- [ ] 密码至少 8 位，邮箱格式校验
- [ ] 重复邮箱注册返回 409，错误密码返回 401

## 技术约束
- Runtime: Node.js + Express + TypeScript
- ORM: Prisma，密码: bcrypt 哈希
- Token: JWT (HS256)

## 边界情况
- 空请求体、超长密码、SQL 注入尝试
```

---

#### Step 2: 继续 Claude Code，拆任务写 Plan

在同一个 Claude Code 会话中继续：

```
基于 specs/user-auth.md，拆解成编码任务，
生成 handoff/plan-ready.json。按依赖排序。
```

Claude Code 生成 `handoff/plan-ready.json`：

```json
{
  "feature": "user-auth",
  "stage": "plan-ready",
  "timestamp": "2026-05-25T10:30:00+08:00",
  "spec_file": "specs/user-auth.md",
  "task_count": 5,
  "tasks": [
    {
      "id": 1,
      "desc": "更新 Prisma schema，添加 User 模型，运行迁移",
      "files": ["prisma/schema.prisma"],
      "status": "pending",
      "depends_on": []
    },
    {
      "id": 2,
      "desc": "实现 POST /api/auth/register 路由 + 验证逻辑",
      "files": ["src/routes/auth.ts", "src/validators/auth.ts"],
      "status": "pending",
      "depends_on": [1]
    },
    {
      "id": 3,
      "desc": "实现 POST /api/auth/login 路由",
      "files": ["src/routes/auth.ts"],
      "status": "pending",
      "depends_on": [1, 2]
    },
    {
      "id": 4,
      "desc": "实现 JWT 认证中间件 + GET /api/me 路由",
      "files": ["src/middleware/auth.ts", "src/routes/auth.ts"],
      "status": "pending",
      "depends_on": [2, 3]
    },
    {
      "id": 5,
      "desc": "编写集成测试覆盖所有端点",
      "files": ["tests/auth.test.ts"],
      "status": "pending",
      "depends_on": [2, 3, 4]
    }
  ]
}
```

退出 Claude Code。

---

#### Step 3: 启动 Codex，编码实现

```bash
codex
```

```
交接
```

Codex 检测到 `plan-ready.json`，自动进入 Build 阶段：

1. 读取 `specs/user-auth.md`，理解需求
2. 读取 `handoff/plan-ready.json`，获取任务列表
3. 按依赖顺序执行：任务 1 → 2 → 3 → 4 → 5
4. 每完成一个任务，更新 `plan-ready.json` 中对应任务状态为 `"completed"`
5. 全部完成后，写入 `handoff/build-done.json`：

```json
{
  "stage": "build-done",
  "timestamp": "2026-05-25T11:15:00+08:00",
  "completed_tasks": [1, 2, 3, 4, 5],
  "files_changed": [
    "prisma/schema.prisma",
    "src/routes/auth.ts",
    "src/validators/auth.ts",
    "src/middleware/auth.ts",
    "tests/auth.test.ts"
  ]
}
```

---

#### Step 4: 切回 Claude Code，代码审查

```bash
claude
```

```
交接
```

Claude Code 检测到 `build-done.json`，自动进入 Review 阶段：

1. 运行 `git diff` 查看所有变更
2. 对照 `specs/user-auth.md` 的验收条件逐条检查
3. 检查密码是否哈希、错误处理是否规范、是否有安全漏洞
4. 生成 `handoff/review-notes.md`：

```markdown
# Review Notes: user-auth

## P0 - 阻断（必须修）
- 无

## P1 - 建议修
- `src/routes/auth.ts:42`: 注册成功后应返回 201 而非 200
- `src/middleware/auth.ts:15`: JWT 过期时返回 500 而非 401

## P2 - 风格
- `tests/auth.test.ts`: 缺少 describe 嵌套分组
```

5. 因为有 P1 问题，写入 `handoff/review-fixes.json`

---

#### Step 5: 切回 Codex，修复问题

```bash
codex
```

```
交接
```

Codex 检测到 `review-fixes.json`，进入 Polish 阶段：

1. 读取 `handoff/review-notes.md`
2. 逐条修复 P1、P2 问题
3. 完成后写入 `handoff/polish-done.json`

---

#### Step 6: 切回 Claude Code，最终确认

```bash
claude
```

```
交接
```

Claude Code 检测到 `polish-done.json`，重新审查修复后的代码。如果通过，写入 `handoff/review-passed.json`。

---

#### Step 7: 提交代码

任一工具执行：

```
交接
```

检测到 `review-passed.json`，生成规范 commit message 并提交：

```
feat(auth): add user registration, login, and JWT auth middleware

- Add User model with bcrypt password hashing (Prisma)
- POST /api/auth/register with email/password validation
- POST /api/auth/login returning JWT token
- JWT auth middleware with expiry handling
- GET /api/me protected route
- Integration tests covering all endpoints
```

---

### 场景 2：Bug 修复（快速模式）

适合 Codex 直接处理的简单修复：

```bash
codex
```

```
帮我修复登录超时没返回 401 的问题，直接改不用走全流程。
```

如果是复杂 bug（涉及多个模块），建议走正常 Review 流程：

```bash
claude
> 分析这个 bug 的根因，写修复方案到 specs/bug-login-timeout.md

codex
> 交接 — 按方案修复
```

---

### 场景 3：重构（重型模式）

重构风险高，建议完整走六阶段：

```bash
claude
> 分析 src/services/ 的耦合问题，设计重构方案，写 specs/refactor-services.md

claude
> 拆解任务，生成 handoff/plan-ready.json

codex
> 交接 — 逐步重构，每一步跑测试确保通过

claude
> 交接 — 审查重构结果，确保行为不变
```

---

### 场景 4：紧急跳过某阶段

如果明确知道当前阶段，可以直接说：

| 短语 | 效果 |
|------|------|
| "直接开始编码" / "just build it" | 跳过 Spec/Plan，假设 plan-ready，直接 Build |
| "直接审查" / "just review" | 跳过 Build，假设 build-done，直接 Review |
| "查看状态" / "what phase" | 只检测并报告当前阶段，不执行任何操作 |

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

## 手动查相位

```bash
# 详细 JSON 输出
python3 ~/.codex/skills/codex-claude-handoff/scripts/check_phase.py

# 只输出相位名
python3 ~/.codex/skills/codex-claude-handoff/scripts/check_phase.py --plain

# 指定 handoff 目录
python3 ~/.codex/skills/codex-claude-handoff/scripts/check_phase.py --handoff-dir /path/to/project/handoff
```

## 完整信号文件参考

所有文件都是 JSON 格式。完整 Schema 见 [references/protocol.md](skill-codex-claude-handoff/references/protocol.md)。

| 文件 | 写入者 | 含义 | 下一个阶段 |
|------|--------|------|-----------|
| `plan-ready.json` | Claude | 计划和任务清单已就绪 | Codex 编码 |
| `build-done.json` | Codex | 编码完成，已列出变更文件 | Claude 审查 |
| `review-notes.md` | Claude | 审查意见（P0/P1/P2 分级） | — |
| `review-passed.json` | Claude | 审查通过，可以提交 | 提交代码 |
| `review-fixes.json` | Claude | 有阻断问题，需要修复 | Codex 修复 |
| `polish-done.json` | Codex | 修复完成 | Claude 重审 |
| `committed.json` | 任一 | 代码已提交 | 流程结束 |

## 项目结构

```
skill-codex-claude-handoff/
├── SKILL.md              # Codex skill 定义
├── CLAUDE.md             # Claude Code 等效配置
├── install.sh            # 一键安装
├── agents/openai.yaml    # UI 元数据
├── references/protocol.md # 协议详细参考（含完整 Schema）
├── scripts/
│   ├── check_phase.py    # 相位检测脚本
│   └── test_check_phase.py # 单元测试
├── docs/
│   ├── AGENTS.md         # 协同规范（可放入项目根目录）
│   ├── WALKTHROUGH.md    # 完整演练示例
│   └── QUICKSTART.md     # 一分钟速查
├── README.md
└── .gitignore
```

## 排错

### "交接"没有触发 skill

- 确认 `~/.codex/skills/codex-claude-handoff/SKILL.md` 存在
- 确认项目目录下有 `handoff/` 目录，或包含信号文件
- 对于 Claude Code：确认 `CLAUDE.md` 已复制到项目根目录或 `~/.claude/`

### 相位检测显示 "init"

- 如果项目还没有 `handoff/` 目录：从 Claude Code 开始，先写 spec
- 如果 `handoff/` 目录存在但为空：删除目录，从 Claude Code 重新开始

### 工具进入了错误的阶段

- 删除 `handoff/` 中最新的信号文件，手动回到上一阶段
- 或运行 `check_phase.py` 确认当前相位

### 两个工具同时操作导致冲突

- 黄金规则：同一时间只有一个工具在编辑代码
- 如果发生冲突，以 `handoff/` 中最新的信号文件为准
- `git stash` 保存当前修改，按信号文件指示的相位重新开始

## 黄金规则

- **一个时间只有一个工具在改代码** — 信号文件保证串行
- **spec 是宪法** — 分歧时以 spec 为准
- **handoff/ 不入 Git** — 仅作进程内信号，specs/ 入 Git
- **说"交接"就好** — skill 自动处理一切
- **Claude 想，Codex 做** — 不要让 Codex 设计架构，不要让 Claude 写大量实现代码

## License

MIT
