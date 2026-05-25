# 完整演练：用 Codex + Claude Code 开发「用户认证」功能

下面模拟一条真实需求的完整生命周期。你可以照着在终端里操作一遍。

---

## 准备：项目初始化

```bash
mkdir my-project && cd my-project
git init
mkdir -p specs handoff
echo "handoff/" >> .gitignore
cp /path/to/AGENTS.md ./
```

---

## 阶段 1: Spec — Claude Code

打开终端，启动 Claude Code：

```bash
cd my-project
claude
```

在 Claude Code 中输入：

```
我需要做一个用户认证功能。请帮我写需求规格文档，
输出到 specs/user-auth.md。

要求覆盖：
- 用户故事
- 验收条件
- 技术约束（用 Express + TypeScript + Prisma）
- 边界情况
```

Claude Code 输出示例：

```markdown
# specs/user-auth.md

## 用户故事
- 作为新用户，我希望能用邮箱和密码注册
- 作为已注册用户，我希望能登录获取 token
- 作为登录用户，我希望能访问受保护的 API

## 验收条件
- [ ] POST /api/auth/register 接收 email + password，返回 user + token
- [ ] POST /api/auth/login 接收 email + password，返回 user + token
- [ ] GET /api/me 需要 Bearer token，返回当前用户信息
- [ ] 密码至少 8 位，邮箱格式校验
- [ ] 重复邮箱注册返回 409
- [ ] 错误密码返回 401

## 技术约束
- Runtime: Node.js + Express + TypeScript
- ORM: Prisma
- 密码: bcrypt 哈希
- Token: JWT (HS256)
- 错误响应格式: { error: { code, message } }
```

---

## 阶段 2: Plan — Claude Code

继续在 Claude Code 中：

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

退出 Claude Code，切换终端。

---

## 阶段 3: Build — Codex

```bash
cd my-project
codex
```

在 Codex 中输入：

```
读取 specs/user-auth.md 和 handoff/plan-ready.json，
按任务清单逐一实现。

每完成一个任务，更新 handoff/plan-ready.json 中
该任务的状态为 completed。

全部完成后写入 handoff/build-done.json。
```

Codex 执行过程：

1. 读取 spec，理解需求
2. 读取 plan-ready.json，获取任务列表
3. 任务 1: 编辑 `prisma/schema.prisma`，添加 User 模型，运行 `npx prisma migrate dev`
4. 更新 plan-ready.json，任务 1 status → completed
5. 任务 2: 创建 `src/routes/auth.ts` + `src/validators/auth.ts`
6. 更新 plan-ready.json，任务 2 status → completed
7. 任务 3: 实现登录路由
8. ...以此类推
9. 全部完成后，生成 `handoff/build-done.json`:

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

## 阶段 4: Review — Claude Code

切回 Claude Code：

```bash
claude
```

```
审查当前未提交的代码变更（git diff）。

对照 specs/user-auth.md 的验收条件逐条检查：

1. 注册端点是否完整
2. 登录端点是否正确
3. 错误处理是否规范
4. 密码是否哈希存储
5. 测试是否覆盖边界情况
6. 代码风格是否符合项目惯例

结果写入 handoff/review-notes.md，按 P0/P1/P2 分级。

如果有 P0 问题，写 handoff/review-fixes.json 并列出修复项。
如果全部通过，写 handoff/review-passed.json。
```

Claude Code 输出 `handoff/review-notes.md`:

```markdown
# Review Notes: user-auth

## P0 - 阻断（必须修）
- 无

## P1 - 建议修
- `src/routes/auth.ts:42`: 注册成功后应返回 201 而非 200
- `src/middleware/auth.ts:15`: JWT 过期未处理，token 过期时返回 500 而非 401

## P2 - 风格
- `tests/auth.test.ts`: 测试用例缺少 describe 嵌套分组
- `src/validators/auth.ts:8`: 邮箱正则过于宽松，建议用更严格格式
```

生成了 `handoff/review-fixes.json`:

```json
{
  "stage": "review-fixes",
  "has_p0": false,
  "fixes": ["review-notes.md#P1", "review-notes.md#P2"]
}
```

---

## 阶段 5: Polish — Codex

切回 Codex：

```bash
codex
```

```
读取 handoff/review-notes.md，逐条修复 P1 和 P2 问题。

修复方式写入 review-notes.md 每条后面（用 #### 修复 小节）。

完成后写 handoff/polish-done.json。
```

Codex 修复完成，写入:

```json
{
  "stage": "polish-done",
  "timestamp": "2026-05-25T11:45:00+08:00",
  "fixes_applied": ["P1-201-status", "P1-jwt-expiry", "P2-test-grouping", "P2-email-regex"]
}
```

---

## 循环 Review（可选）

切回 Claude Code：

```
重新审查修复后的代码。
```

如果通过，写 `handoff/review-passed.json`。

---

## 阶段 6: Commit

用任一工具：

```
根据 spec 和变更内容，生成规范的 commit message 并提交。
```

生成结果：

```
feat(auth): add user registration, login, and JWT auth middleware

- Add User model with bcrypt password hashing (Prisma)
- POST /api/auth/register with email/password validation
- POST /api/auth/login returning JWT token
- JWT auth middleware with expiry handling
- GET /api/me protected route
- Integration tests covering all endpoints

Closes #42
```

---

## 关键技巧总结

| 技巧 | 说明 |
|------|------|
| **先写 spec，再拆任务** | 两个工具都读同一份 spec，不会理解偏差 |
| **handoff 文件就是握手信号** | 不看终端输出，看文件是否存在 |
| **状态机驱动** | plan-ready → build-done → review-passed → committed |
| **review 循环可多次** | review → polish → review → polish → ... 直到通过 |
| **遇到分歧暂停** | Build 时发现 spec 不可行 → 写 spec-issue.md → 切回 Claude |

---

## 一行命令快速体验

```bash
# 终端 1: Claude Code 写 spec + plan
cd my-project && claude
# > 帮我设计 XXX 功能，写 spec 和 plan-ready.json

# 等 Claude 完成后，终端 1: Codex 编码
codex
# > 读取 spec 和 plan，逐项实现，写完写 build-done.json

# 终端 1: Claude Code 审查
claude
# > 审查 diff，写 review-notes.md
```

所有工作都在同一个终端窗口切换完成，无需多开。
