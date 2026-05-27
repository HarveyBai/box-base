# BoxBase v1.0 Week 1 Retrospective

## 时间范围

2026-05-24 ~ 2026-05-27（4 个自然日，6 个 Day 编号 = Day 1 + Day 2-3 合并 + Day 4 + Day 5 + Day 6）

## Week 1 目标 vs 实际产出

| 原计划 | 实际完成 | 状态 |
|---|---|---|
| 工程骨架 (pyproject.toml, package.json) | 后端 pyproject.toml + 前端 package.json 均落地 | ✅ |
| Linting / formatting / type checking | ruff + mypy（backend）+ ESLint + Prettier（frontend） | ✅ |
| CI/CD 流水线 (GitHub Actions) | ci.yml 含 3 个并行 job（lint-and-test / frontend-quality / secret-scan） | ✅ |
| 测试框架搭建 | pytest + pytest-asyncio + httpx（backend） | ✅ |
| Pre-commit hooks | 5 个 hook（ruff check / format check / mypy / eslint / prettier） | ✅ |
| Hello World 端点 + 测试 | /health 端点 + /docs /redoc OpenAPI 验证 | ✅ |
| 前端骨架 | Vite 8 + React 19.2 + AntD 6 + react-router-dom v7 + 登录页雏形 | ✅ |
| TruffleHog 安全扫描 | secret-scan job 接入 ci.yml | ✅ |
| 文档体系 | AGENTS.md + CONTRIBUTING.md + frontend/README.md + 6 份归档/决策文档 | ✅ |

## 技术栈最终落定

- **后端**：Python 3.12 + FastAPI + SQLAlchemy 2.0 + Pydantic v2 + uv
- **前端**：React 19.2 + Vite 8 + TypeScript 6 + Ant Design 6.4.3 + react-router-dom v7.15.1
- **数据库**：SQLite（dev）/ PostgreSQL 13+（prod）
- **工具链**：ruff + mypy + pytest + ESLint 10 Flat Config + Prettier 3.8 + pre-commit + GitHub Actions
- **包管理**：uv（Python）/ pnpm 10.33+（Node）
- **CI 防线**：pre-commit（本地 5 hook）+ GitHub Actions（云端 3 job 并行）
- **暂缓引入**：Ant Design Pro Components（延后到 Week 4-5 重评估）、TruffleHog（已接入但仅 --only-verified）

## 关键决策（按时间顺序）

1. **uv.lock 入库**（Day 2）—— 锁定依赖版本，确保所有环境一致性
2. **pre-commit local 模式 + uv run --directory**（Day 2）—— 不引入全局依赖
3. **双重防线**（Day 2-3）—— pre-commit（本地）+ GitHub Actions（云端），通过攻防演练验证有效
4. **React 18 → 19 / Vite 7 → 8 / TS 5 → 6 / ESLint 9 → 10 接受新栈**（Day 4）—— 联网核实版本全部真实存在，接受工具链默认新版
5. **Pro Components 延后到 Week 4-5**（Day 4）—— v3 仅 beta，v2 与 antd 6 peer 冲突
6. **轻量集成路线**（Day 4）—— 不用 AntD Pro 脚手架，pnpm create vite 按需引入
7. **SSH Agent Windows 双客户端 sshCommand 修复**（Day 4）—— 永久固化 git config
8. **react-router-dom v7 上车**（Day 5）—— createBrowserRouter 路由表
9. **前端 CI 合并到 ci.yml 不独立 workflow**（Day 5）—— frontend-quality job 与 backend 并行
10. **pre-commit 前端 hook 不跑 tsc**（Day 5）—— tsc 全量太慢，留到 CI job
11. **TruffleHog 接入**（Day 6）—— 独立 secret-scan job 并行，--only-verified
12. **GitHub Actions actions 主版本统一升级**（Day 6）—— checkout@v6 / setup-node@v6 / setup-uv@v8 / pnpm/action-setup@v6，根治 Node 20 deprecation

## 踩过的坑（按类别归并）

### 类别 1：环境配置

- **pre-commit 路径错误 backend/backend/**：--directory backend 已切 CWD，entry 里不能再写 backend/，改相对路径 . 和 boxbase/
- **Windows 双 SSH 客户端不共享 Agent**：ssh-add 用 Windows OpenSSH，git 默认用 Git for Windows 自带 SSH。修复：`git config --global core.sshCommand 'C:/Windows/System32/OpenSSH/ssh.exe'`
- **ssh-agent 服务需管理员 PowerShell**：`Set-Service -Name ssh-agent -StartupType Automatic`
- **PowerShell @ 字符 + CLIXML 吞 pnpm stdout**：版本号单引号包裹，装完读 package.json 验证
- **node 僵尸进程占用 5173**：Vite 漂移到 5174/5175，清理僵尸进程解决

### 类别 2：版本判断

- **AI 误判 React 19 / Vite 8 / TS 6 / ESLint 10 是幻觉**：联网核实全部真实存在，知识滞后。此后所有版本判断必须先联网
- **Pro Components v3 仅 beta 与 antd 6 不兼容**：ERR_PNPM_NO_MATCHING_VERSION，v2 锁死 antd 5。决策 Day 4 不引入
- **GitHub Actions Node 20 deprecation warning**：2026-06-02 强制切 Node 24。升级所有 actions 主版本根治

### 类别 3：流程纪律

- **Day 2-3 归档文件漏 commit**：docs/decisions/2026-0526-day2-3-archive.md 直到 Day 4 才补登
- **AI 派工提示词被拆成多段影响复制**：约定后续所有派工提示词用单个代码块整段输出
- **归档文件名日期错误**：凭"前一日 +1"直觉凑数，未核对当天实际日期。约定所有带日期文件名以 current-time 为准

### 类别 4：CI / 防线

- **故意引入错误验证 pre-commit 拦截**：3 类错误（print / type ignore / bare except），pre-commit 全拦截
- **--no-verify 绕过 + GitHub Actions 20 秒熔断验证**：CI 在云端独立运行，不受本地 --no-verify 影响，双重防线有效

## 工程纪律沉淀（给 Week 2 接班的自己）

1. **技术栈版本变更必须先报备**—— AI 工具默认装的新版本可能超预期，确认后再拍板（Day 4 教训）
2. **慎用 @ 字符在 PowerShell**—— pnpm add 版本号必须单引号包裹（Day 4 教训）
3. **pre-commit 全绿是 commit 前提**—— 5 个 hook 必须全部通过（AGENTS.md 要求）
4. **严禁 --no-verify / --force push**—— CI 是安全网的最后一道防线（Day 3 验证）
5. **ops/SECRETS.md 永久不入库**—— git status 每次 commit 前必须检查（Day 4 确定）
6. **归档文件名以 actual date 为准**—— 不准顺延 +1（Day 5 教训）
7. **backend 命令用 uv run，frontend 命令用 pnpm**—— 避免命令漂移（AGENTS.md 统一约定）
8. **验收三连**：tsc / eslint / prettier --check + pytest + pre-commit --all-files（各 Day 积累）
9. **AI 工具自由发挥要按住**—— 不在 spec 范围内的动作先问（Day 4 教训）
10. **commit message 用 Conventional Commits 英文**—— 自动化 changelog 兼容（AGENTS.md 要求）

## CI 数据

| Run # | 关联 Day | 耗时 | 状态 | 备注 |
|---|---|---|---|---|
| #1 | Day 2 | ~30s | ✅ | 首次 CI，全绿 |
| #2 | Day 3 | ~20s | ❌ | 破坏性测试，mypy 20 秒熔断 |
| #3 | Day 3 | ~30s | ✅ | 修复后恢复全绿 |
| #4 | Day 4 | 21s | ✅ | 前端骨架接入，9 步全绿 |
| #5 | Day 5 | 25s | ✅ | 前端 CI job 并行，2 deprecation warnings |
| #6 | Day 6 | pending | ⏳ | 3 job 并行 + Node 24 native |

## Week 1 时间统计

| Day | 任务 | 实际耗时 |
|---|---|---|
| Day 1（5/24） | 工程骨架 + /health TDD + AGENTS.md | ~6 小时 |
| Day 2-3（5/25-26） | uv.lock 修复 + pre-commit + CI + 攻防演练 | ~10 小时 |
| Day 4（5/27） | 前端骨架 + 工程化配置 + Git 接入 | ~8 小时 |
| Day 5（5/27 晚） | 路由化重构 + 前端 CI + pre-commit 前端 hook + README | ~4.5 小时 |
| Day 6（5/27 深夜） | deprecation 修复 + TruffleHog + 登录页 + OpenAPI + 复盘 | ~8 小时 |
| **合计** | | **~36.5 小时** |

原计划 Week 1 40 小时，实际 ~36.5 小时，节省 8.75%。

## Week 2 开门待办

1. **FastAPI Users 接入**（认证体系）—— 注册 / 登录 / Token 刷新 / 密码重置
2. **多租户数据模型设计**—— org_id + SQLAlchemy 事件监听器自动注入 WHERE org_id
3. **RBAC 实现**—— PermissionChecker 接口 + Casbin 实现
4. **前端 LoginPage 接真后端 API**—— 替换 console.log → POST /auth/login
5. **前端状态管理库决策**—— zustand / jotai / redux-toolkit 三选一
6. **测试覆盖率基线建立**—— pytest-cov + vitest，目标整体 ≥80%
7. **前端 CI 加 pnpm build**—— 当前 ci.yml 仅 tsc + eslint + prettier，未含 build
8. **Pro Components v3 重新评估**—— Week 4-5，但 Week 2 可开始关注转正进展

## References

- [../docs/decisions/2026-0526-day1-archive.md](../docs/decisions/2026-0526-day1-archive.md) —— Day 1 工作记忆
- [../docs/decisions/2026-0526-day2-3-archive.md](../docs/decisions/2026-0526-day2-3-archive.md) —— Day 2-3 工作记忆
- [../docs/decisions/2026-0527-day4-archive.md](../docs/decisions/2026-0527-day4-archive.md) —— Day 4 工作记忆
- [../docs/decisions/2026-0527-day4-tech-stack-update.md](../docs/decisions/2026-0527-day4-tech-stack-update.md) —— 技术栈选型决策
- [../docs/decisions/2026-0527-day5-archive.md](../docs/decisions/2026-0527-day5-archive.md) —— Day 5 工作记忆
- [../docs/decisions/2026-0527-day6-archive.md](../docs/decisions/2026-0527-day6-archive.md) —— Day 6 工作记忆
- [../AGENTS.md](../AGENTS.md) —— AI 工具协作规则
- [../frontend/README.md](../frontend/README.md) —— 前端工程文档
- [../CONTRIBUTING.md](../CONTRIBUTING.md) —— 贡献指南
