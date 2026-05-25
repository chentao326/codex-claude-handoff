# Codex + Claude Code 协同工作流

## 角色分工

| 角色 | 工具 | 核心职责 |
|------|------|---------|
| **架构师** | Claude Code | 需求分析、架构设计、任务拆解、Code Review、测试策略 |
| **建造师** | Codex | 功能实现、Bug 修复、重构执行、测试编写、文档生成 |

**原则**: 同一时间只有一个工具在修改代码。通过 Git commit 和 handoff 文件完成交接。

---

## 工作流六阶段

```
Spec ──→ Plan ──→ Build ──→ Review ──→ Polish ──→ Commit
 CC        CC       Codex      CC         Codex      任一
```

### 阶段 1: Spec（需求澄清）— Claude Code
- 输入: 用户需求描述
- 输出: `specs/<feature-name>.md`
- 产物: 用户故事、验收条件、边界约束、影响范围

### 阶段 2: Plan（任务拆解）— Claude Code
- 输入: `specs/<feature-name>.md`
- 输出: `specs/<feature-name>.md`（追加任务清单）
- 产物: 分步骤任务列表，每个任务标注优先级、预估复杂度、依赖关系
- 最后写入: `handoff/plan-ready.json`（交接信号）

### 阶段 3: Build（编码实现）— Codex
- 输入: `specs/<feature-name>.md` + `handoff/plan-ready.json`
- 行为: 按任务清单逐项实现
- 每完成一个任务，更新 `handoff/plan-ready.json` 中的状态
- 全部完成后写入: `handoff/build-done.json`

### 阶段 4: Review（代码审查）— Claude Code
- 输入: `git diff` + `specs/<feature-name>.md`
- 输出: `handoff/review-notes.md`
- 产物: 问题分级（P0 阻断 / P1 建议 / P2 风格）
- 通过则写入: `handoff/review-passed.json`
- 有问题则写入: `handoff/review-fixes.json`

### 阶段 5: Polish（修复打磨）— Codex
- 输入: `handoff/review-fixes.json` + `handoff/review-notes.md`
- 行为: 逐条修复 review 问题，每条标注修复方式
- 完成后写入: `handoff/polish-done.json`
- 可循环回阶段 4

### 阶段 6: Commit（提交）— 任一工具
- 条件: `handoff/review-passed.json` 存在 且 `handoff/polish-done.json` 存在（或未触发修复）
- 行为: 生成规范 commit message，提交代码
- 写入: `handoff/committed.json`

---

## 交接协议

### 目录结构
```
project/
├── AGENTS.md                  # 本文件
├── specs/                     # 需求规格（只增不改）
│   └── <feature-name>.md
├── handoff/                   # 交接信号文件（.gitignore）
│   ├── plan-ready.json        # Claude → Codex: 计划就绪
│   ├── build-done.json        # Codex → Claude: 编码完成
│   ├── review-notes.md        # Claude → Codex: 审查意见
│   ├── review-passed.json     # Claude: 审查通过
│   ├── review-fixes.json      # Claude → Codex: 需要修复
│   ├── polish-done.json       # Codex → Claude: 修复完成
│   └── committed.json         # 最终: 已提交
└── .gitignore                 # 包含 handoff/
```

### 信号文件格式

```json
// handoff/plan-ready.json
{
  "feature": "add-user-auth",
  "stage": "plan-ready",
  "timestamp": "2026-05-25T10:30:00+08:00",
  "spec_file": "specs/add-user-auth.md",
  "task_count": 5,
  "tasks": [
    {"id": 1, "desc": "创建 User model", "status": "pending", "files": ["src/models/user.ts"]},
    {"id": 2, "desc": "实现注册接口", "status": "pending", "files": ["src/routes/auth.ts"]},
    {"id": 3, "desc": "实现登录接口", "status": "pending", "files": ["src/routes/auth.ts"]},
    {"id": 4, "desc": "添加 JWT 中间件", "status": "pending", "files": ["src/middleware/auth.ts"]},
    {"id": 5, "desc": "编写集成测试", "status": "pending", "files": ["tests/auth.test.ts"]}
  ]
}
```

### `.gitignore` 配置
```
handoff/
```

---

## 使用场景速查

### 场景 A: 新功能开发（标准全流程）
```
$ claude    # 启动 Claude Code
> 帮我设计用户认证功能，写到 specs/user-auth.md

> 拆成任务清单，生成 handoff/plan-ready.json

$ codex     # 启动 Codex
> 读取 specs/user-auth.md，按 handoff/plan-ready.json 逐项实现

$ claude    # 切回 Claude Code
> 审查 git diff，输出 review-notes.md

$ codex     # 切回 Codex
> 根据 review-notes.md 修复问题

$ codex     # 提交（或让 Claude 提交）
> 生成 commit message 并提交
```

### 场景 B: Bug 修复（快速模式）
```
# 更适合 Codex 直接处理
$ codex
> 读取 issue 描述/错误日志，定位并修复，提交

# 如有必要，让 Claude 审查
$ claude
> 审查刚才的修复是否引入新问题
```

### 场景 C: 重构（重型模式）
```
$ claude
> 分析现有代码，设计重构方案，写 specs/refactor-xxx.md

$ codex
> 按方案逐步重构，每一步跑测试确保通过
```

---

## 黄金规则

1. **同一时间只有一个工具在编辑代码** — 通过 handoff 文件确保串行
2. **handoff/ 不入 Git** — 加入 .gitignore，仅作进程内信号
3. **specs/ 入 Git** — 需求文档是项目资产，版本控制
4. **每阶段结束必须写信号文件** — 这是两个工具之间唯一的握手方式
5. **Claude Code 偏重思考，Codex 偏重执行** — 不要反过来让 Codex 设计架构
6. **遇到分歧以 spec 为准** — 如果 Build 阶段发现 spec 不合理，暂停并写 handoff/spec-issue.md，切回 Claude
