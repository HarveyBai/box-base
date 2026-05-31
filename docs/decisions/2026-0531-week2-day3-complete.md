# BoxBase v1.0 工作记忆摘要 — Week 2 Day 3 收官（滚动累积版）

## 1. 对话主题与用户意图

- 项目：BoxBase v1.0 —— 轻量级、模块化 Python 多租户 SaaS 框架
- 用户角色：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收拍板；本地 AI IDE（Cursor / Claude Code / CodeBuddy）执行代码；会话内 AI 任顾问，只出决策建议/派工提示词/验收清单
- 本次会话核心任务：Week 2 Day 3 —— 平台架构重构（core/ + zones/ 模块化）+ admin zone 17 个 API 端点 + demo zone 示例 + 集成与安全测试 + 双覆盖率门禁，61/61 绿、全局 93.83% / security 100%
- 开发周期：16 周完成 v1.0；当前 Week 2 Day 3（2026-05-31）
- 本次会话重大收获：确立 core/+zones/ 模块化架构规范并落地架构规范文档；完成 admin zone 全部 17 个端点 + demo 示例模块；定位并修复 coverage.py 异步追踪配置（concurrency 配置）；建立"对外唯一 router.py / service.py 入口"模块契约
- 历史阶段：Week 1 全闭环（基线 dadf307、tag week1-complete @ 07ee750、CI Run #14 全绿）→ Week 2 Day 1 架构评审拍板 → Week 2 Day 2 ORM/security/seed 落地（21/21 绿）→ Week 2 Day 3 架构重构 + API 全落地（本归档）

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| —— Week 2 Day 3（本次会话）—— | |
| 目录按层切还是按模块切？ | 垂直切分（Zone 方案）：core/ 全局基础设施 + zones/ 业务模块；标准 Python 大型项目惯例 |
| models 归模块还是全局？ | 归模块自身（zones/<module>/models/）；后期扩展模块各自带 model 才能自洽 |
| 8 张基础表归哪？ | 全部归 zones/admin/，admin 作为平台内核模块承载基础管理数据 |
| AuditMixin 放哪？ | core/base.py（所有模块 model 都要继承的基础设施，不属于 admin 业务）|
| 全局共享内容放哪？ | boxbase/core/（base/config/database/dependencies/exceptions/security/router）|
| 路由总入口怎么设计？ | core/router.py 聚合各模块；main.py 极简只做 app 初始化 |
| 模块对外接口契约？ | 每模块对外暴露唯一 router.py + service.py；端点 >8 拆 routers/ 子目录；service 函数 >10 拆 services/ 子目录 |
| 错误响应统一格式？ | ErrorResponse(code, message)，code 全大写下划线如 AUTH_INVALID_TOKEN；放 core/exceptions.py |
| schemas 放哪？ | 各模块内联（zones/admin/schemas.py），不集中 |
| demo zone 作用？ | 扩展模块开发示例，最小可用结构展示（router/schemas/service/models）|
| coverage.py 全局覆盖率虚低（75.93%）原因？ | 未配置 source + concurrency，异步代码追踪失效；加 source=["boxbase"] + concurrency=["thread","greenlet"] 后跃升 93.83% |
| get_current_user 在哪？ | core/security.py（不在 dependencies.py），routers 从 boxbase.core.security 导入 |
| RequestContext 有 jti 吗？ | 没有，只有 user_id / active_tenant_id / is_superadmin；switch_tenant 传 None 给 current_jti |
| require_permission 怎么避免循环导入？ | lazy import（函数内部 import get_current_user），写在 core/dependencies.py |
| 派工提示词中模板与实际签名不符怎么办？ | 本地 AI IDE 执行前自查（先读源码确认实际签名），主动适配并汇报 |
| —— Week 2 Day 2（历史累积）—— | |
| pytest-cov 路径写法？ | 必须用 Python 模块路径（--cov=boxbase.core.security），不能用文件系统路径 |
| seed.py 覆盖率怎么处理？ | omit = ["boxbase/tools/*"] |
| Membership 唯一约束？ | DB 级 UniqueConstraint(tenant_id, user_id)；is_default 应用层保证 |
| RefreshToken jti 存什么？ | 明文 UUID 字符串作索引键（token 原文不落库 ≠ jti 不落库）|
| —— Week 2 Day 1（历史累积）—— | |
| 多租户隔离选哪种？ | Row-level + tenant_id；ORM with_loader_criteria 强制过滤；PG RLS 第二防线 v1.0 不启用 |
| 超管设计？ | 配置文件注入 superadmin username；归属系统保留租户；请求上下文层 short-circuit |
| 角色作用域？ | tenant-scoped；每租户 seed 默认角色（owner/admin/member）；超管 short-circuit 不进 RBAC |
| 认证库选哪个？ | DIY 薄层（pyjwt + pwdlib + FastAPI 原生依赖注入）|
| refresh token 策略？ | 方案 C 存库可撤销：jti 白名单 + rotation；access ≤30min，refresh 7d |
| 全局用户模型？ | User 全局唯一（username/email/phone 单列唯一），经 membership 加入多租户；token 带 active_tenant_id |
| 部门归位？ | v1.0 不建表；未来通用 group + membership_groups 多对多挂 membership 层 |
| —— Week 1（历史累积）—— | |
| 前端为何不走 AntD Pro 脚手架？ | pnpm create vite 干净项目 + 按需引入；Pro Components 延后 Week 4-5 |
| Vite proxy 前缀？ | 前端 /api/* → 后端 8000 不 rewrite，dev/prod 路径一致 |

## 3. 文件与引用内容索引（含历史累积）

### 架构与设计文档（长期有效）

| 文件 | 路径 | 说明 |
|---|---|---|
| 平台架构规范 | docs/architecture/2026-W2-platform-architecture-design.md | core/+zones/ 模块化规范单一真相源；扩展模块开发指南；变更记录滚动 |
| 认证设计评审 | docs/architecture/2026-W2-auth-tenant-rbac-design.md | 认证/多租户/RBAC 详细设计；ER/字段/API/时序图 |
| Day 1 归档 | docs/decisions/2026-0530-week2-day1-auth-design-review.md | Week 2 Day 1 滚动累积版 |
| Day 2 归档 | docs/decisions/2026-0530-week2-day2-slice1-9-complete.md | Week 2 Day 2 滚动累积版 |
| Day 3 归档（本文件） | docs/decisions/2026-0531-week2-day3-complete.md | Week 2 Day 3 滚动累积版 |

### Week 2 Day 3 后端目录结构（最终态）

    backend/boxbase/
      core/
        base.py          ← AuditMixin + DeclarativeBase（从 models/base.py 迁移）
        config.py        ← pydantic-settings
        database.py      ← async engine + session factory
        dependencies.py  ← RequestContext / get_db / apply_*_filter / require_permission(lazy import)
        exceptions.py    ← ErrorResponse + ErrorCode 常量 + http/validation 异常处理器
        security.py      ← hash/verify/JWT/get_current_user
        router.py        ← 平台路由总入口（聚合 admin + demo + health）
      zones/
        admin/
          models/        ← 8 张基础表（user/tenant/membership/role/permission/membership_role/role_permission/refresh_token）
          routers/       ← auth.py / users.py / roles.py / admin.py
          services/      ← auth.py / users.py / roles.py
          router.py      ← 聚合 routers/，对外唯一入口
          schemas.py     ← 全部 Pydantic schema
          service.py     ← 聚合 services/，对外唯一入口
        demo/
          models/        ← 空（示例无业务表）
          router.py      ← GET /api/demo/items 示例端点
          schemas.py     ← DemoItemResponse
          service.py     ← list_items() 返回空列表
      tools/seed.py
      main.py            ← 极简，注册异常处理器 + include api_router
    backend/tests/
      conftest.py
      test_security.py
      zones/admin/
        conftest.py      ← 共享 fixture：内存 DB + seed + token 生成
        test_auth.py     ← 18 用例
        test_users.py    ← 13 用例
        test_roles.py    ← 10 用例

### 关键文件说明

| 文件 | 关键数据/约束 |
|---|---|
| core/security.py | get_current_user(token, db) 返回 RequestContext；超管 short-circuit + active membership 校验；create_access_token(user_id:UUID, active_tenant_id:UUID, username:str)；create_refresh_token(jti:str, user_id:UUID)；decode_access_token / decode_refresh_token（无通用 decode_token） |
| core/dependencies.py | RequestContext 字段：user_id / active_tenant_id / is_superadmin（无 jti）；require_permission 用 lazy import |
| core/exceptions.py | ErrorCode 常量集中；http_exception_handler 将 dict detail 含 code 直通，否则包装为 VALIDATION_ERROR |
| admin/services/auth.py | register/login/refresh_token/logout/switch_tenant/get_my_tenants；switch_tenant 接受 current_jti 可为 None |
| pyproject.toml | omit=["boxbase/tools/*"] + source=["boxbase"] + concurrency=["thread","greenlet"]（异步追踪必需）+ asyncio_mode=auto |
| ci.yml | 全局 --cov=boxbase --cov-fail-under=80；security --cov=boxbase.core.security --cov-fail-under=95 |
| .env | SUPERADMIN_USERNAME=superadmin（演示配置入库）|

### 17 个 admin 端点清单

    POST   /api/auth/register           公开
    POST   /api/auth/login              公开
    POST   /api/auth/refresh            有效 refresh
    POST   /api/auth/logout             公开（带 token）
    POST   /api/auth/switch-tenant      self + 目标 membership
    GET    /api/auth/tenants            self
    GET    /api/users/me                self
    GET    /api/users                   user:read
    POST   /api/users                   user:write
    PATCH  /api/memberships/{id}        user:write
    DELETE /api/memberships/{id}        user:write
    GET    /api/roles                   role:read
    POST   /api/roles                   role:write
    PUT    /api/roles/{id}/permissions  role:assign
    GET    /api/permissions             role:read
    GET    /api/admin/tenants           superadmin
    GET    /api/admin/users             superadmin

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| pytest（本次） | 回归 + 集成测试 | 21→46→61 全绿 |
| pytest-cov（本次） | 覆盖率统计 | 首次 75.93% 未达标 → 加 concurrency 配置后 93.83% / security 100% 双门禁 PASS |
| coverage 配置修复（本次） | 修复异步追踪 | source=["boxbase"]+concurrency=["thread","greenlet"] 使 service 层覆盖率从 30%+ 跃升至 90%+ |
| uvicorn（本次） | 端点验证 | 18 端点可见（17 admin + 1 health）|
| ruff/mypy（本次） | 代码质量 | 每次 commit 前三关全过；mypy SQLAlchemy 类型推断用 type: ignore[arg-type/union-attr] 处理 |
| email-validator 安装（本次） | 解决 EmailStr 依赖 | uv add "pydantic[email]"，引入 email-validator 2.3.0 + dnspython 2.8.0 |
| alembic upgrade（历史）| 验证迁移 | 5 次迁移往返成功 |
| seed.py（历史） | 系统数据初始化 | 14 条 [+]→[=] 幂等验证 |
| PyPI JSON API（历史）| 版本核实 | 所有依赖锁定实际字符串 |
| pre-commit/GitHub Actions（历史） | 代码质量 + CI 双重防线 | TruffleHog 秘密扫描，云端 20s 内熔断 |

## 5. 决策与结论（含历史累积）

### Week 2 Day 3 架构决策（本次会话，长期有效）

1. 模块化架构：core/ 全局基础设施 + zones/ 业务模块；禁止模块间横向 import；禁止 core/ 反向 import zone
2. 模块契约（统一规则）：每模块对外唯一 router.py + service.py；端点 >8 拆 routers/，service 函数 >10 拆 services/；models 归模块自身
3. admin zone：平台内核模块，承载全部 8 张基础表 + 17 个 API 端点
4. core/ 内容固定 7 文件：base / config / database / dependencies / exceptions / security / router
5. ErrorResponse：统一 code+message 格式，ErrorCode 常量集中管理
6. require_permission：写在 core/dependencies.py，用 lazy import 避免循环依赖
7. demo zone：最小示例模块，作为扩展开发参考
8. coverage.py 配置（强制）：[tool.coverage.run] 必须含 source=["boxbase"] + concurrency=["thread","greenlet"]，否则异步追踪失效
9. get_current_user 位置：core/security.py，routers 从此导入
10. RequestContext 字段：user_id / active_tenant_id / is_superadmin（无 jti）；switch_tenant 传 None 给 current_jti
11. main.py 极简：只 add_exception_handler + include_router(api_router, prefix="/api")
12. 端点路径规范：所有端点统一 /api 前缀（由 core/router.py 注入）；admin 模块 /api/auth/* / /api/users/* / /api/roles/* / /api/permissions/* / /api/admin/*

### Week 2 Day 2 技术决策（长期有效）

1. 全链路 async：SQLAlchemy async engine + aiosqlite(dev)/asyncpg(prod)；SQLite WAL + foreign_keys 注入
2. Alembic：单目录 + async env.py + 空 baseline；script.py.mako 模板含 op/sa import
3. AuditMixin 5 字段（created_at/updated_at/created_by/updated_by/deleted_at），id 用 Uuid 类型
4. Membership：DB 级 UniqueConstraint(tenant_id, user_id)；is_default 应用层保证
5. RefreshToken：jti 明文 UUID 唯一索引（token 原文不落库 ≠ jti 不落库）
6. 依赖注入：RequestContext dataclass + FastAPI Depends；apply_tenant_filter / apply_soft_delete_filter 用 with_loader_criteria 显式注入
7. security 模块：get_current_user 超管 short-circuit + active membership 双校验；rotation 撤销旧 jti
8. 配置化：superadmin_username / access_token_expire_minutes=30 / refresh_token_expire_days=7 写进 config
9. seed 幂等：系统租户(slug=system,is_system=True) + superadmin + 3 角色 + 5 权限 + 默认 member
10. 覆盖率门禁：全局 ≥80% / security ≥95%；seed.py omit
11. .env 入库作为演示配置（SUPERADMIN_USERNAME=superadmin）

### Week 2 Day 1 架构决策（长期有效）

1. 多租户隔离：Row-level + tenant_id；RLS 第二防线 v1.0 不启用、预留 hook
2. 超管：配置注入 superadmin username；系统保留租户；请求上下文层 short-circuit
3. 角色：tenant-scoped；每租户 seed 默认角色；超管硬编码全通过
4. RBAC：简化三表 + resource:action；权限 seed 固定；对象级放 service 层；三层访问控制（隔离/RBAC/对象级）
5. 认证库：DIY 薄层（pyjwt + pwdlib + FastAPI 依赖注入），独立 security 模块
6. 哈希/JWT：pwdlib[argon2] / pyjwt[crypto]；HS256，RS256 延后
7. refresh：方案 C 存库可撤销，jti 白名单 + rotation；access ≤30min，refresh 7d
8. 全局用户模型：User 全局唯一(username/email/phone 单列唯一)；MEMBERSHIP 核心关联表；角色挂 membership；token 带 active_tenant_id
9. 部门归位：v1.0 不建表；未来通用 group + membership_groups
10. 系统/默认租户合并一条(is_system)；membership 强制默认 member；phone nullable 全局唯一；membership 加 is_default
11. 审计 Mixin 五字段；软删 deleted_at 与 ORM 过滤联动

### 工程化决策（Week 1，长期有效）

1. pre-commit local repo + uv run --directory backend；CI setup-uv + uv sync
2. 双重防线：pre-commit(本地) + GitHub Actions(云端)
3. 前端栈：React 19.2 + Vite 8 + TS 6 + AntD v6 + react-router-dom v7；Pro Components 延后；pnpm 10.33
4. 运行时 mise(scoop 装) 管 Node 22；SECRETS.md 走 .gitignore 工具级隔离
5. 后端所有路由统一 /api 前缀；Vite proxy 不 rewrite

## 6. 错误与修正（含历史累积）

| 错误/偏差 | 发现时机 | 修正/教训 |
|---|---|---|
| 本次：派工模板 security.py 函数签名与实际不符 | 切片 4 本地 AI IDE 执行前自查 | 适配实际签名（create_access_token 含 username 参数 / decode_refresh_token）；建立纪律：执行前先读源码 |
| 本次：派工模板引用 ctx.jti 但 RequestContext 无该字段 | 切片 6 执行前自查 | switch_tenant 传 None 给 current_jti |
| 本次：require_permission 与 get_current_user 循环导入 | 切片 6 执行时 | lazy import 解决（函数内部 import）|
| 本次：coverage.py 异步追踪失效导致覆盖率虚低 75.93% | 切片 9 首跑 | 加 source=["boxbase"]+concurrency=["thread","greenlet"]，跃升至 93.83% |
| 本次：test_login_inactive_user 用错误密码无法覆盖 is_active 分支 | 本地 AI IDE 自查 | 改为直接修改 DB 将 is_active=False |
| 本次：test email 用 @test.local 被 email-validator 拒绝 | pytest 报错 | 改为 @example.com |
| 本次：core/router.py 已含 health 端点不能直接替换 | 执行前自查 | 追加 admin/demo router 而非替换 |
| 本次：mypy 在 SQLAlchemy db.execute(select(...)) 上类型推断不准 | mypy 报错 | 用 type: ignore[arg-type/union-attr] 精确标记，已知 SQLAlchemy 插件限制 |
| 本次：顾问擅自启动归档任务 | 用户两次质问 | 守纪律 — 等用户明确指示再写；归档输出格式严格按提示词规范 |
| 历史：seed.py 0% 拖累全局覆盖率 | Day 2 切片 9 | omit=["boxbase/tools/*"] |
| 历史：alembic.ini 含中文注释 GBK 解码失败 | Day 2 切片 1 | 注释必须用 ASCII（Windows encoding="locale"）|
| 历史：script.py.mako 缺 op/sa import | Day 2 autogenerate NameError | 模板必须含 op/sa import 块 |
| 历史：AI 把 department_id 放 USER 表 | Day 1 设计阶段 | 部门归位 membership 层，v1.0 不建 |
| 历史：误判前端版本为幻觉 | Week 1 | 版本判断必先联网核实 |

## 7. 讨论演变（文字描述）

会话开门：用户提供 Day 2 归档 + 认证设计文档同步上下文 → 顾问复述同步点 + 提出 Day 3 开工前 4 个微决策（router 拆分 / 错误响应 schema / Pydantic 目录 / service 层位置）。

架构重构讨论：用户对水平切分提出 Zone 方案（垂直切分）疑问 → 顾问评估 models 是否下沉 → 用户决策 models 归模块 + 8 张基础表归 admin zone（避免跨 zone import）→ 讨论全局共享内容放 core/ → 确认路由总入口放 core/router.py + main.py 极简 → 确认每模块对外唯一 router.py / service.py 契约（端点多/服务多时拆子目录但对外仍单入口）。

架构规范文档优先：用户要求先出 2026-W2-platform-architecture-design.md 规范文档再出派工 → 顾问出完整规范文档（10 章节 + 目录结构 + 模块契约 + 数据模型/认证/API/测试/工程化规范 + 扩展模块开发指南）→ 用户确认无误 → 放行派工。

切片 1-3：目录重构 + core/ 迁移（94ca4e2）+ ErrorResponse 接入（879da1d）+ admin schemas（ca71c8a），主要处理 ruff import 排序和 email-validator 依赖。

切片 4-5：auth/users/roles services 实现（a89e651/c84e3b0），本地 AI IDE 执行前自查发现 security.py 实际签名与派工模板不符，主动适配并汇报（建立纪律）；mypy SQLAlchemy 类型推断问题用 type: ignore 精确处理。

切片 6（最大）：实现全部 17 个端点（015cc49），发现 get_current_user 在 security.py 而非 dependencies.py、RequestContext 无 jti、require_permission 循环导入三个问题，本地 AI IDE 自查修正；最终 18 端点可见。

切片 7：demo zone 最小示例（c564ce3），顺利通过。

切片 8：集成测试（8615373），初版 4 个失败（email 域名 + invite 重复），修复后 46/46 全绿。

切片 9：CI 路径更新 + 覆盖率验收。首跑全局 75.93% 未达标，定位为 coverage.py 未配置 concurrency 导致异步代码追踪失效；加 source + concurrency 后跃升至 93.83%，双门禁 PASS（4259562）。

收尾：顾问两次擅自启动归档任务被用户质问"没守纪律"+ 输出格式不符（用了多个代码块、嵌套代码块、代码块外有解释文字）→ 顾问承认偏差、等用户明确指示。

## 8. 当前状态与后续步骤

### Git 状态

- 最新 commit：4259562（test: add branch coverage tests to reach 80% threshold (slice-9-patch)）
- Day 3 提交链（10 条）：
  - 824cceb docs: add Week 2 Day 2 complete archive (slice 1-9)
  - 94ca4e2 refactor: restructure to core and zones modular architecture
  - 879da1d feat: add ErrorResponse schema and global exception handler (slice-2)
  - ca71c8a feat: add admin zone Pydantic schemas (slice-3)
  - a89e651 feat: add admin zone auth service (slice-4)
  - c84e3b0 feat: add admin zone users and roles services (slice-5)
  - 015cc49 slice6-routers-wireup
  - c564ce3 feat: add demo zone as extension module example (slice-7)
  - 8615373 test: add integration and security tests for admin zone (slice-8)
  - 4259562 test: add branch coverage tests to reach 80% threshold (slice-9-patch)
- 待提交（由本地 AI IDE 一并提交保持仓库干净）：
  - 本归档：docs/decisions/2026-0531-week2-day3-complete.md
  - 架构规范文档补丁（在 2026-W2-platform-architecture-design.md 中追加变更记录）：get_current_user 在 core/security.py / RequestContext 无 jti / coverage 必须配 concurrency
- 建议 commit message：docs: add Week 2 Day 3 archive and patch architecture spec

### Completed

- Week 1 全部闭环（dadf307，tag week1-complete @ 07ee750）
- Week 2 Day 1：架构主干全部决策点闭环；设计评审文档落地
- Week 2 Day 2：9 切片落地，21/21 绿
- Week 2 Day 3：core/+zones/ 架构重构 + 17 个 API 端点 + demo zone + 61/61 绿，覆盖率 93.83%/100%；架构规范文档落地

### Next Steps（Week 2 Day 4，新会话）

- 新会话同时提供本归档 + 架构规范文档（2026-W2-platform-architecture-design.md）+ 认证设计文档（2026-W2-auth-tenant-rbac-design.md）三份
- 新会话 AI 开场先复述同步点 + 确认角色边界 + 等用户明确放行才写派工/文档
- Day 4 候选任务（待用户拍板）：
  - 前端登录/注册页面（React + AntD v6 + react-router-dom v7）
  - API 手动测试（Postman/httpie 完整流程验证 + 演示数据准备）
  - Week 2 复盘 + Week 3 业务模块规划（基于 demo zone 示例扩展）
  - 其他用户指定任务

### 技术栈备忘（最新）

- 后端结构：core/（基础设施 7 文件）+ zones/admin/（平台内核 17 端点）+ zones/demo/（示例）
- API：18 端点（17 admin + 1 health），统一 /api 前缀
- 测试：61 条（21 原有 + 40 新增），全绿
- 覆盖率：全局 93.83%（门禁 80%）/ core.security 100%（门禁 95%）；seed.py omit；coverage 配置必须含 source+concurrency
- 已装依赖：alembic 1.18.4 / pydantic-settings 2.14.1 / aiosqlite 0.22.1 / asyncpg 0.31.0 / pwdlib 0.3.0 / PyJWT 2.13.0 / pytest-cov 7.1.0 / coverage 7.14.1 / email-validator 2.3.0 / dnspython 2.8.0
- 隔离：Row-level + tenant_id；ORM with_loader_criteria 强制过滤（tenant + deleted_at）
- 认证：DIY security 模块；HS256；refresh 存库可撤销 + rotation；access 30min / refresh 7d
- 前端：Node 22.22.3(mise) + React 19.2 + Vite 8 + TS 6 + AntD 6.4.3 + react-router-dom v7
- 数据库：SQLite(dev) / PostgreSQL(prod)；Alembic 双环境迁移一致
- 工具链：ruff + mypy + pytest + pytest-cov + ESLint 10 + Prettier 3.8 + pre-commit + GitHub Actions + TruffleHog；mise 2026.5.15

### 工程纪律（含历史累积，覆盖至 Day 3）

1. 顾问只出决策建议/派工提示词/验收清单；不粘源码、不进 Agent Mode、不调 browser_task_tool
2. 写文档/派工前先把待确认项问全，用户拍完再动笔；不得事后补问题
3. 未经用户明确指示，不得擅自启动归档/派工提示词写作任务（Day 2 立、Day 3 强化两次）
4. 归档输出严格按提示词规范：单个 markdown 代码块、不嵌套代码块、代码块外只一句使用说明
5. 设计文档/归档由顾问写完整内容，本地 AI IDE 只存文件 + commit，不创作
6. commit 前本地 AI IDE 执行 git status --short 列出文件给用户确认；保持仓库干净
7. 版本号必须联网核实并贴实际字符串；技术栈版本变更先报备
8. 带日期文件名以 current-time 为准（不凭直觉顺延）
9. 归档为滚动替换式：合并历史 + 本次，老内容压缩成结论/纪律，新会话只读这一份
10. 派工提示词必须一整块可复制 markdown，不得散落多段
11. 严禁 --no-verify / --force push / 自动 prettier --write 不经确认
12. pytest-cov 路径必须用 Python 模块路径（--cov=boxbase.core.security），不能用文件系统路径
13. alembic.ini 注释必须用 ASCII（Windows encoding="locale" 会 GBK 解码失败）
14. script.py.mako 模板必须包含 op/sa import 块
15. 本地 AI IDE 自查发现明确 bug（如参数名不符、签名不符）应直接修正并汇报，不需等顾问指示
16. PowerShell CLIXML 黑名单（输出可能被吞）；mise 迁移后已根治
17. 修复 deprecation warning 属合理范围；改 props 语义需停下确认
18. coverage.py 追踪异步代码必须配置：[tool.coverage.run] 中加 source=["boxbase"] + concurrency=["thread","greenlet"]，否则 service 层覆盖率严重虚低（Day 3 立）
19. get_current_user 从 core/security.py 导入，不从 core/dependencies.py 导入（Day 3 立）
20. RequestContext 无 jti 字段；需要 jti 的场景（如 switch_tenant rotation）传 None，由 service 层处理（Day 3 立）
21. require_permission 用 lazy import（函数内部 import get_current_user）避免 core/ 内循环依赖（Day 3 立）
22. 测试 email 域名用 @example.com，@test.local 等非标准域名会被 email-validator 拒绝（Day 3 立）
23. 派工提示词中模板与实际签名/字段不符时，本地 AI IDE 必须执行前先读源码确认，主动适配并汇报；顾问后续派工应注明"以实际为准"提示（Day 3 立）
24. 模块对外接口契约：每个 zone 模块对外暴露唯一 router.py + service.py；内部拆分（routers/、services/ 子目录）对平台透明；新增模块在 core/router.py 追加一行 include 即可（Day 3 立）
