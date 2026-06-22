# BoxBase v1.0 工作记忆摘要 — Week 2 Day 5 Session 1 收官（滚动累积版）

## 1. 对话主题与用户意图

- 项目：BoxBase v1.0 —— 轻量级、模块化 Python 多租户 SaaS 框架，16 周完成 v1.0，当前 Week 2 Day 5 Session 1（2026-06-23）。
- 用户角色：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收拍板；本地 AI IDE（Cursor / Claude Code / Copilot）执行代码；会话内 AI 任顾问，只出决策建议 / 派工提示词 / 验收清单 / 归档草稿。
- 顾问交互硬规矩：①未经用户明确放行不得擅自写派工提示词；②给本地 AI IDE 的提示词指令必须放进一整段可复制的内容区块，与给用户看的内容严格分开；③碰安全语义的改动必须先出方案给用户确认（STOP 点）再让本地 AI IDE 动手。
- Week 2 Day 5 Session 1 核心任务（全部完成并 push）：现状盘点（git/grep/试跑测试）→ 抓出三处"文档 vs 现实"对齐项 + 脏工作区 → 用户认 A→B→C 顺序、定 Current Phase = Week 2 Day 5 复盘收尾 → housekeeping commit（.gitignore 加 .tmp/ + .github/copilot-instructions.md 指针文件）→ AGENTS.md 归真（5 处外科手术式修订 + 一次 amend 修正引用错指）→ push 4512459..a2eac4a 落地 → 由顾问写本归档第一稿（首版第一稿由本地 AI IDE 写、Day 4 历史累积被压坏，顾问接手重写）。
- 历史阶段：Week 1 全闭环（基线 dadf307，tag week1-complete @ 07ee750）→ Week 2 Day 1 架构评审拍板 → Day 2 ORM/security/seed（21/21 绿）→ Day 3 core+zones 重构 + 17 端点 + demo zone（61/61 绿，覆盖率 93.83%/100%）→ Day 4 前端登录注册 Dashboard + 竞态修复 + 孤儿 token 根除（70/70 绿 + e2e 6/6，覆盖率 94%/100%，commit 9bfc11b）→ Day 4 收官后追加两笔（e4ab8d9 Day 4 归档入库 + 4512459 一次格式化）→ 本归档（Day 5 Session 1）。

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| —— Week 2 Day 5 Session 1（本次）—— | |
| 同步上下文需要哪些文件？ | AGENTS.md + 平台架构规范 + 认证设计文档 + Day 4 归档；下次重开新会话最小恢复集 = 3 份（最新滚动归档 + 平台架构规范 + 认证设计文档），AGENTS.md 不在恢复集（它是给本地 AI IDE 的执行规则）。 |
| 21 天没动过仓库吗？ | HEAD 已不在 9bfc11b，多两条已 push 提交（e4ab8d9 Day 4 归档入库 + 4512459 一次格式化），无业务代码偷改；tag 仍仅 week1-complete。 |
| 工作区为什么脏？ | .gitignore 多一行 .tmp/（合理）；.github/copilot-instructions.md 是新增未跟踪指针文件（"严格遵守 ../AGENTS.md，单一真相源"，符合 AGENTS.md "不要在工具专属文件里重复规则"原则）。 |
| 文档对齐三项哪些是真账？ | 真账两项：①平台架构规范变更记录只有 2026-05-31 v1.0 一条，refresh_rotation_grace_seconds / successor_jti / BEGIN IMMEDIATE / revoked_reason 四关键词只命中 Day 4 归档、未进规范正文；②AGENTS.md 严重过时，描述幻影架构（org_id+event listener / Casbin+PermissionChecker / fastapi-users 优先 / auth-tenant-rbac-modules 目录 / Current Phase Week 1 完成 + CI Run #9）。Day 4 归档已入库（e4ab8d9）。 |
| 文档归真优先级？ | A 文档归真 > B housekeeping 清脏工作区 > C 可选前端 e2e 验证；实际执行顺序 B → A（B 阻塞 A 的 commit 干净性）。 |
| AGENTS.md 归真改几处？ | 5 处外科手术式修订：①Project Identity 后端栈一行（补 async / pydantic-settings / DIY auth 描述）②Core Design Principles 第 2~4 条（多租户改 tenant_id+with_loader_criteria / RBAC 改简化三表+require_permission / 库优先改"DIY 认证为刻意例外"）③File Organization 整段替换为 core/+zones/+Module Contract ④API Routing Convention 段尾追加一句指向 core/router.py ⑤Current Phase 整段（推进到 Week 2 Day 4 完成 / 现进 Day 5 / CI Run #20）。其余段落零改动。 |
| 必须清除的幻影词？ | fastapi-users（作首选库时）、Casbin、PermissionChecker、org_id、`auth/ tenant/ rbac/ modules/` 目录命名。 |
| CI Run 编号怎么取？ | gh CLI 不可用 + github.com:443 不通；初版用 `Run #TBD` 占位，用户提供 GitHub Actions 截图核实 = Run #20（commit 4512459，main 分支，Status Success，39s，3 job 全绿：lint-and-test 36s / Frontend Lint & Typecheck 22s / Secret Scan TruffleHog 9s）。 |
| Module Contract 引用指向哪份？ | docs/architecture/2026-W2-platform-architecture-design.md（模块契约真相源，章节 3 "模块规范 Zone Contract"）；首版 amend 前误指 auth-tenant-rbac-design.md 已修正。 |
| 归档第一稿谁写？ | 试派工让本地 AI IDE 写第一稿，工程纪律 1~23 条丢失 + Day 4 历史压坏；改由顾问重写，本地 AI IDE 仅落盘覆盖文件 + 单独派工提交。 |
| Day 4 变更记录什么时候补？ | 留待下一会话（Day 5 Session 2）；建议单 commit 一次到位，与 Week 2 retrospective 文档分开 commit。 |
| —— Week 2 Day 4（历史，保留结论）—— | |
| 根目录启动脚本？ | mise.toml（dev / dev:frontend / dev:backend，dev 用 depends 并行）；不放根 package.json。 |
| 前端 token 存哪？ | access 内存 React Context（刷新即失效）；refresh localStorage（必须尊重后端 7 天会话）；启动静默换发；axios/fetch 401 拦截器自动 refresh + rotation 覆盖 localStorage。 |
| refresh 并发竞态根因？ | StrictMode 双挂载 → 两个 init useEffect 用同一 jti 并发 refresh → 先到的 rotation revoke 该 jti，后到的用已 revoke 的 jti → 401 → clearAuth 删掉刚换发的合法 token；本质"并发 refresh 同 jti + rotation 一次性语义"，生产多标签页同样存在。 |
| 竞态修复方案？ | 三层：①前端 init useEffect useRef 去重 ②客户端 refreshAccessToken 单飞锁（init 与 401 拦截器共享）③后端 rotation 宽限放行（rotation-revoke 且宽限窗口内不 401）。 |
| 孤儿 token 是什么？怎么根除？ | 宽限放行时给并发第二个请求签发全新 jti → 多个 active token 悬空到 7 天过期；根除方案 C：B（治本，串行化 rotation + successor_jti 指针让并发请求拿同一 jti）+ A（兜底，删 expires_at<now 的过期 token）+ 手动 superadmin 清理端点。 |
| B 方案 SQLite 怎么串行化？ | SQLite FOR UPDATE 是 no-op；改用 connect 事件设 isolation_level=None + begin 事件发 BEGIN IMMEDIATE（全局生效）；PG 用 with_for_update() 行锁。 |
| B 方案怎么防并发插入重复？ | 插入唯一责任归 Branch A（看到 active 的请求）；Branch B（看到 revoked+rotation+宽限内）纯读 successor_jti 重签、不插入；jti UNIQUE 索引兜底。 |
| 租户名显示成 UUID？ | 后端 /api/users/me 只返回 active_tenant_id；前端额外请求 /api/auth/tenants 匹配出租户名（MembershipResponse 扩 tenant_name/tenant_slug）。 |
| —— Week 2 Day 1-3（历史，保留结论）—— | |
| 目录按层切还是按模块切？ | 垂直切分 Zone：core/ 基础设施 + zones/ 业务模块；models 归模块自身；8 张基础表归 zones/admin/。 |
| 模块对外接口契约？ | 每模块唯一 router.py + service.py；端点>8 拆 routers/，service 函数>10 拆 services/。 |
| coverage 全局虚低？ | 必须配 source=["boxbase"] + concurrency=["thread","greenlet"]，否则异步追踪失效。 |
| get_current_user 在哪？ | core/security.py（不在 dependencies.py）。 |
| RequestContext 有 jti 吗？ | 没有，只有 user_id/active_tenant_id/is_superadmin；需 jti 场景传 None。 |
| 多租户隔离？ | Row-level + tenant_id；ORM with_loader_criteria 强制过滤；PG RLS 第二防线 v1.0 不启用、预留 hook。 |
| 认证库？ | DIY 薄层（pyjwt + pwdlib + FastAPI 依赖注入）；HS256；refresh 存库可撤销 + rotation；access 30min / refresh 7d。 |
| 全局用户模型？ | User 全局唯一（username/email/phone 单列唯一）；经 membership 加入多租户；token 带 active_tenant_id。 |
| 超管？ | 配置注入 superadmin username；系统保留租户；short-circuit 绕过 tenant 过滤 + RBAC。 |
| Membership 唯一约束？ | DB 级 UniqueConstraint(tenant_id,user_id)；is_default 应用层保证。 |
| RefreshToken jti 存什么？ | 明文 UUID 字符串作索引键（token 原文不落库 ≠ jti 不落库）。 |

## 3. 文件与引用内容索引（含关键签名/字段/配置）

### 架构与设计文档（长期有效）

| 文件 | 路径 | 说明 |
|---|---|---|
| 平台架构规范 | docs/architecture/2026-W2-platform-architecture-design.md | core/+zones/ 模块化规范单一真相源；模块契约（Zone Contract）在章节 3；扩展指南；变更记录滚动。⚠️ Day 4 变更记录尚未补登（refresh_rotation_grace_seconds / successor_jti 字段 / BEGIN IMMEDIATE 钩子 / rotation 宽限），下一会话首要任务。 |
| 认证设计评审 | docs/architecture/2026-W2-auth-tenant-rbac-design.md | 认证/多租户/RBAC 详细设计；ER/字段/API/时序图；§2.1 DIY 薄层 vs fastapi-users/authx 决策证据。 |
| Day 4 归档 | docs/decisions/2026-0601-week2-day4-complete.md | Week 2 Day 4 滚动累积版（已被本归档替代为唯一会话状态源）。 |
| 本归档 | docs/decisions/2026-0623-week2-day5-session1.md | Week 2 Day 5 Session 1 滚动累积版（本文件）。 |
| AGENTS.md | AGENTS.md | 所有 AI agent（Cursor/Claude Code/Copilot）执行规则单一真相源；本次已归真至 Week 2 Day 5；不在新会话恢复集。 |
| Copilot 指针 | .github/copilot-instructions.md | 单行指针文件，内容："请阅读并严格遵守 ../AGENTS.md 作为本仓库唯一行为准则。该文件是单一真相源,任何冲突以其为准。" |

### 后端目录结构（最新态，与平台架构规范一致）

    backend/boxbase/
      core/
        base.py          ← AuditMixin + DeclarativeBase
        config.py        ← pydantic-settings；含 refresh_rotation_grace_seconds=10
        database.py      ← async engine + session factory；SQLite BEGIN IMMEDIATE 全局事件钩子
        dependencies.py  ← RequestContext / get_db / apply_*_filter / require_permission(lazy import)
        exceptions.py    ← ErrorResponse + ErrorCode 常量 + 异常处理器
        security.py      ← hash/verify/JWT/get_current_user；rotate_refresh_token(仅测试用，端点不调)
        router.py        ← 平台路由总入口（聚合 admin + demo + health）
      zones/admin/
        models/          ← 8 张基础表；refresh_token.py 含 revoked_at/revoked_reason/successor_jti
        routers/         ← auth.py / users.py / roles.py / admin.py(含 maintenance/cleanup 端点)
        services/        ← auth.py(rotation 重写+清理函数) / users.py / roles.py
        router.py / schemas.py(含 CleanupResponse + MembershipResponse 扩 tenant_name/tenant_slug) / service.py
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
      playwright.config.ts（无具名 project，调用时不要带 --project=chromium）
      package.json(devDep @playwright/test 1.60.0 + test:e2e script)
    mise.toml（根目录唯一启动配置：dev / dev:frontend / dev:backend）

### 关键签名 / 约束（查文档才知道的细节，长期有效）

| 项 | 细节 |
|---|---|
| core/security.py | create_access_token(user_id:UUID, active_tenant_id:UUID, username:str)；create_refresh_token(jti:str, user_id:UUID)；decode_access_token / decode_refresh_token（无通用 decode_token）；get_current_user(token,db) 超管 short-circuit + active membership 校验 |
| RequestContext | 字段 user_id / active_tenant_id / is_superadmin（无 jti） |
| RefreshToken 模型 | jti 明文 UUID + ix_refresh_token_jti UNIQUE 索引；status active/revoked；revoked_at(DateTime tz)；revoked_reason("rotation"/"logout")；successor_jti(String(64) nullable，仅存 jti 不存 token 原文) |
| services/auth.py refresh_token | SELECT...with_for_update()；Branch A(status=active)→revoke+写 successor_jti+INSERT 新 active 行；Branch B(revoked+reason=rotation+宽限内)→读 successor_jti 重签、不 INSERT；reason≠rotation 或超窗口→401；successor_jti 为 None→401 |
| services/auth.py cleanup_expired_refresh_tokens | DELETE WHERE expires_at<now()，返回删除条数；只删过期、不动在用 |
| services/auth.py switch_tenant | 路由传 current_jti=None（实际不 revoke）；若 revoke 则 reason=rotation 但不设 successor_jti（故旧 jti 宽限内仍 401，语义正确） |
| 清理端点 | POST /api/admin/maintenance/cleanup-refresh-tokens；superadmin only；返回 CleanupResponse{deleted:int}；普通用户 403 |
| 前端 token 存储 | access→内存 React Context（刷新即失效，正常）；refresh→localStorage（尊重 7 天）；启动 init 静默换发；401 拦截器自动 refresh + rotation 覆盖 localStorage |
| SQLite 串行化钩子 | connect 事件 isolation_level=None（阻止 do_begin 发 DEFERRED BEGIN）+ begin 事件 exec_driver_sql("BEGIN IMMEDIATE")；全局生效；PG 不注册此钩子，用 with_for_update() |
| config 配置项 | database_url / secret_key / superadmin_username(默认"") / access_token_expire_minutes=30 / refresh_token_expire_days=7 / refresh_rotation_grace_seconds=10 |
| 17+1 admin 端点 | auth(register/login/refresh/logout/switch-tenant/tenants) + users/me + users(GET/POST) + memberships(PATCH/DELETE) + roles(GET/POST/{id}/permissions) + permissions + admin(tenants/users) + admin/maintenance/cleanup-refresh-tokens(Day 4 新增) |

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| git（本次） | 只读盘点 + 提交 + push | git status -sb / log --oneline -25 / log 9bfc11b..HEAD / grep；本次新增两笔 commit 已 push（4512459..a2eac4a） |
| pytest（本次） | 后端回归 | uv run pytest -q = 70 passed / 10 warnings / 32.86s（与 Day 4 收官一致，未回归） |
| pytest-cov（本次） | 覆盖率 | 全局 94%（门禁 80%）/ boxbase.core.security 100%（门禁 95%） |
| pnpm/playwright（本次） | 前端 e2e | `pnpm exec playwright test --project=chromium` 报错 "Available projects: """，因 playwright.config.ts 无具名 project；按只读纪律未修配置；e2e 在 a2eac4a 上未重新验证 |
| Get-Command gh（本次） | gh 可用性 | gh CLI 不可用 |
| curl / Invoke-WebRequest（本次） | 网络验证 | github.com:443 不通（端口连接失败） |
| GitHub Actions 截图（本次） | CI Run 编号取数 | 用户提供截图核实 Run #20，commit 4512459，39s 全绿 |
| git grep（本次） | 幻影词自检 | AGENTS.md 中 fastapi-users（首选）/Casbin/PermissionChecker/org_id 全部清空；platform-architecture-design.md 引用至少 1 处（Module Contract 段尾） |
| mise（历史 Day 4） | 根目录启动 | mise run dev 并行起前后端 |
| playwright（历史 Day 4） | e2e 竞态实测 | B1~B6 全过；多标签页并发用 context.newPage() 共享 localStorage |
| alembic（历史 Day 4） | 迁移 | e0757aa877d0 + a1b2c3d4e5f6；upgrade/downgrade 往返验证 |
| ruff/mypy/tsc（历史） | 静态检查 | 全过；SQLAlchemy 类型用 type:ignore[arg-type/union-attr] 精确标记 |

## 5. 决策与结论（含历史累积）

### Week 2 Day 5 Session 1 决策（本次，长期有效）

1. 文档归真优先级：A 文档归真 > B housekeeping 清脏工作区 > C 可选 e2e 验证；实际执行 B→A，避免 housekeeping 脏污染 AGENTS.md commit。
2. AGENTS.md 归真定位为外科手术式修订：仅改 5 处（Project Identity 后端栈 / Core Design Principles 第 2-4 条 / File Organization 整段 / API Routing Convention 段尾追加 / Current Phase 整段），其它段落零改动；Shell Environment / Coding Standards / TDD / Forbidden Actions / Language Policy 等核对仍准确，不动。
3. 幻影词清单（必须从 AGENTS.md 中清除且不得复活）：fastapi-users（作首选库时）、Casbin、PermissionChecker、org_id、`auth/ tenant/ rbac/ modules/` 目录命名。
4. 多租户描述统一口径：tenant_id + with_loader_criteria 强制过滤（tenant_id + 软删 deleted_at IS NULL）；PG RLS 第二防线 v1.0 不启用、预留 hook；不再用 SQLAlchemy event listeners 表述。
5. RBAC 描述统一口径：简化三表（Role / Permission + 角色挂 Membership）+ resource:action 字符串 + tenant-scoped；走 require_permission 依赖；Casbin v1.0 不引入，引入需显式决策记录。
6. 库优先原则补刻意例外：开源优先（PyJWT / pwdlib / slowapi / secure / sse-starlette / LiteLLM / fastapi-mail）；auth 是刻意例外（DIY core/security 薄层），决策见 auth-tenant-rbac-design.md §2.1。
7. Module Contract（Zone Contract）真相源：docs/architecture/2026-W2-platform-architecture-design.md 章节 3，不是 auth-tenant-rbac-design.md。
8. CI Run 编号绝不编造：无源（gh 不可用 + 网络不通）时用 `Run #TBD` 占位 + 后续补登；本次由用户截图核实为 Run #20。
9. 上下文恢复最小集 = 3 份：最新滚动会话归档 + 平台架构规范 + 认证设计文档；AGENTS.md 不在恢复集（它是给本地 AI IDE 的执行规则）。
10. 滚动归档纪律延续：本归档发布后即替代 Day 4 归档作为唯一会话状态源；新会话只读这一份。
11. 归档第一稿派工策略调整：实测让本地 AI IDE 写第一稿在"历史累积保留"维度失守（工程纪律 1-23 条丢失），改由顾问写第一稿全文、本地 AI IDE 仅落盘覆盖 + 单独派工提交；写稿与提交派工严格分轮。
12. Day 5 Session 2 候选（待用户拍）：架构规范补 Day 4 变更记录（单 commit）+ Week 2 retrospective 文档（独立 commit）+ 前端 e2e 在 a2eac4a 上回归 + 决定 Week 3 scope。

### 历史决策（Week 2 Day 1-4，长期有效，保留结论）

1. 模块化架构：core/ 基础设施 + zones/ 业务；禁模块间横向 import；禁 core/ 反向 import zone；每模块唯一 router.py+service.py 入口；端点>8 拆 routers/，service>10 拆 services/。
2. 多租户隔离：Row-level + tenant_id；ORM with_loader_criteria 强制过滤（tenant + deleted_at）；PG RLS v1.0 不启用、预留 hook。
3. 认证：DIY security 薄层（pyjwt+pwdlib）；HS256；refresh 存库可撤销 + rotation；access 30min/refresh 7d；全局用户模型（User 全局唯一，经 membership 入多租户，token 带 active_tenant_id）。
4. 超管：配置注入 username + 系统保留租户 + short-circuit 绕过 tenant 过滤与 RBAC。
5. RBAC：简化三表 + resource:action；seed 固定权限（user:read/write、role:read/write/assign）+ 默认角色（owner/admin/member）；对象级放 service 层。
6. AuditMixin 5 字段（created_at/updated_at/created_by/updated_by/deleted_at）；id 用 Uuid；软删 deleted_at 与 ORM 过滤联动。
7. coverage 必须配 source=["boxbase"]+concurrency=["thread","greenlet"]；seed.py omit。
8. 前端栈：React 19.2 + Vite 8 + TS 6 + AntD v6 + react-router-dom v7；pnpm 10.33；Node 22(mise)；Pro Components 延后。
9. Day 4：mise.toml 根目录启动；前端 token 存储（access 内存 / refresh localStorage 尊重 7 天）；refresh 竞态三层修复；孤儿 token 根除（successor_jti + 串行化 + 过期清理）；switch_tenant 不设 successor_jti。
10. successor_jti 只存 jti 不存 token 原文（守"token 原文不落库"纪律）；jti UNIQUE 索引作并发插入兜底。

### 已知技术债 / 设计记录（Week 3 评估）

1. 全局 SQLite BEGIN IMMEDIATE 事务变更：所有 SQLite 写事务升级为 IMMEDIATE，单用户 dev / 低并发可接受（WAL 下读不阻塞）；多 worker / 高并发生产需重新评估锁粒度（仅串行化 refresh 而非全局）。
2. 孤儿 token 已从根上解决（successor_jti + 串行化），但 rotation 宽限窗口（10s）机制本身保留，作为设计记录。
3. 平台架构规范 Day 4 变更记录尚未补登（refresh_rotation_grace_seconds 配置 / RefreshToken 三字段 / SQLite BEGIN IMMEDIATE 钩子 / rotation 宽限），Day 5 Session 2 首要任务。
4. 前端 e2e 在 a2eac4a 上未回归验证（playwright.config.ts 无具名 project，调用姿势需用不带 --project 的 `pnpm exec playwright test`）。
5. AGENTS.md 中 CI Run #20 已据实填写；后续 CI run 推进后需同步更新。
6. 历史扩展点（v1.0 不实现）：部门/分组（通用 group + membership_groups 挂 membership 层）；PG RLS 第二防线；access token 即时吊销；ABAC/五表 RBAC。

## 6. 错误与修正（含历史累积）

| 错误/偏差 | 修正/教训 |
|---|---|
| 本次：首版 AGENTS.md 改动 3 末尾 Module Contract 引用错指为 auth-tenant-rbac-design.md（应为 platform-architecture-design.md）| 顾问审 diff 时抓出；amend 修正（一行删一行加，无新 commit）。教训：原派工里写的就是 platform-，落地复制时弄反；今后涉及多份相似文件名的引用，落地后必须 git grep 双向自检（`auth-tenant-rbac-design.md` 仅应在 Core Principles 第 4 条 + Current Phase Day 1 出现，`platform-architecture-design.md` 至少在 Module Contract 段尾出现）。|
| 本次：Commit 2 卡在 CI Run 编号无法在线获取 | gh 不可用 + 网络不通；首版用 `Run #TBD` 占位推进，用户提供 Actions 截图后改为 `Run #20`；立纪律 26（编号绝不编造，无源用占位符 + 后续补登）。|
| 本次：playwright e2e 调用姿势错（带 --project=chromium）| 归因"配置无具名 project"正确；但顺手验证 e2e 在新 HEAD 上是否仍 6/6 这事被搁置，需 Day 5 Session 2 或 Week 3 前补做（不带 --project 直接 `pnpm exec playwright test`）。|
| 本次：归档第一稿派工失守 | 本地 AI IDE 第一稿丢失 Day 4 工程纪律 1-23 条 + Day 4 历史问答/结论被压坏到信息丢失；顾问接手重写本归档全文；立纪律 27（写稿与提交派工分轮，禁止合并 git add/commit/push 到写稿派工）+ 调整 28（滚动归档历史累积保留必须由顾问主笔，本地 AI IDE 仅落盘）。|
| 历史 Day 4：mise.toml dev:frontend 未先装依赖致启动失败 | 手动 pnpm install 一次；不必每次 install。|
| 历史 Day 4：前端 token 存储首版设计成刷新即失效（破坏 7 天会话）| 改为 refresh 存 localStorage + 启动静默换发。|
| 历史 Day 4：refresh 并发竞态（StrictMode 双挂载同 jti）| 三层修复；e2e B1 从 67% 失败→0 失败。|
| 历史 Day 4：宽限放行产生孤儿 token | 改 successor_jti 指针 + 串行化，Branch B 纯读不插入。|
| 历史 Day 4：Part B 首版绕过 STOP 点自行实现（"State assumptions and continue"）| 用户纠正；后续两次 STOP 均守住；立为强纪律 20。|
| 历史 Day 4：并发测试用 :memory:+StaticPool 被假串行化，却归因为"测试问题"宣布可行 | 用户驳回；改用确定性 Branch B 测试（造 revoked+successor 态→旧 jti 二次 refresh→验 active 行数不变）；立纪律 21。|
| 历史 Day 4：运行库漏跑 successor_jti 迁移致 login 500 | curl 定位真因 + alembic upgrade head 修复；e2e 随即 6/6（诚实排查，未甩锅）。|
| 历史 Day 4：根目录残留临时 npm 产物（playwright 临时装）| 扶正进 frontend devDep + e2e/，清理根目录，精确 git add 不用 -A。|
| 历史：coverage 异步追踪失效虚低 75.93% | 加 source+concurrency → 93.83%。|
| 历史：派工模板与实际签名不符 | 本地 AI IDE 执行前先读源码确认，主动适配。|
| 历史：department_id 错放 USER 表 | 部门归位 membership 层，v1.0 不建。|
| 历史：alembic.ini 中文注释 GBK 失败 | 注释必须 ASCII。|

## 7. 讨论演变（文字描述）

会话开场，用户提供 4 份引用文档（AGENTS.md + 平台架构规范 + 认证设计文档 + Day 4 归档）启动 Week 2 Day 5 复盘收尾，并复述两条交互纪律（未放行不擅自派工、提示词单独成可复制块）。顾问读档后做现状盘点，先列出三处"文档 vs 现实"对齐项的怀疑（架构规范变更记录可能没补、AGENTS.md 可能过时、Day 4 归档可能未入库），并提示这是 Day 4 收官到 06-23 之间 21 天的首次会话，需先确认仓库是否还在 9bfc11b。

用户授权出只读盘点提示词。本地 AI IDE 跑回完整原始输出：HEAD 已推进到 4512459（多两条已 push 提交：e4ab8d9 Day 4 归档入库 + 4512459 一次格式化），无业务代码偷改；工作区脏（M .gitignore + ?? .github/copilot-instructions.md）；架构规范变更记录确认只有 v1.0 一条、四个 Day 4 关键词全部只命中 Day 4 归档；AGENTS.md 严重过时（描述 org_id+event listener / Casbin+PermissionChecker / fastapi-users 优先 / auth-tenant-rbac-modules 目录 / Current Phase Week 1）；Day 4 归档已入库（e4ab8d9）；后端 70 passed 复跑健康；前端 e2e 因 playwright.config.ts 无具名 project 调用失败但属配置认知问题非回归。

顾问梳理出 AGENTS.md 已被 .github/copilot-instructions.md 显式指向，过时的它现在会主动把所有 AI agent 带向幻影架构，是最高优先级技术债，建议优先级 A→B→C（A 文档归真 / B housekeeping / C 可选 e2e）。用户认顺序，定 Current Phase = Week 2 Day 5 复盘收尾。顾问随即出 AGENTS.md 5 处改后草案给用户审：Project Identity 后端栈一行精确补全；Core Design Principles 第 2-4 条改为 tenant_id+with_loader_criteria / 简化三表 RBAC / DIY auth 作刻意例外；File Organization 整段替换为 core/+zones/+Module Contract；API Routing Convention 段尾追加一句指向 core/router.py；Current Phase 整段推进到 Week 2 Day 4 完成 / 进入 Day 5。用户认后，顾问出分两 commit 派工块（housekeeping → AGENTS.md 归真）。

本地 AI IDE 落地 Commit 1（6db91dc）顺利、工作区清空。Commit 2 卡在 CI Run 编号取数：gh CLI 不可用、Invoke-WebRequest 与 curl 都拿不到 github.com:443。本地 AI IDE 严格按派工"两条路径都拿不到就停下来汇报"执行。顾问判断 CI 编号属注释性信息、不是行为依据，主张用 `Run #TBD` 占位推进、不让幻影架构 AGENTS.md 多停一天，遂出占位派工。但用户随即提供 GitHub Actions 截图核实 Run #20（commit 4512459，39s 全绿，3 job 详情），顾问立即作废 TBD 派工、改出据实编号派工。本地 AI IDE 落地 Commit 2，diff 完整贴回。

顾问审 diff 时抓出 Module Contract 段尾引用错指为 auth-tenant-rbac-design.md（应为 platform-architecture-design.md），原派工写的本是后者落地复制时弄反。出 amend 派工，本地 AI IDE 一行删一行加修正、git grep 双向自检通过、amend 上一笔（HEAD 推进至 a2eac4a）。顾问放行 push，本地 AI IDE 推送 4512459..a2eac4a 落地、HEAD 与 origin/main 同步。

收尾时用户问下次重开会话需要几份文件恢复上下文。顾问答最小集 3 份（最新滚动归档 + 平台架构规范 + 认证设计文档），并指出当前 Day 5 Session 1 状态只活在对话里、需先归档兜底。用户认派工让本地 AI IDE 写第一稿。本地 AI IDE 写完贴回，顾问审稿发现工程纪律 1-23 条整段丢失（仅写 24-27）、Day 4 历史问答和决策被压坏到信息丢失粒度，按用户预案"不行的话你再写"接手重写，并把"派工写稿失守"立为新纪律 28。本归档（顾问主笔版）即为第二稿。

## 8. 当前状态与后续步骤

### Git 状态

- 最新 commit：a2eac4a（origin/main 同步，HEAD 与 origin/main 一致）
- 标签：仅 week1-complete @ 07ee750
- Day 5 Session 1 提交链：4512459 → 6db91dc（chore: ignore .tmp/ and add copilot pointer to AGENTS.md）→ a2eac4a（docs(agents): align AGENTS.md with real architecture (zones/, tenant_id, DIY auth) and advance Current Phase to Week 2 Day 5）
- 历史提交链：9bfc11b → e4ab8d9（docs: add Week 2 Day 4 archive）→ 4512459（style: fix formatting (ruff + prettier)）→ 本会话两笔
- 待提交：本归档 docs/decisions/2026-0623-week2-day5-session1.md（用户手动覆盖落盘后，由本地 AI IDE 单独派工提交，建议 message：docs: add Week 2 Day 5 session 1 archive）
- 仓库状态：工作区干净（除本归档文件待落盘），无其它临时产物

### Completed

- Week 1 全闭环（dadf307，tag week1-complete @ 07ee750）
- Week 2 Day 1 架构评审；Day 2 ORM/security/seed（21/21）；Day 3 core+zones+17 端点（61/61，93.83%/100%）；Day 4 前端 + 竞态修复 + 孤儿根除（70/70 + e2e 6/6，94%/100%，commit 9bfc11b）
- Day 4 后追加：e4ab8d9 Day 4 归档入库 + 4512459 一次格式化
- Week 2 Day 5 Session 1：现状盘点（git/grep/测试/网络/CI 截图）+ housekeeping commit（6db91dc）+ AGENTS.md 归真 commit（a2eac4a，含 amend 修正 Module Contract 引用）+ push 4512459..a2eac4a；后端 70/70 复跑确认未回归（94%/100%）

### Next Steps（Week 2 Day 5 Session 2，新会话）

- 新会话同时提供本归档 + 平台架构规范 + 认证设计文档三份；AI 开场先复述同步点 + 确认角色边界 + 等用户明确放行才写派工。
- 候选任务（待用户拍板）：
  a. 架构规范 docs/architecture/2026-W2-platform-architecture-design.md 补 Day 4 变更记录（4.4 配置加 refresh_rotation_grace_seconds=10；4.5 security 补 rotation 宽限语义；5.2 RefreshToken 关键约束加 revoked_at/revoked_reason/successor_jti 三字段；database.py 描述补 SQLite BEGIN IMMEDIATE 全局事务钩子并标注技术债；末尾变更记录表追加 v1.1 行）。建议单 commit 一次到位。
  b. Week 2 retrospective 独立文档（docs/retrospectives/2026-W2-retrospective.md），与上一项分开 commit。
  c. 前端 e2e 在 a2eac4a 上回归验证（不带 --project，直接 `pnpm exec playwright test`）。
  d. 评估全局 SQLite BEGIN IMMEDIATE 事务在生产多 worker 下的锁粒度（技术债 1）。
  e. 决定 Week 3 scope：基于 zones/demo/ 起首个真实业务模块 / refresh rotation 锁粒度精化 / 可选后台清理调度器。

### 工程纪律（含历史累积，覆盖至 Day 5 Session 1，不得淡出）

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
26. 【Day 5 Session 1 立】CI Run 编号 / commit hash / 测试数字等可核实事实必须取自真源（gh / 截图 / git 命令原始输出），无源可取时用明确占位符（如 `#TBD`）并在能联网时补登，绝不编造。
27. 【Day 5 Session 1 立】归档第一稿派工时，禁止合并 git add/commit/push 到同一派工；先写文件交审，审过后再单独派工提交（写稿与提交分轮）。
28. 【Day 5 Session 1 立】滚动归档的历史累积部分（工程纪律全条 + 历史关键问答 + 历史决策 + 历史关键签名）必须由顾问主笔，本地 AI IDE 不得"概述压缩"；本地 AI IDE 第一稿仅可用于本次新增内容，历史段落必须 verbatim 搬运 Day N-1 归档对应段落（首次实测本地 AI IDE 在保留维度失守）。
