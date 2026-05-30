# BoxBase v1.0 工作记忆摘要 — Week 2 Day 2 收官（滚动累积版）

## 1. 对话主题与用户意图

- **项目**：BoxBase v1.0 —— 轻量级、模块化 Python 多租户 SaaS 框架
- **用户角色**：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收拍板；本地 AI IDE（Cursor / Claude Code / CodeBuddy）执行代码；会话内 AI 任顾问，只出决策建议/派工提示词/验收清单
- **本次会话核心任务**：Week 2 Day 2 全部 9 个切片落地 —— Alembic 异步基础设施 + 8 张业务表 ORM + security 模块 + seed 脚本 + pytest-cov 覆盖率门禁，21/21 绿、双覆盖率门禁 PASS
- **开发周期**：16 周完成 v1.0；当前 Week 2 Day 2（2026-05-30 23:00 开工，2026-05-31 00:04 收尾）
- **本次会话重大收获**：架构落地完整闭环（评审→ORM→service→test→CI 门禁）；建立 pytest-cov 模块路径规范、alembic 模板 import 规范、本地 AI IDE 自查修正纪律；切片 9 二次补丁后实现全局 96% / security 100%
- **历史阶段**：Week 1 全闭环（基线 dadf307、tag week1-complete @ 07ee750、CI Run #14 全绿）→ Week 2 Day 1 架构评审全部决策点拍板（设计文档 + Day 1 归档）→ Week 2 Day 2 代码全落地（本归档）

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| —— Week 2 Day 2（本次会话）—— | |
| 今天算 Day 1 还是 Day 2？ | Day 2 正式开工，文件命名按 2026-05-30 |
| 推进方式？ | 逐片推进，从切片 1（Alembic baseline）起 |
| DB URL 配置放哪？ | 引入最小 backend/boxbase/config.py，pydantic-settings 管理；切片 1 先立 database_url |
| pydantic-settings 何时装？ | 切片 1 一并装，不推迟 |
| 迁移目录单库还是多环境？ | 单目录 backend/alembic/，SQLite/PG 通过 config 切换 URL |
| async 模式 + SQLite WAL？ | 全链路 async（SQLAlchemy async engine + aiosqlite/asyncpg）；SQLite 启用 WAL + foreign_keys |
| 切片 1 装哪 4 包？版本？ | alembic 1.18.4 / pydantic-settings 2.14.1 / aiosqlite 0.22.1 / asyncpg 0.31.0（PyPI JSON API 核实） |
| ORM Base 放哪？ | backend/boxbase/models/ 目录，每张表一文件，__init__.py 统一导出 |
| AuditMixin created_by/updated_by 类型？ | Uuid 类型（SQLAlchemy 2.0 原生，与主键一致） |
| deleted_at 过滤逻辑何时建？ | 切片 2 只建字段，统一过滤逻辑放切片 6 |
| Membership 唯一约束实现？ | 数据库级 UniqueConstraint("tenant_id", "user_id") |
| is_default 每用户至多一条 active 约束？ | 应用层保证（seed/service 层），数据库不建约束 |
| 关联表是否继承 AuditMixin？ | 是，4 张关联表全部继承（8 列：id + tenant_id + 2FK + 5 审计） |
| 4 张关联表分文件还是合文件？ | 各一个文件（role.py / permission.py / membership_role.py / role_permission.py） |
| RefreshToken jti 存 hash 还是明文？ | 明文 UUID 字符串（"明文不落库"特指 token 原文，jti 作为索引键需落库） |
| tenant 强制过滤实现方式？ | ORM with_loader_criteria + 依赖注入（显式注入，易测试易审计） |
| 请求上下文载体？ | 自定义 RequestContext dataclass 通过 FastAPI Depends 传递 |
| 切片 6 文件边界？ | 新建 backend/boxbase/dependencies.py 存放基础依赖；切片 7 get_current_user 接入同一文件 |
| superadmin_username / token 有效期？ | 写进 config.py 可配置（access_token_expire_minutes=30 / refresh_token_expire_days=7） |
| get_current_user session 注入？ | 通过 Depends(get_db) 注入；参数名 db（非 session）|
| seed 脚本放哪？ | backend/boxbase/tools/seed.py，uv run python -m boxbase.tools.seed 手动触发 |
| 默认权限集？ | 5 个 code：user:read / user:write / role:read / role:write / role:assign |
| 默认角色？ | 3 个：owner / admin / member |
| 系统租户？ | slug=system, name=BoxBase System, is_system=True |
| seed 执行方式？ | asyncio.run(main()) 包裹 |
| pytest-cov 门禁何时加 CI？ | 切片 9 同步改 CI 加门禁 |
| 首批单测范围？ | security 核心（hash/JWT/rotation/get_current_user 三路径）+ ORM filter helper |
| .env 是否入库？ | 是，作为演示配置入库（SUPERADMIN_USERNAME=superadmin），方便新人直接开发调试 |
| CI 文件路径？ | .github/workflows/ci.yml |
| seed.py 覆盖率怎么处理？ | omit = ["boxbase/tools/*"]，排除出覆盖率统计避免 0% 拖累全局 |
| get_current_user 测试深度？ | 补 3 条路径：超管 short-circuit / 有 membership 放行 / 无 membership 抛 403 |
| pytest-cov 路径写法？ | 必须用 Python 模块路径（--cov=boxbase.security），不能用文件系统路径（boxbase/security）|
| —— Week 2 Day 1（历史累积）—— | |
| 多租户隔离选哪种？ | Row-level + tenant_id；RLS 第二防线 Week 2 不启用，预留 hook |
| 超管设计？ | break-glass：配置文件注入 superadmin username；归属系统保留租户；请求上下文层集中 short-circuit |
| 角色作用域？ | tenant-scoped（Role 带 tenant_id）；每租户 seed 默认角色；超管 short-circuit 不进 RBAC |
| RBAC 用几张表？ | 简化三表 + resource:action；权限 seed 固定；对象级所有权放 service 层 |
| 未来"同部门读"怎么办？ | 三层访问控制模型：①租户隔离(ORM) ②RBAC(角色) ③对象级/关系级(service 层) |
| 认证库选哪个？ | DIY 薄层（pyjwt + pwdlib + FastAPI 原生依赖注入）；fastapi-users 15.0.5 已维护模式 / authx 1.6.0 Beta |
| refresh token 策略？ | 方案 C 存库可撤销：jti 白名单 + rotation + logout 真吊销；access ≤30min 窗口；可平滑升级即时吊销 |
| username/email 唯一性？ | 全局唯一（User 全局实体，去 tenant_id；经 membership 加入多租户；token 带 active_tenant_id） |
| department 放哪？ | 不放 User；v1.0 不建表；未来方向通用 group + membership_groups 多对多挂 membership 层 |
| 内置默认租户与系统保留租户？ | 同一条 TENANT（is_system=true，Q-A）|
| 注册行为？ | 不自动登录、不自动建组织；默认加入内置租户；强制赋默认 member 角色 |
| 审计字段？ | 公共 Mixin 五字段；软删 deleted_at 与 ORM 过滤联动 |
| —— Week 1（历史累积）—— | |
| uv.lock 为何提交？ | 锁定依赖版本，uv 最佳实践 |
| GitHub Actions 能拦 --no-verify？ | 能，CI 云端独立 20 秒内熔断 |
| 前端为何不走 AntD Pro 脚手架？ | pnpm create vite 干净项目 + 按需引入；Pro Components v3 仅 beta 延后 Week 4-5 |
| Vite proxy 前缀？ | 前端 /api/* → 后端 8000 不 rewrite，因后端也统一 /api，dev/prod 路径一致 |
| 归档命名规范？ | 日期+任务主题（Day 5 立）；日期以 current-time 为准 |

## 3. 文件与引用内容索引（含历史累积）

### Week 2 Day 2 产出（切片 1-9，本次会话）

| 文件 | 路径 | 说明 |
|---|---|---|
| Alembic 配置 | backend/alembic.ini | ASCII 注释，encoding=utf-8（中文注释会 GBK 解码失败）|
| Alembic env.py | backend/alembic/env.py | 全链路 async，run_async_migrations() 范例 |
| Alembic 模板 | backend/alembic/script.py.mako | 含 op/sa import，避免 autogenerate NameError |
| baseline 迁移 | backend/alembic/versions/b845e3107bf8_baseline.py | 空 pass，revision b845e3107bf8（2026-05-30 22:21:14）|
| 后续迁移 5 条 | backend/alembic/versions/ | 切片 2-5 autogenerate，8 张表全部落库 |
| config.py | backend/boxbase/config.py | pydantic-settings；database_url / secret_key / superadmin_username / access_token_expire_minutes=30 / refresh_token_expire_days=7 |
| database.py | backend/boxbase/database.py | async engine + session factory；SQLite WAL + foreign_keys=ON 注入 |
| AuditMixin | backend/boxbase/models/base.py | 5 字段（created_at/updated_at/created_by/updated_by/deleted_at）；DeclarativeBase |
| user.py | backend/boxbase/models/user.py | 全局唯一（username/email/phone 单列唯一）；phone nullable |
| tenant.py | backend/boxbase/models/tenant.py | slug 全局唯一索引；is_system 标记 |
| membership.py | backend/boxbase/models/membership.py | UniqueConstraint(tenant_id, user_id)；is_default / status |
| role.py | backend/boxbase/models/role.py | tenant-scoped，UniqueConstraint(tenant_id, name) |
| permission.py | backend/boxbase/models/permission.py | tenant-scoped，UniqueConstraint(tenant_id, code) |
| membership_role.py | backend/boxbase/models/membership_role.py | 关联表 + AuditMixin |
| role_permission.py | backend/boxbase/models/role_permission.py | 关联表 + AuditMixin |
| refresh_token.py | backend/boxbase/models/refresh_token.py | jti 明文 UUID 唯一索引；status active/revoked |
| models __init__ | backend/boxbase/models/__init__.py | 统一导出 8 张表 |
| dependencies.py | backend/boxbase/dependencies.py | RequestContext dataclass；get_db；apply_tenant_filter / apply_soft_delete_filter（with_loader_criteria）|
| security.py | backend/boxbase/security.py | hash/verify(argon2)；create/decode access+refresh(HS256)；rotation；get_current_user（含 active membership 校验 + superadmin short-circuit）；覆盖率 100% |
| seed.py | backend/boxbase/tools/seed.py | 系统租户 + superadmin + 3 角色/5 权限 + 默认 member；幂等（[+]→[=]）；140 行；omit 出覆盖率 |
| conftest.py | backend/tests/conftest.py | pytest async fixture；内存 SQLite db_session |
| test_security.py | backend/tests/test_security.py | 21 条：hash/JWT/rotation/decode 异常分支/get_current_user 三路径 |
| ci.yml | .github/workflows/ci.yml | 覆盖率门禁：全局 --cov-fail-under=80 / security --cov=boxbase.security --cov-fail-under=95（必须 Python 模块路径）|
| .env | backend/.env | 演示配置 SUPERADMIN_USERNAME=superadmin，入库 |
| pyproject.toml | backend/pyproject.toml | 新增 7 包依赖 + [tool.coverage.run] omit=["boxbase/tools/*"] + [tool.pytest.ini_options] asyncio_mode=auto |

### Week 2 Day 1 产出

| 文件 | 路径 | 说明 |
|---|---|---|
| 设计评审文档 | docs/architecture/2026-W2-auth-tenant-rbac-design.md | Day 2 唯一蓝图，10 章；ER/字段/API/Day2 预案完整 |
| Day 1 归档 | docs/decisions/2026-0530-week2-day1-auth-design-review.md | Week 2 Day 1 滚动累积版 |

### 后端（Week 1 产物，dadf307）

| 文件 | 路径 | 说明 |
|---|---|---|
| main.py | backend/boxbase/ | FastAPI app；APIRouter(prefix='/api')；openapi/docs/redoc 均挂 /api |
| test_health.py / test_openapi.py | backend/tests/ | /api/health + /api/openapi.json/docs/redoc 共 4 用例 |
| .pre-commit-config.yaml | 根目录 | 5 hook：ruff check / ruff format / mypy / frontend-eslint / frontend-prettier |
| ci.yml | .github/workflows/ | 3 job：lint-and-test / Frontend Lint & Typecheck / Secret Scan(TruffleHog) |
| pyproject.toml | backend/ | uv 管理，Python 3.12 |
| AGENTS.md | 根目录 | 跨工具 AI 规则单一真相源；含 API Routing Convention |
| SECRETS.md | ops/ | 敏感备忘，.gitignore 工具级隔离，永不入库 |

### 前端（Week 1 产物）

| 文件 | 路径 | 说明 |
|---|---|---|
| package.json | frontend/ | antd 6.4.3 / icons 6.2.3 / react 19.2 / react-router-dom v7 / vite 8 / typescript 6 / eslint 10 / prettier 3.8 |
| vite.config.ts | frontend/ | port 5173；proxy /api → localhost:8000 不 rewrite |
| api/health.ts | frontend/src/api/ | fetchHealth() 类型对齐后端 |
| HomePage.tsx | frontend/src/pages/ | Hello World + Card 三态；AntD v6 Alert 用 title |

### 决策与归档历史

| 文件 | 路径 | 说明 |
|---|---|---|
| 2026-0529-api-health-integration.md | docs/decisions/ | Day 5 收官归档 |
| 2026-W1-retrospective.md | docs/retrospectives/ | Week 1 全景复盘 |

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| PyPI JSON API（本次） | 核实 7 个依赖包最新版本 | alembic 1.18.4 / pydantic-settings 2.14.1 / aiosqlite 0.22.1 / asyncpg 0.31.0 / pwdlib 0.3.0 / PyJWT 2.13.0 / pytest-cov 7.1.0 / coverage 7.14.1 |
| alembic revision（本次） | 生成迁移文件 | baseline(b845e3107bf8) + 5 次 autogenerate，8 张表全部落库 |
| alembic upgrade/downgrade（本次） | 实跑迁移验证 | 全部成功，往返通路完整 |
| sqlite3（本次） | 验证 DB 状态 | 8 张表 + alembic_version 表存在 |
| pytest（本次） | 回归测试 | 4/4 → 15/15 → 21/21 全绿 |
| pytest-cov（本次） | 覆盖率统计 | 首次跑 60%/80% 不达标 → 补丁后 全局 96% / security.py 100%，双门禁 PASS |
| ruff check --fix / ruff format（本次） | 代码质量 | 每次 commit 前自动修复 import 排序/格式化，pre-commit 全过 |
| git add/commit（本次） | 版本控制 | Day 2 新增 12 条 commit 全部入链，pre-commit 三关全过 |
| web_search / web_fetch（Day 1）| 认证库联网核实 | fastapi-users 15.0.5 维护模式；authx 1.6.0 Beta；WorkOS 2026 横评 |
| git/GitHub Actions（Week 1）| 版本控制+CI | 基线 dadf307；tag week1-complete @ 07ee750；Run #14 全绿 24s |
| pre-commit/pytest/前端三连（Week 1）| 验收 | pre-commit 5/5；前端 tsc/eslint/prettier exitCode 0 |
| mise（Week 1）| 运行时管理 | 2026.5.15，node@22.22.3（Active LTS），替代 fnm |

## 5. 决策与结论（含历史累积）

### Week 2 Day 2 技术决策（本次会话）

1. **全链路 async**：SQLAlchemy async engine + aiosqlite(dev)/asyncpg(prod)；SQLite WAL + foreign_keys 注入
2. **Alembic**：单目录 + async env.py + 空 baseline；script.py.mako 模板含 op/sa import
3. **ORM 结构**：models/ 目录每表一文件；AuditMixin 5 字段 Uuid 类型；关联表继承 AuditMixin（8 列）
4. **Membership 唯一约束**：DB 级 UniqueConstraint(tenant_id, user_id)；is_default 应用层保证
5. **RefreshToken**：jti 明文 UUID 唯一索引（token 原文不落库，jti 作索引必落库）
6. **依赖注入**：RequestContext dataclass + FastAPI Depends；apply_tenant_filter / apply_soft_delete_filter 用 with_loader_criteria 显式注入
7. **security 模块**：独立 backend/boxbase/security.py；get_current_user 超管 short-circuit + active membership 双校验；rotation 撤销旧 jti
8. **配置化**：superadmin_username / access_token_expire_minutes=30 / refresh_token_expire_days=7 写进 config.py
9. **seed 幂等**：系统租户(slug=system,is_system=True) + superadmin + 3 角色(owner/admin/member) + 5 权限(user:read/write, role:read/write/assign) + 默认 member；14 条 [+]→[=]
10. **覆盖率门禁**：全局 ≥80%（实际 96%）/ security ≥95%（实际 100%）；seed.py omit；pytest-cov 必须用 Python 模块路径
11. **​.env 入库**：作为演示配置入库（SUPERADMIN_USERNAME=superadmin），方便新人开发调试
12. **测试范围**：21 条 — hash/verify、JWT 签发/解码/过期/篡改/类型不符、rotation、get_current_user 超管/有 membership/无 membership 三路径、ORM filter helper

### Week 2 Day 1 架构决策（长期有效）

1. **D2 隔离**：Row-level + tenant_id；RLS 第二防线 Week 2 不启用、预留 hook
2. **超管**：配置注入 superadmin username；系统保留租户；请求上下文层 short-circuit
3. **D4 角色**：tenant-scoped；每租户 seed 默认角色；超管硬编码全通过
4. **D3 RBAC**：简化三表 + resource:action；权限 seed 固定；对象级放 service 层；三层访问控制模型
5. **D1 认证库**：DIY 薄层（pyjwt+pwdlib+FastAPI 依赖注入），独立 security 模块；fastapi-users/authx 保留为候选
6. **D5/D6**：pwdlib[argon2] / pyjwt[crypto]；HS256，RS256 延后
7. **D7 refresh**：方案C 存库可撤销，jti 白名单 + rotation；access ≤30min 窗口；可平滑升级即时吊销
8. **D8/D9/D10**：Alembic Day 2 首件 / 覆盖率分层 80%/95% CI 强制 / /api/admin/* 走 short-circuit
9. **全局用户模型**：User 全局唯一(username/email/phone 单列唯一)；MEMBERSHIP 核心关联表；角色挂 membership；token 带 active_tenant_id
10. **部门归位**：v1.0 不建表；部门=租户内 group 挂 membership 层；未来通用 group + membership_groups
11. **Q-A~Q-E**：系统/默认租户合并一条(is_system) / membership 强制默认 member / switch-tenant(P2) / phone nullable 全局唯一 / membership 加 is_default
12. **审计字段**：公共 Mixin 五字段；软删 deleted_at 与 ORM 过滤联动

### 工程化决策（Week 1，长期有效）

1. pre-commit local repo 模式 + uv run --directory backend；CI setup-uv + uv sync
2. 双重防线：pre-commit(本地) + GitHub Actions(云端)
3. 前端栈：React 19.2 + Vite 8 + TS 6 + AntD v6；Pro Components 延后 Week 4-5；pnpm 10.33
4. 运行时 mise(scoop 装)管 Node 22；SECRETS.md 走 .gitignore 工具级隔离
5. 后端所有路由统一 /api 前缀；Vite proxy 不 rewrite，dev/prod 一致

## 6. 错误与修正（含历史累积）

| 错误/偏差 | 发现时机 | 修正 |
|---|---|---|
| 本次：派工提示词散落多段 | 用户质问（切片 1）| 重做为一整块可复制 markdown |
| 本次：alembic.ini 含中文注释 | alembic revision 报 GBK 解码失败 | 去掉中文注释只用 ASCII（Windows encoding="locale" 限制）|
| 本次：script.py.mako 模板缺 op/sa import | 切片 2 autogenerate 后 NameError | 修复迁移文件 + 更新模板（始终包含 op/sa import）|
| 本次：迁移文件 import 顺序不符 ruff | 每次 commit pre-commit 拦截 | ruff check --fix + ruff format 自动修复 |
| 本次：CI 覆盖率路径用文件系统路径 | pytest-cov "Module never imported" | 改 Python 模块路径（--cov=boxbase.security）|
| 本次：全局覆盖率 60% 不达 80% 门禁 | 切片 9 STOP 2 | seed.py omit 后 96% PASS |
| 本次：security.py 80% 不达 95% 门禁 | 切片 9 STOP 2 | 补 6 条用例（decode 异常 3 + get_current_user 三路径 3）→ 100% |
| 本次：测试调用 session= 但函数参数名是 db | 本地 AI IDE 自查 | 主动改为 db=db_session 并汇报（建立纪律：明确 bug 直接修不等顾问）|
| 本次：顾问擅自启动写归档任务 | 用户质问 | 守纪律 — 等用户明确指示再写 |
| Day 1：草案 w2-day1.txt 落后当前进度 | 顾问核对 | 列硬伤，对齐后再用 |
| Day 1：AI 草图用"租户内唯一"User 模型 | 用户纠正 | 重构全局唯一 + membership |
| Day 1：AI 把 department_id 放 USER 表 | 用户纠正 | 移除；部门归位 membership 层，v1.0 不建 |
| Day 1：AI 文档写完才抛 Q-A~Q-E | 用户批评 | 立纪律：写文档前先问全再动笔 |
| Day 1：首版归档未滚动累积（只写当天）| 用户察觉变短 | 重做合规滚动累积版 |
| 历史：误判 React19/Vite8/TS6/ESLint10 为幻觉 | 用户截图反驳 | 版本判断必先联网核实 |
| 历史：ssh-add 可见但 push 仍要 passphrase | push 报错 | git config core.sshCommand 永久固化 |
| 历史：mise 装完 cmd 找不到 node | mise doctor shims_on_path:no | 手动写 User PATH |
| 历史：PowerShell CLIXML 吞 stdout | install 卡住 | mise 迁移后根治；CLIXML 黑名单 |
| 历史：Day 5 顾问越界用 browser_task_tool 建空仓库 | 用户质问 | 明文写入角色边界规约 |

## 7. 讨论演变（文字描述）

会话开门：用户提供 Day 1 两份归档（Day 1 归档 + 设计评审文档）同步上下文 → 顾问复述同步点 + 确认 Day 1 架构主干已拍板 → 询问今天是 Day 1 还是 Day 2 → 用户确认 Day 2 正式开工 + 逐片推进。

切片 1（Alembic 基础设施）：顾问出 3 个微决策询问（config.py 载体 / pydantic-settings 时机 / 单目录） → 用户全部确认 → 用户补充全链路 async + SQLite WAL 要求 → 顾问评估影响面 → 询问 database.py 是否本片建 → 用户确认 → 顾问出完整派工（第一版散落多段被用户纠正，重做为一整块） → 本地 AI IDE 执行 STOP 1（PyPI 核实 4 版本号） → STOP 2（7 文件写入 + uv sync）→ 提交。

切片 2-5（ORM 模型）：按依赖顺序逐片推进，关键决策一次过（AuditMixin Uuid / Membership UniqueConstraint / 关联表继承 AuditMixin / RefreshToken jti 明文）。中途修复 script.py.mako 模板 NameError 与 ruff import 排序问题。每片 autogenerate 迁移 + upgrade 验证 + commit。

切片 6-7（依赖注入 + security）：建 RequestContext + apply_tenant_filter/apply_soft_delete_filter（with_loader_criteria 显式注入） → security 模块（hash/JWT/rotation/get_current_user）；config.py 追加 superadmin_username + token 有效期字段。

切片 8（seed）：系统租户 + superadmin + 3 角色/5 权限/默认 member 幂等脚本，14 条 [+] → 14 条 [=] 验证幂等。用户主动决策 .env 演示配置入库（方便新人调试，避免拉下仓库无法直接开发）。

切片 9（覆盖率门禁）：首次跑暴露两问题 — CI 路径 bug（用了文件系统路径）+ 全局 60%/security 80% 双未达标 → 拍决策：seed.py omit + 补 6 条 security 用例（decode 异常 3 条 + get_current_user 三路径 3 条）→ 本地 AI IDE STOP 1 自查发现测试用 session= 但函数参数名是 db，主动修正并汇报（建立"明确 bug 直接修不等顾问"纪律）→ STOP 2 全部 PASS（21/21 绿、全局 96%、security 100%）→ commit e09ab0d 收官。

收尾：顾问首次擅自启动写归档任务被用户质问"没守纪律"+ 输出格式不符（未单代码块）→ 顾问承认偏差、等用户明确指示 → 用户给定归档提示词 → 顾问按规范输出本归档。

## 8. 当前状态与后续步骤

### Git 状态

- 最新 commit：e09ab0d（test: add coverage gates and security test cases (slice-9)）
- Day 2 提交链（12 条）：
  - 35c53b7 docs: add Week 2 Day 1 auth/tenant/RBAC design review and archive
  - fc03a72 chore: init project structure for Week 2 Day 2
  - df7c4e7 feat: add alembic async infrastructure and database setup (slice-1)
  - 5e08dae feat: add audit mixin user tenant ORM models and migration (slice-2)
  - c5f1d9c feat: add membership ORM model and migration (slice-3)
  - c654724 feat: add role permission membership-role role-permission ORM and migration (slice-4)
  - 33300ca feat: add refresh-token ORM model and migration (slice-5)
  - 8d058ff feat: add request context tenant filter soft-delete filter dependencies (slice-6)
  - e2494ba feat: add security module jwt get-current-user rotation (slice-7)
  - 841d775 feat: add seed script for system tenant superadmin roles permissions (slice-8)
  - 970000e chore: track backend/.env as demo config for onboarding
  - e09ab0d test: add coverage gates and security test cases (slice-9)
- 待提交：本归档（docs/decisions/2026-0530-week2-day2-slice1-9-complete.md），由本地 AI IDE 一并提交保持仓库干净
- 建议 commit message：docs: add Week 2 Day 2 complete archive (slice 1-9)

### Completed

- Week 1 全部闭环（dadf307，tag week1-complete @ 07ee750）
- Week 2 Day 1：认证+多租户+RBAC 架构主干全部决策点闭环；设计评审文档落地
- Week 2 Day 2：9 个切片全部落地，21/21 绿，覆盖率双门禁 PASS（全局 96% / security 100%）

### Next Steps（Week 2 Day 3，新会话）

- **新会话同时提供本归档 + 设计文档两份**（docs/architecture/2026-W2-auth-tenant-rbac-design.md）
- **新会话 AI 开场先复述同步点 + 确认角色边界 + 等用户明确放行才写派工/文档**
- **Day 3 核心任务**：实现 ≥17 个 API 端点（设计文档章节 5）+ 集成测试 + 安全场景测试
  - P0：/api/auth/register / login / refresh / logout / /api/users/me
  - P1：/api/auth/tenants / /api/users GET+POST / /api/memberships PATCH / /api/roles GET+POST+permissions / /api/admin/tenants
  - P2：/api/auth/switch-tenant / /api/memberships DELETE / /api/permissions / /api/admin/users
- **待 Day 3 确认的微决策**（顾问开场询问）：
  - router 文件拆分方式（auth/users/roles 分文件 vs 合文件）
  - 错误响应 schema 统一格式（FastAPI HTTPException vs 自定义 ErrorResponse）
  - Pydantic request/response schema 目录（schemas/ vs 各模块内联）
  - service 层是否独立目录（services/ vs 端点函数内联）
- **待 Day 2 复核继承到 Day 3**：系统/默认租户合并 seed 唯一性、is_default 唯一约束实现、switch-tenant 是否 rotation 旧 refresh

### 技术栈备忘（最新）

- **后端**：FastAPI + SQLAlchemy 2.0 async + Pydantic v2 + uv（Python 3.12）；统一 /api 前缀
- **已装依赖**：alembic 1.18.4 / pydantic-settings 2.14.1 / aiosqlite 0.22.1 / asyncpg 0.31.0 / pwdlib 0.3.0 / PyJWT 2.13.0 / pytest-cov 7.1.0 / coverage 7.14.1
- **隔离**：Row-level + tenant_id；ORM with_loader_criteria 强制过滤（tenant + deleted_at）
- **认证**：DIY security 模块；HS256；refresh 存库可撤销 + rotation；access 30min / refresh 7d
- **前端**：Node 22.22.3(mise) + React 19.2 + Vite 8 + TS 6 + AntD 6.4.3 + react-router-dom v7
- **数据库**：SQLite(dev) / PostgreSQL(prod)；Alembic 双环境迁移一致
- **工具链**：ruff + mypy + pytest + pytest-cov + ESLint 10 + Prettier 3.8 + pre-commit + GitHub Actions + TruffleHog；mise 2026.5.15
- **覆盖率**：全局 96%（门禁 80%）/ security.py 100%（门禁 95%）；seed.py omit
- **CI 文件路径**：.github/workflows/ci.yml

### 工程纪律（含历史累积）

1. 顾问只出决策建议/派工提示词/验收清单；不粘源码、不进 Agent Mode、不调 browser_task_tool
2. 写文档/派工前先把待确认项问全，用户拍完再动笔；不得事后补问题
3. **未经用户明确指示，不得擅自启动归档/派工提示词写作任务**（本次会话强化）
4. 归档输出必须严格按提示词规范：单个 markdown 代码块、不嵌套代码块、代码块外只输出一句使用说明（本次会话强化）
5. 设计文档/归档由顾问写完整内容（markdown），本地 AI IDE 只存文件 + commit，不创作
6. commit 前本地 AI IDE 执行 git status --short 列出文件给用户确认；保持仓库干净
7. 版本号必须联网核实并贴实际字符串；技术栈版本变更先报备
8. 带日期文件名以 current-time 为准（不凭直觉顺延）
9. 归档为滚动替换式：合并历史 + 本次，老内容压缩成结论/纪律，新会话只读这一份
10. 派工提示词必须一整块可复制 markdown，不得散落多段
11. 严禁 --no-verify / --force push / 自动 prettier --write 不经确认
12. **pytest-cov 路径必须用 Python 模块路径（--cov=boxbase.security），不能用文件系统路径**（本次会话立）
13. **alembic.ini 注释必须用 ASCII**（Windows encoding="locale" 会 GBK 解码失败）（本次会话立）
14. **script.py.mako 模板必须包含 op/sa import 块**（否则 autogenerate 生成的迁移缺 import 报 NameError）（本次会话立）
15. **本地 AI IDE 自查发现明确 bug（如参数名不符）应直接修正并汇报，不需等顾问指示**（本次会话立）
16. PowerShell CLIXML 黑名单（Select-String/ConvertFrom-Json 等输出可能被吞）；mise 迁移后已根治
17. 修复 deprecation warning（如 AntD message→title）属合理范围；改 props 语义需停下确认
