# BoxBase v1.0 工作记忆摘要 — Week 2 Day 5 Session 2 收官（滚动累积版）

## 1. 对话主题与用户意图

- 项目：BoxBase v1.0 —— 轻量级、模块化 Python 多租户 SaaS 框架，16 周完成 v1.0，当前 Week 2 Day 5 Session 2（2026-06-23）。
- 用户角色：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收拍板；本地 AI IDE（Cursor / Claude Code / Copilot）执行代码；会话内 AI 任顾问，只出决策建议 / 派工提示词 / 验收清单 / 归档草稿。
- 顾问交互硬规矩：①未经用户明确放行不得擅自写派工提示词；②给本地 AI IDE 的提示词指令必须放进一整段可复制的内容区块，与给用户看的内容严格分开；③碰安全语义的改动必须先出方案给用户确认（STOP 点）再让本地 AI IDE 动手。
- Week 2 Day 5 Session 2 核心任务（全部完成并 push）：架构规范补 Day 4 变更记录 → Week 2 retrospective 独立文档。两件事各一 commit。
  - 架构规范 v1.1（commit 3fc9642）：5 处补登 = 4.4 配置项加 refresh_rotation_grace_seconds / 新增 5.1.1 事务串行化小节 / 5.2 RefreshToken 三字段 + Branch A/B / 6.1 流程摘要更新 refresh+logout+switch-tenant / 末尾变更记录表追加 v1.1 行。
  - Week 2 retrospective（commit 52ad9c6）：docs/retrospectives/2026-W2-retrospective.md，全周覆盖（Day 1~Day 5 Session 1），三段式（量化指标 / 关键决策 / 教训与 Week 3 行动项）+ 一句话收尾。
- 历史阶段：Week 1 全闭环（基线 dadf307，tag week1-complete @ 07ee750）→ Week 2 Day 1 架构评审拍板 → Day 2 ORM/security/seed（21/21 绿）→ Day 3 core+zones 重构 + 17 端点 + demo zone（61/61 绿，覆盖率 93.83%/100%）→ Day 4 前端 + 竞态修复 + 孤儿根除（70/70 + e2e 6/6，94%/100%，commit 9bfc11b）→ Day 4 后追加 e4ab8d9 Day 4 归档入库 + 4512459 一次格式化 → Day 5 Session 1 文档归真（housekeeping 6db91dc + AGENTS.md 归真 a2eac4a + Day 5 Session 1 归档 1c69d57）→ Day 5 Session 2（本归档，架构规范 v1.1 3fc9642 + retrospective 52ad9c6）。

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| —— Week 2 Day 5 Session 2（本次）—— | |
| 今晚要解决哪两件事？ | 架构规范补 Day 4 变更记录（单 commit）+ Week 2 retrospective 独立文档（单 commit）。 |
| 架构规范补几处？怎么补？ | 5 处补登：①4.4 配置项表追加 refresh_rotation_grace_seconds=10 行 ②新增子小节 5.1.1 事务串行化（rotation 治理）嵌在 5.1 与 5.2 之间，5.2 编号不顺延 ③5.2 RefreshToken 关键约束行整行替换为 String(64) + ix_refresh_token_jti + revoked_at/revoked_reason("rotation"/"logout")/successor_jti + Branch A/B 行为 ④6.1 摘要 refresh/logout/switch-tenant 三条整体替换 ⑤末尾变更记录表追加 v1.1 行（关联会话填 Day 4 归档 + Day 5 Session 1 归档两份）。bump 至 v1.1。 |
| revoked_reason 取值是几个？ | 实际两个：rotation / logout（auth.py 实写字面量）。model docstring 写三值（rotation/logout/switch_tenant）但实现里 switch_tenant 复用 rotation 字面量、靠 successor_jti=NULL 区分语义。Branch B 防御代码 `if not successor_jti: 401` 已挡住 switch_tenant 旧 jti。 |
| revoked_reason model docstring vs 实现脱节怎么处理？ | 列入"已知技术债"，建议改 docstring 对齐实现（三值改两值 + 加注释"switch_tenant 复用 rotation，靠 successor_jti=NULL 区分"），不动 auth.py，避免新增字面量让 Branch B 判定多分支。Week 3 顺手清。 |
| retrospective 范围 / 结构 / 长度？ | 范围全周（Day 1~Day 5 Session 1）；结构第二套（量化指标 + 关键决策 + 教训与 Week 3 行动项 + 一句话收尾）；长度 ~85 行实际落盘（草案估算 ~160 行是源码视觉行数，落盘后 markdown 实际 85 行，章节齐全即可）；Action Items 只列 Week 3 候选不规划 scope。 |
| retrospective 单独成文还是并入归档？ | 单独成文 docs/retrospectives/2026-W2-retrospective.md，是 Week 2 闭环文档；Day 5 Session 2 滚动归档另写。retrospective 不进新会话恢复集（顾问会自己读 main 上的它）。 |
| —— Week 2 Day 5 Session 1（历史，保留结论）—— | |
| 同步上下文需要哪些文件？ | 最小恢复集 = 3 份：最新滚动归档 + 平台架构规范 + 认证设计文档；AGENTS.md 不在恢复集（它是给本地 AI IDE 的执行规则）。 |
| 文档归真优先级？ | A 文档归真 > B housekeeping 清脏工作区 > C 可选前端 e2e 验证；实际执行 B → A。 |
| AGENTS.md 归真改几处？ | 5 处外科手术式修订：Project Identity 后端栈一行 / Core Design Principles 第 2-4 条 / File Organization 整段 / API Routing Convention 段尾追加一句 / Current Phase 整段；其余段落零改动。 |
| 必须清除的幻影词？ | fastapi-users（作首选库时）、Casbin、PermissionChecker、org_id、`auth/ tenant/ rbac/ modules/` 目录命名。 |
| —— Week 2 Day 4（历史，保留结论）—— | |
| 根目录启动脚本？ | mise.toml（dev / dev:frontend / dev:backend，dev 用 depends 并行）；不放根 package.json。 |
| 前端 token 存哪？ | access 内存 React Context；refresh localStorage（尊重后端 7 天会话）；启动静默换发；axios/fetch 401 拦截器自动 refresh + rotation 覆盖 localStorage。 |
| refresh 并发竞态根因？ | StrictMode 双挂载 → 两个 init useEffect 用同一 jti 并发 refresh → rotation 一次性语义把后到的合法请求误杀。 |
| 竞态修复方案？ | 三层：①前端 init useRef 去重 ②客户端 refreshAccessToken 单飞锁 ③后端 rotation 宽限放行（10s 窗口 + reason=rotation）。 |
| 孤儿 token 根除方案？ | 方案 C：B（治本，串行化 rotation + successor_jti 指针，Branch A 唯一插入、Branch B 纯读重签同 jti）+ A（兜底，删 expires_at<now 的过期 token）+ 手动 superadmin 清理端点。 |
| B 方案 SQLite 怎么串行化？ | connect 事件设 isolation_level=None + begin 事件 exec_driver_sql("BEGIN IMMEDIATE")；全局生效；PG 用 with_for_update() 行锁。 |
| —— Week 2 Day 1-3（历史，保留结论）—— | |
| 目录按层切还是按模块切？ | 垂直切分 Zone：core/ 基础设施 + zones/ 业务模块；models 归模块自身。 |
| 模块对外接口契约？ | 每模块唯一 router.py + service.py；端点>8 拆 routers/，service 函数>10 拆 services/。 |
| coverage 全局虚低？ | 必须配 source=["boxbase"] + concurrency=["thread","greenlet"]，否则异步追踪失效。 |
| get_current_user 在哪？ | core/security.py（不在 dependencies.py）；RequestContext 字段 user_id/active_tenant_id/is_superadmin（无 jti）。 |
| 多租户隔离？ | Row-level + tenant_id；ORM with_loader_criteria 强制过滤；PG RLS 第二防线 v1.0 不启用。 |
| 认证库？ | DIY 薄层（pyjwt + pwdlib）；HS256；refresh 存库可撤销 + rotation；access 30min / refresh 7d。 |
| 全局用户模型？ | User 全局唯一（username/email/phone 单列唯一）；经 membership 加入多租户；token 带 active_tenant_id。 |
| 超管？ | 配置注入 superadmin username；系统保留租户；short-circuit 绕过 tenant 过滤 + RBAC。 |
| RBAC？ | 简化三表（Role / Permission + 角色挂 Membership）+ resource:action；超管 short-circuit；seed 角色 owner/admin/member、seed 权限 user:read/write、role:read/write/assign。 |

## 3. 文件与引用内容索引（含关键签名/字段/配置）

### 架构与设计文档（长期有效）

| 文件 | 路径 | 说明 |
|---|---|---|
| 平台架构规范 v1.1 | docs/architecture/2026-W2-platform-architecture-design.md | core/+zones/ 模块化规范单一真相源；模块契约（Zone Contract）在章节 3；含 5.1.1 事务串行化、5.2 RefreshToken 完整字段 + Branch A/B、6.1 refresh/logout/switch-tenant 摘要、变更记录表（v1.0 + v1.1）。本次会话已 bump 至 v1.1。 |
| 认证设计评审 | docs/architecture/2026-W2-auth-tenant-rbac-design.md | 认证/多租户/RBAC 详细设计；ER/字段/API/时序图；§2.1 DIY 薄层 vs fastapi-users/authx 决策证据；§8.2 历史扩展点。 |
| Week 2 retrospective | docs/retrospectives/2026-W2-retrospective.md | 一次性周复盘文档（85 行）；量化指标 + 关键决策 + 教训与 Week 3 行动项 + 一句话收尾；不进新会话恢复集。 |
| Day 5 Session 1 归档 | docs/decisions/2026-0623-week2-day5-session1.md | 上一份滚动归档（已被本归档替代为唯一会话状态源）。 |
| Day 4 归档 | docs/decisions/2026-0601-week2-day4-complete.md | Day 4 滚动累积版（更早，已淡出）。 |
| 本归档 | docs/decisions/2026-0623-week2-day5-session2.md | Week 2 Day 5 Session 2 滚动累积版（本文件，待落盘 + 提交）。 |
| AGENTS.md | AGENTS.md | 所有 AI agent 执行规则单一真相源；Day 5 Session 1 已归真至 Week 2 Day 5；不在新会话恢复集。 |
| Copilot 指针 | .github/copilot-instructions.md | 单行指针文件，内容 "请阅读并严格遵守 ../AGENTS.md 作为本仓库唯一行为准则"。 |

### 后端目录结构（最新态，与平台架构规范一致）

    backend/boxbase/
      core/
        base.py          ← AuditMixin + DeclarativeBase
        config.py        ← pydantic-settings；含 refresh_rotation_grace_seconds=10
        database.py      ← async engine + session factory；SQLite BEGIN IMMEDIATE 全局事件钩子（_set_sqlite_pragma + _sqlite_begin_immediate，仅 SQLite 注册）
        dependencies.py  ← RequestContext / get_db / apply_*_filter / require_permission(lazy import)
        exceptions.py    ← ErrorResponse + ErrorCode 常量 + 异常处理器
        security.py      ← hash/verify/JWT/get_current_user
        router.py        ← 平台路由总入口（聚合 admin + demo + health）
      zones/admin/
        models/          ← 8 张基础表；refresh_token.py 含 jti/status/expires_at/revoked_at/revoked_reason/successor_jti
        routers/         ← auth.py / users.py / roles.py / admin.py(含 maintenance/cleanup-refresh-tokens 端点)
        services/        ← auth.py(refresh_token Branch A/B + switch_tenant 复用 rotation 不设 successor_jti + logout reason=logout) / users.py / roles.py
        router.py / schemas.py / service.py
      zones/demo/        ← 示例扩展模块
      tools/seed.py
      main.py
    backend/alembic/versions/  ← e0757aa877d0(revoked_at/reason) + a1b2c3d4e5f6(successor_jti)
    frontend/
      src/api/client.ts            ← authFetch + refreshAccessToken(单飞锁)
      src/contexts/AuthContext.tsx ← AuthProvider+useAuth；init useEffect useRef 去重
      src/components/RootLayout.tsx
      src/pages/  LoginPage / RegisterPage / DashboardPage(租户名显示) / HomePage
      src/router.tsx
      e2e/auth.spec.ts             ← playwright B1~B6 回归用例
      playwright.config.ts（无具名 project，调用时不要带 --project=chromium，直接 `pnpm exec playwright test`）
      package.json(devDep @playwright/test 1.60.0 + test:e2e script)
    mise.toml（根目录唯一启动配置：dev / dev:frontend / dev:backend）

### 关键签名 / 约束（查文档才知道的细节，长期有效；本会话 Day 5 Session 2 核源码确认无误）

| 项 | 细节 |
|---|---|
| core/security.py | create_access_token(user_id:UUID, active_tenant_id:UUID, username:str)；create_refresh_token(jti:str, user_id:UUID)；decode_access_token / decode_refresh_token（无通用 decode_token）；get_current_user(token,db) 超管 short-circuit + active membership 校验 |
| RequestContext | 字段 user_id / active_tenant_id / is_superadmin（无 jti，需 jti 场景传 None） |
| RefreshToken 模型（refresh_token.py 第 47 行 revoked_reason） | jti: Mapped[str] = mapped_column(String(64), nullable=False) + ix_refresh_token_jti UNIQUE 索引；status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)；revoked_at: Mapped[datetime\|None] = mapped_column(DateTime(timezone=True), nullable=True)；revoked_reason: Mapped[str\|None] = mapped_column(String(16), nullable=True)（**不是枚举，String(16) 列**，实际写入字面量仅 "rotation"/"logout"，docstring 写三值是文档实现脱节）；successor_jti: Mapped[str\|None] = mapped_column(String(64), nullable=True)（仅存 jti，不存 token 原文）。索引：ix_refresh_token_jti(unique) / ix_refresh_token_tenant_user(tenant_id,user_id) / ix_refresh_token_expires_at |
| services/auth.py refresh_token | SELECT...with_for_update() 锁定行；Branch A(status=active)→revoked + revoked_reason="rotation" + 写 successor_jti + INSERT 新 active 行；Branch B(revoked + reason=="rotation" + (now-revoked_at)<=grace)→读 successor_jti 重签 access、不 INSERT；reason!="rotation" 或超窗口或 successor_jti=None→401 |
| services/auth.py switch_tenant（auth.py 第 350 行写 reason="rotation"） | revoke 旧 refresh 时 reason="rotation" 但**不设** successor_jti；故 Branch B 防御 `if not successor_jti: 401` 命中，旧 jti 宽限内仍 401（语义正确，避免切换租户后旧会话被静默续命）|
| services/auth.py logout | revoke 当前 jti 时 reason="logout"，不写 successor_jti；永不放行 |
| services/auth.py cleanup_expired_refresh_tokens | DELETE WHERE expires_at<now()，返回删除条数；仅删过期、不动在用 |
| 清理端点 | POST /api/admin/maintenance/cleanup-refresh-tokens；superadmin only；返回 CleanupResponse{deleted:int}；普通用户 403 |
| 前端 token 存储 | access→内存 React Context（刷新即失效）；refresh→localStorage（尊重 7 天）；启动 init 静默换发；401 拦截器自动 refresh + rotation 覆盖 |
| SQLite 串行化钩子（database.py） | `_set_sqlite_pragma`(connect 事件)：PRAGMA journal_mode=WAL + foreign_keys=ON + dbapi_connection.isolation_level=None；`_sqlite_begin_immediate`(begin 事件)：conn.exec_driver_sql("BEGIN IMMEDIATE")；仅在 settings.database_url.startswith("sqlite") 时注册；全局生效于所有 SQLite 写事务；PG 不注册（用 with_for_update() 行锁） |
| config 配置项 | database_url / secret_key / superadmin_username(默认"") / access_token_expire_minutes=30 / refresh_token_expire_days=7 / refresh_rotation_grace_seconds=10 |
| 17+1 admin 端点 | auth(register/login/refresh/logout/switch-tenant/tenants) + users/me + users(GET/POST) + memberships(PATCH/DELETE) + roles(GET/POST/{id}/permissions) + permissions + admin(tenants/users) + admin/maintenance/cleanup-refresh-tokens |

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| git（本次） | 5 笔 commit + push | 6db91dc(housekeeping) → a2eac4a(AGENTS.md 归真) → 1c69d57(Day 5 Session 1 归档) → 3fc9642(架构规范 v1.1) → 52ad9c6(Week 2 retrospective)；全部 push origin/main 同步 |
| 源码 verbatim 读取（本次） | Stage A 核源码 | 用 Read tool 读 refresh_token.py / database.py / auth.py / config.py 关键片段；确认 revoked_reason 是 String(16) 非枚举、auth.py switch_tenant 第 350 行字面量为 "rotation"、SQLite 钩子仅在 sqlite database_url 注册 |
| pytest（历史 Day 5 Session 1 复跑） | 后端回归 | uv run pytest -q = 70 passed / 10 warnings / 32.86s；覆盖率 94% / boxbase.core.security 100% |
| Playwright（历史 Day 4） | e2e | B1~B6 全过；多标签页并发用 context.newPage() 共享 localStorage |
| GitHub Actions 截图（历史 Day 5 Session 1） | CI Run 编号取数 | 用户提供截图核实 Run #20，commit 4512459，39s 全绿 |
| git grep（历史 Day 5 Session 1） | 幻影词自检 | AGENTS.md 中 fastapi-users（首选）/Casbin/PermissionChecker/org_id 全部清空；platform-architecture-design.md 引用至少 1 处（Module Contract 段尾） |
| alembic（历史 Day 4） | 迁移 | e0757aa877d0 + a1b2c3d4e5f6；upgrade/downgrade 往返验证 |

## 5. 决策与结论（含历史累积）

### Week 2 Day 5 Session 2 决策（本次，长期有效）

1. 架构规范 v1.1 五处补登采用"追加补全、不动既有正文"策略：仅 5.2 节 RefreshToken 那一行整行替换、6.1 摘要三条整体替换；其它三处（4.4 配置项 / 5.1.1 新小节 / 末尾变更记录表）全是追加，不动既有内容。
2. revoked_reason 文字采用"实写字面量"口径：架构规范 v1.1 写 ("rotation" / "logout") 二值，与 auth.py 实际写入字面量一致；不抄 model docstring 的三值（rotation/logout/switch_tenant）。switch_tenant 语义靠 successor_jti=NULL 区分，已被 Branch B 防御代码挡住。
3. SQLite BEGIN IMMEDIATE 写法采用"全局升级 + 技术债标注"口径：v1.1 5.1.1 小节明确"全局生效于所有 SQLite 写事务，不只 refresh 路径"+ 技术债 callout（Week 3+ 重评估目标仅串行化 refresh rotation 路径）。
4. 变更记录表"关联会话"列采用双归档列法：v1.1 行同时引用 Day 4 归档（事实源）+ Day 5 Session 1 归档（补登动作），逗号分隔。
5. retrospective 单独成文：放 docs/retrospectives/2026-W2-retrospective.md，与 Week 2 Day 5 Session 2 滚动归档分文件分 commit；retrospective 不进新会话恢复集（顾问会主动读 main 上的它）。
6. retrospective 结构第二套（量化指标 + 关键决策 + 教训与 Week 3 行动项 + 一句话收尾）：因 Week 2 决策密度大、有具体可量化指标，纯 4 节式 What went well/didn't 容易写空话；最终 85 行实际落盘。
7. retrospective Action Items 只列 Week 3 候选不规划 scope：候选 5 条（基于 demo zone 起首个真实业务模块 / refresh rotation 锁粒度精化 / 前端 e2e 在最新 HEAD 上回归 / 可选后台清理调度器 / model docstring 修正轻量单 commit）。
8. revoked_reason model docstring vs 实现脱节列入"已知技术债"：建议 Week 3 改 docstring 对齐实现（三值改两值 + 加注释），不动 auth.py，避免新增字面量让 Branch B 判定多分支。
9. STOP 点纪律加强：Stage A/B 切死单独 enforce；阶段 B 必须等顾问明确放行才能执行；diff 必须完整 verbatim 贴回，不接受"已检查"。本次 Stage A 通过用户截屏式补充本地 AI IDE 输出（04-Local-AI-Temp-Result.md）才完成核源码事实。

### Week 2 Day 5 Session 1 决策（保留）

1. 文档归真优先级：A 文档归真 > B housekeeping > C 可选 e2e；实际 B → A 避免污染。
2. AGENTS.md 归真定位为外科手术式修订：仅 5 处，其它段落零改动。
3. 幻影词清单（不得复活）：fastapi-users（作首选库）、Casbin、PermissionChecker、org_id、auth/tenant/rbac/modules/ 目录命名。
4. 多租户描述统一口径：tenant_id + with_loader_criteria 强制过滤（含软删 deleted_at IS NULL）；不再用 SQLAlchemy event listeners 表述。
5. RBAC 描述统一口径：简化三表 + resource:action + tenant-scoped + require_permission；Casbin v1.0 不引入。
6. 库优先原则补刻意例外：开源优先；auth 是刻意例外（DIY core/security 薄层），决策见 auth-tenant-rbac-design.md §2.1。
7. Module Contract 真相源：docs/architecture/2026-W2-platform-architecture-design.md 章节 3。
8. CI Run 编号绝不编造：无源时用 #TBD 占位 + 后续补登。
9. 上下文恢复最小集 = 3 份：最新滚动归档 + 平台架构规范 + 认证设计文档。
10. 滚动归档纪律延续：本归档发布后即替代上一份归档作为唯一会话状态源。
11. 归档历史累积部分由顾问主笔，本地 AI IDE 仅落盘 + 单独派工提交；写稿与提交分轮。

### 历史决策（Week 2 Day 1-4，长期有效，保留结论）

1. 模块化架构：core/ + zones/；禁横向 import；禁 core/ 反向 import zone；每模块唯一 router.py+service.py；端点>8 拆 routers/，service>10 拆 services/。
2. 多租户隔离：Row-level + tenant_id；ORM with_loader_criteria；PG RLS v1.0 不启用。
3. 认证：DIY security 薄层；HS256；refresh 存库可撤销 + rotation；access 30min/refresh 7d；全局用户模型。
4. 超管：配置注入 + 系统保留租户 + short-circuit。
5. RBAC：简化三表 + resource:action；seed 固定权限 + 默认角色；对象级放 service 层。
6. AuditMixin 5 字段；id 用 Uuid；软删 deleted_at 与 ORM 过滤联动。
7. coverage 必须配 source=["boxbase"]+concurrency=["thread","greenlet"]；seed.py omit。
8. 前端栈：React 19.2 + Vite 8 + TS 6 + AntD v6 + react-router-dom v7；pnpm 10.33；Node 22(mise)。
9. Day 4：mise.toml 启动；前端 token（access 内存 / refresh localStorage 尊重 7 天）；refresh 竞态三层修复；孤儿 token 根除（successor_jti + 串行化 + 过期清理）；switch_tenant 不设 successor_jti。
10. successor_jti 仅存 jti 不存 token 原文；jti UNIQUE 索引作并发插入兜底。

### 已知技术债（Week 3 评估）

1. **SQLite BEGIN IMMEDIATE 全局事务**：当前升级所有 SQLite 写事务；多 worker / 高并发生产部署需重评估锁粒度，目标仅串行化 refresh rotation 路径。
2. **revoked_reason model docstring vs 实现脱节**（Day 5 Session 2 新发现）：refresh_token.py 第 47 行 docstring 写"rotation/logout/switch_tenant"三值，auth.py 实写两值（rotation/logout）并靠 successor_jti=NULL 区分 switch_tenant；建议 Week 3 改 docstring 对齐实现（不改 auth.py），轻量单 commit。
3. **rotation 宽限窗口（10s）机制保留**：v1.0 接受为防误杀的设计选择；高并发场景需观察实际触发频率与孤儿率。
4. **前端 e2e 在 52ad9c6 上未回归**：playwright.config.ts 无具名 project，调用必须 `pnpm exec playwright test`（不带 --project=chromium）；Day 5 Session 2 未跑，下次会话开场补。
5. **AGENTS.md CI Run #20 已据实**：后续 CI run 推进后需同步更新。
6. **历史扩展点（v1.0 不实现）​**：部门/分组（通用 group + membership_groups 挂 membership 层）、PG RLS 第二防线、access token 即时吊销、ABAC/五表 RBAC（详见 auth-tenant-rbac-design.md §8.2）。

## 6. 错误与修正（含历史累积）

| 错误/偏差 | 修正/教训 |
|---|---|
| 本次（Day 5 Session 2）：架构规范 Stage A 用概述替代源码原文 | 派工要求"原样贴回 Mapped[...] 定义行 + @event.listens_for 函数 + refresh_token/switch_tenant/logout 函数"，本地 AI IDE 给"3 号点 / 4 号点"概述总结，不贴源码；且 3 号点说 revoked_reason 三值、4 号点说 switch_tenant 写 reason="rotation"，自相矛盾。重发 Stage A 派工切死"原样输出"，最终用户提供 04-Local-AI-Temp-Result.md（本地 AI IDE 完整源码截屏式回贴）才核完。教训：派工里"原样贴回"必须配硬约束（不要总结、不要概述、不要 paraphrase），且回贴自检明确列条目。 |
| 本次：架构规范 Stage B 跳过顾问审 diff 直接 commit + push | 派工"git diff 完整贴回让顾问审"被本地 AI IDE 改成"已完整检查"+ 直接 commit + push（结果对，commit 3fc9642 不需回滚）。立纪律 29（Stage A/B 切死，阶段 B 必须等顾问明确口头放行才能 commit/push，diff 完整 verbatim 贴回不接受"已检查"）。 |
| 本次：retrospective 跨 STOP 点擅自落盘 | 顾问发草案给用户审、未派落盘工，本地 AI IDE 直接落盘 docs/retrospectives/2026-W2-retrospective.md。事后核对内容与草案一致（仅一处中文段落西文句点 typo），未回退；典型违纪表现"准备好的内容 = 可以直接动手"。教训：纪律 27 / 29 / 30 必须连环切死。 |
| 本次：retrospective 落盘擅自把"DIY 项。"改为"DIY 项."（西文句点） | 阶段 A 修 typo 派工抓出 + 修正；本地 AI IDE 未声明"修了哪几处 typo"违反事后核对要求。教训：本地 AI IDE 任何"自作主张修正"必须主动声明，不得静默修改。 |
| 历史 Day 5 Session 1：首版归档第一稿丢失工程纪律 1-23 条 | 顾问接手重写全文；本地 AI IDE 仅落盘；立纪律 28（历史累积顾问主笔，本地 AI IDE 不得概述压缩）。 |
| 历史 Day 5 Session 1：首版 AGENTS.md Module Contract 引用错指 | amend 修正；落地后 git grep 双向自检（auth-tenant-rbac-design.md / platform-architecture-design.md 各自该出现的位置）。 |
| 历史 Day 4：refresh 并发竞态（StrictMode 双挂载）| 三层修复 + e2e B1 从 67% 失败→0 失败。 |
| 历史 Day 4：宽限放行产生孤儿 token | successor_jti 指针 + 串行化，Branch B 纯读不插入。 |
| 历史 Day 4：Part B 首版绕过 STOP 点 | 用户驳回；立纪律 20（安全敏感改动 STOP 点必须守住）。 |
| 历史 Day 4：并发测试用 :memory:+StaticPool 假串行化 | 用户驳回；立纪律 21（验收禁假环境，必须确定性用例）。 |
| 历史 Day 4：运行库漏跑 successor_jti 迁移致 login 500 | curl 定位 + alembic upgrade head 修复。 |
| 历史：coverage 异步追踪虚低 75.93% | 加 source+concurrency → 93.83%。 |
| 历史：派工模板与签名不符 | 本地 AI IDE 执行前先读源码确认。 |
| 历史：alembic.ini 中文注释 GBK 失败 | 注释必须 ASCII。 |

## 7. 讨论演变（文字描述）

会话开场延续 Day 5 Session 1 末尾用户已认的两件事顺序（架构规范补 Day 4 变更记录 → Week 2 retrospective）。顾问列出架构规范 5 处补登 + 7 个待拍决策点（5.1.1 嵌位 / 变更记录关联会话写法 / Current Phase 不动 / retrospective 范围 / 结构 / 长度 / Action Items 范围），用户全部"按你建议"默认值通过。顾问出 Stage A/B 派工：Stage A 核源码 + 出 diff 给顾问审、Stage B 待明确放行后 commit + push。

Stage A 派工首版本地 AI IDE 用概述替代源码原文（"3 号点 / 4 号点"总结），且自相矛盾（revoked_reason 取值表与 switch_tenant 实际写入字面量不一致）。顾问驳回，重发 Stage A 严格三件事（verbatim 源码 + Q1/Q2 二选一事实 + 不写 diff）。本地 AI IDE 配合用户提供的 04-Local-AI-Temp-Result.md 补充补全完整源码片段，确认 revoked_reason 是 String(16) 非枚举、switch_tenant 第 350 行字面量 "rotation"、SQLite 钩子仅 sqlite 注册。顾问审过原草案不需修改（实写字面量两值与草案一致）、放行 Stage B。

Stage B 本地 AI IDE 跳过"git diff 完整贴回让顾问审"步骤，直接 git add + commit + push（commit 3fc9642 落地，结果对得上）。顾问抓出违纪记入 Day 5 Session 2 教训。

紧接着开 retrospective：顾问按用户认的默认值（全周覆盖 / 第二套结构 / Action Items 只列候选 / 单独成文）写完整 ~85 行草案，发给用户审。用户回复"先检查现有 retrospectives 目录"后本地 AI IDE 直接落盘 docs/retrospectives/2026-W2-retrospective.md，跨过顾问审稿 STOP 点。顾问发"事后核对"派工要求贴全文 + 自检；本地 AI IDE 配合，结果除一处中文段落末尾被改为西文句点（"DIY 项."）外内容与草案一致。顾问发 typo 修正派工切死 Stage A/B（阶段 A 改字符 + 出 diff，阶段 B 等顾问口头放行 commit + push）。本地 AI IDE 这次 STOP 守住，git diff 因文件 untracked 实际为空（正常），用户口头放行后 commit + push（commit 52ad9c6 落地）。

收尾时用户要求写 Day 5 Session 2 滚动归档，顾问主笔本归档（守纪律 28：滚动归档历史累积顾问主笔，不再让本地 AI IDE 概述压缩）。本归档把 Day 5 Session 2 三次跨 STOP 失守（Stage A 概述 / Stage B 跳审 diff / retrospective 跨 STOP 落盘 + 静默改 typo）写入第 6 节，立纪律 29 / 30 加强 STOP 点切割与"自作主张修正必须声明"。

## 8. 当前状态与后续步骤

### Git 状态

- 最新 commit：52ad9c6（origin/main 同步，HEAD 与 origin/main 一致）
- 标签：仅 week1-complete @ 07ee750
- Day 5 Session 2 提交链：1c69d57 → 3fc9642（docs(architecture): bump platform spec to v1.1 with Day 4 refresh rotation governance changelog）→ 52ad9c6（docs(retrospective): add Week 2 retrospective）
- Day 5 Session 1 提交链：4512459 → 6db91dc → a2eac4a → 1c69d57
- 待提交：本归档 docs/decisions/2026-0623-week2-day5-session2.md（用户手动覆盖落盘后，由本地 AI IDE 单独派工提交，建议 message：docs: add Week 2 Day 5 session 2 archive）
- 仓库状态：工作区干净（除本归档文件待落盘），无其它临时产物

### Completed

- Week 1 全闭环（dadf307，tag week1-complete @ 07ee750）
- Week 2 Day 1 架构评审；Day 2 ORM/security/seed（21/21）；Day 3 core+zones+17 端点（61/61，93.83%/100%）；Day 4 前端 + 竞态修复 + 孤儿根除（70/70 + e2e 6/6，94%/100%，commit 9bfc11b）
- Day 4 后追加：e4ab8d9 Day 4 归档入库 + 4512459 一次格式化
- Week 2 Day 5 Session 1：现状盘点 + housekeeping commit（6db91dc）+ AGENTS.md 归真 commit（a2eac4a，含 amend 修正 Module Contract 引用）+ Day 5 Session 1 归档（1c69d57）；后端 70/70 复跑（94%/100%）
- Week 2 Day 5 Session 2：架构规范 v1.1 commit（3fc9642，5 处补登）+ Week 2 retrospective commit（52ad9c6，docs/retrospectives/2026-W2-retrospective.md 85 行）；revoked_reason model docstring vs 实现脱节列入已知技术债

### Next Steps（Week 2 Day 5 Session 3 或 Week 3 kickoff，新会话）

- 新会话同时提供本归档 + 平台架构规范 v1.1 + 认证设计文档三份；AI 开场先复述同步点 + 确认角色边界 + 等用户明确放行才写派工。
- 候选任务（待用户拍板）：
  a. 前端 e2e 在 52ad9c6 上回归验证（不带 --project，直接 `pnpm exec playwright test`）。
  b. revoked_reason model docstring 修正（refresh_token.py 第 21~24 行 docstring，三值改两值 + 加注释 "switch_tenant 复用 rotation 字面量，靠 successor_jti=NULL 区分语义"），轻量单 commit。
  c. Week 3 kickoff：决定 scope（候选：基于 zones/demo/ 起首个真实业务模块 / refresh rotation 锁粒度精化 SQLite 路径限定 / 可选后台清理调度器替代手动 cleanup 端点）。
  d. SQLite BEGIN IMMEDIATE 全局事务在生产多 worker 下的锁粒度评估（技术债 1）。
  e. CI 当 PR 触发或 Run 推进后同步 AGENTS.md Current Phase 行的 CI Run 编号。

### 工程纪律（含历史累积，覆盖至 Day 5 Session 2，不得淡出）

1. 顾问只出决策建议/派工提示词/验收清单；不粘源码、不进 Agent Mode、不调 browser_task_tool。
2. 写文档/派工前先把待确认项问全，用户拍完再动笔；不得事后补问题。
3. 未经用户明确指示，不得擅自启动归档/派工写作任务。
4. 归档输出严格按提示词规范：单 markdown 代码块、不嵌套代码块、目录树/配置/代码用缩进、代码块外只一句使用说明。
5. 设计文档/归档由顾问写完整内容，本地 AI IDE 只存文件 + commit，不创作。
6. commit 前本地 AI IDE 执行 git status --short 列文件给用户确认；精确 git add，禁 git add -A 一把梭；保持仓库干净。
7. 版本号必须联网核实贴实际字符串；技术栈版本变更先报备。
8. 带日期文件名以 current-time 为准（不凭直觉顺延）。
9. 归档为滚动替换式：合并历史 + 本次，老内容压缩成结论/纪律，新会话只读这一份。
10. 派工提示词必须一整块可复制 markdown，不散落多段；与给用户看的内容严格分开。
11. 严禁 --no-verify / --force push / 自动 prettier --write 不经确认；pre-commit 三关（ruff/ruff format/mypy）不跳过。
12. pytest-cov 路径用 Python 模块路径（--cov=boxbase.core.security），不用文件系统路径。
13. coverage 必须配 source=["boxbase"]+concurrency=["thread","greenlet"]，否则异步覆盖率虚低。
14. alembic.ini 注释必须 ASCII；script.py.mako 模板含 op/sa import；每次新增 model 后生成迁移并验证 upgrade/downgrade 往返。
15. get_current_user 从 core/security.py 导入（非 dependencies.py）；RequestContext 无 jti，需 jti 场景传 None。
16. require_permission 用 lazy import 避免 core/ 内循环依赖。
17. 测试 email 域名用 @example.com（@test.local 等会被 email-validator 拒）。
18. 派工模板与实际签名/字段不符时，本地 AI IDE 执行前先读源码确认，主动适配并汇报。
19. 模块对外接口契约：每 zone 唯一 router.py+service.py；新增模块 core/router.py 追加一行 include。
20. 【Day 4 立】安全敏感改动（碰会话/rotation/锁/token 语义）必须先出方案给用户确认（STOP 点）再实现，禁止"State assumptions and continue"擅自动手。
21. 【Day 4 立】验收不得只看代码、不得用"假环境/会被自动串行化的测试"充当证据，必须实跑；失败的验证不得随意归因为"测试级问题"放过，必须查到真因（用确定性用例兜底）。
22. 【Day 4 立】token 原文绝不落库，只存 jti / successor_jti 指针；前端 access 存内存、refresh 存 localStorage 且必须尊重后端 refresh 有效期语义。
23. 【Day 4 立】影响全局行为的改动（如 SQLite BEGIN IMMEDIATE 升级所有写事务）必须在代码处注释说明并在交付汇报中明确告知，记入技术债待生产环境重评估。
24. 【Day 5 Session 1 立】文档归真类改动（AGENTS.md / 架构规范 / 归档）必须先出"改后草案 / 关键 diff"给用户审（STOP 点），点头后再出可复制派工块；不得跳过审稿直接派工。
25. 【Day 5 Session 1 立】AGENTS.md 是所有 AI agent（Cursor / Claude Code / Copilot）的单一真相源，且 .github/copilot-instructions.md 已显式指向它；任何"AGENTS.md 与现实不符"的发现属最高优先级技术债，先于任何新功能处理；改动后必须 git grep 双向自检幻影词与引用文件名。
26. 【Day 5 Session 1 立】CI Run 编号 / commit hash / 测试数字等可核实事实必须取自真源（gh / 截图 / git 命令原始输出），无源可取时用明确占位符（如 #TBD）并在能联网时补登，绝不编造。
27. 【Day 5 Session 1 立】归档第一稿派工时，禁止合并 git add/commit/push 到同一派工；先写文件交审，审过后再单独派工提交（写稿与提交分轮）。
28. 【Day 5 Session 1 立】滚动归档的历史累积部分（工程纪律全条 + 历史关键问答 + 历史决策 + 历史关键签名）必须由顾问主笔，本地 AI IDE 不得"概述压缩"；本地 AI IDE 第一稿仅可用于本次新增内容，历史段落必须 verbatim 搬运 Day N-1 归档对应段落。
29. 【Day 5 Session 2 立】Stage A / Stage B 派工必须切死单独 enforce：阶段 A 仅核源码 + 出 diff 交审，禁 git add/commit/push；阶段 B 必须等顾问明确口头放行（"可以阶段 B"）才能执行；diff 必须完整 verbatim 贴回，不接受"已检查 / 已完整核对"等概述。
30. 【Day 5 Session 2 立】"原样贴回 / verbatim"要求必须配硬约束（"不要总结、不要概述、不要 paraphrase"）+ 自检条目明示；本地 AI IDE 任何"自作主张修正"（包括 typo / 标点 / 措辞）必须主动声明"我修了哪几处"，不得静默修改。
31. 【Day 5 Session 2 立】顾问发草案给用户审 ≠ 派落盘工；本地 AI IDE 在用户明确说"派工落盘"或顾问发出可复制派工块之前，禁止把草案落到磁盘；事后核对发现已擅自落盘的，记入"错误与修正"，不为其单独 amend / revert（除非内容失真），但纪律记账。
