# BoxBase v1.0 工作记忆摘要 — Week 2 Day 4 收官（滚动累积版）

## 1. 对话主题与用户意图

- 项目：BoxBase v1.0 —— 轻量级、模块化 Python 多租户 SaaS 框架，16 周完成 v1.0，当前 Week 2 Day 4（2026-06-01）。
- 用户角色：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收拍板；本地 AI IDE（Cursor / Claude Code / CodeBuddy）执行代码；会话内 AI 任顾问，只出决策建议 / 派工提示词 / 验收清单。
- 顾问交互硬规矩：①未经用户明确放行不得擅自写派工提示词；②给本地 AI IDE 的提示词指令必须放进一整段可复制的内容区块，与给用户看的内容严格分开；③碰安全语义的改动必须先出方案给用户确认（STOP 点）再让本地 AI IDE 动手。
- Week 2 Day 4 核心任务（全部完成并 commit）：mise 根目录启动脚本 → 前端登录/注册/Dashboard 页 + 后端联调 → 修复 refresh 并发竞态（前端去重 + 客户端单飞锁 + 后端 rotation 宽限）→ 租户名显示 → playwright e2e 扶正 → 根除孤儿 refresh token（successor_jti 指针 + 串行化 rotation + 过期清理端点）。
- 历史阶段：Week 1 全闭环（基线 dadf307，tag week1-complete @ 07ee750，CI Run #14 全绿）→ Week 2 Day 1 架构评审拍板 → Day 2 ORM/security/seed（21/21 绿）→ Day 3 core+zones 重构 + 17 端点 + demo zone（61/61 绿，覆盖率 93.83%/100%）→ Day 4 前端 + 竞态修复 + 孤儿根除（本归档）。

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| —— Week 2 Day 4（本次）—— | |
| 根目录快速启动脚本怎么做？ | 用 mise.toml（不放根目录 package.json）；dev/dev:frontend/dev:backend 三 task；dev 用 depends 并行 |
| 前端依赖未装致 mise run dev 失败？ | 手动在 frontend 下 pnpm install 一次即可，不改 mise.toml（不必每次启动都 install） |
| API 还要手动测试吗？ | 不要，自动化测试已覆盖；Day 4 跳过手动测试 |
| 登录后 token 怎么存（安全优先）？ | access 存内存(Context)；refresh 存 localStorage（必须尊重后端 7 天会话，刷新/关标签页不能失效）；启动时内存无 access 但有 refresh 则静默换发 |
| 注册后行为？ | 不自动登录，跳回 /login 提示"注册成功，请登录" |
| 多租户切换 UI？ | v1.0 登录后静默进默认租户，不做租户选择 UI |
| refresh 刷新页面偶发 401 掉登录态根因？ | StrictMode 双挂载 → 两个 init useEffect 用同一 jti 并发 refresh → 先到的 rotation revoke 该 jti，后到的用已 revoke 的 jti → 401 → clearAuth 删掉刚换发的合法 token；本质是"并发 refresh 同 jti + rotation 一次性语义"，生产多标签页同样存在 |
| 竞态修复方案？ | 三层：①前端 init useEffect useRef 去重 ②客户端 refreshAccessToken 单飞锁（init 与 401 拦截器共享）③后端 rotation 宽限放行（rotation-revoke 且宽限窗口内不 401） |
| 孤儿 token 是什么？怎么根除？ | 宽限放行时给并发第二个请求签发全新 jti → 多个 active token 悬空到 7 天过期；根除方案 C：B（治本，串行化 rotation + successor_jti 指针让并发请求拿同一 jti）+ A（兜底，删 expires_at<now 的过期 token）+ 手动清理端点 |
| 孤儿清理触发方式？ | 手动 superadmin 端点，不引调度器 |
| B 方案 SQLite 怎么串行化？ | SQLite FOR UPDATE 是 no-op；改用 connect 事件设 isolation_level=None + begin 事件发 BEGIN IMMEDIATE（全局生效）；PG 用 with_for_update() 行锁 |
| B 方案怎么防并发插入重复？ | 插入唯一责任归 Branch A（看到 active 的请求）；Branch B（看到 revoked+rotation+宽限内）纯读 successor_jti 重签、不插入；jti UNIQUE 索引兜底 |
| 租户名显示成 UUID？ | 后端 /api/users/me 只返回 active_tenant_id；前端额外请求 /api/auth/tenants 匹配出租户名（MembershipResponse 扩 tenant_name/tenant_slug） |
| —— Week 2 Day 3（历史）—— | |
| 目录按层切还是按模块切？ | 垂直切分 Zone：core/ 基础设施 + zones/ 业务模块；models 归模块自身；8 张基础表归 zones/admin/ |
| 模块对外接口契约？ | 每模块唯一 router.py + service.py；端点>8 拆 routers/，service 函数>10 拆 services/ |
| coverage 全局虚低？ | 必须配 source=["boxbase"] + concurrency=["thread","greenlet"]，否则异步追踪失效 |
| get_current_user 在哪？ | core/security.py（不在 dependencies.py） |
| RequestContext 有 jti 吗？ | 没有，只有 user_id/active_tenant_id/is_superadmin；需 jti 场景传 None |
| —— Week 2 Day 1-2（历史）—— | |
| 多租户隔离？ | Row-level + tenant_id；ORM with_loader_criteria 强制过滤；PG RLS 第二防线 v1.0 不启用 |
| 认证库？ | DIY 薄层（pyjwt + pwdlib + FastAPI 依赖注入）；HS256；refresh 存库可撤销 + rotation；access 30min / refresh 7d |
| 全局用户模型？ | User 全局唯一(username/email/phone 单列唯一)；经 membership 加入多租户；token 带 active_tenant_id |
| 超管？ | 配置注入 superadmin username；系统保留租户；short-circuit 绕过 tenant 过滤 + RBAC |
| Membership 唯一约束？ | DB 级 UniqueConstraint(tenant_id,user_id)；is_default 应用层保证 |
| RefreshToken jti 存什么？ | 明文 UUID 字符串作索引键（token 原文不落库 ≠ jti 不落库） |

## 3. 文件与引用内容索引（含关键签名/字段/配置）

### 架构与设计文档（长期有效）

| 文件 | 路径 | 说明 |
|---|---|---|
| 平台架构规范 | docs/architecture/2026-W2-platform-architecture-design.md | core/+zones/ 模块化规范单一真相源；扩展指南；变更记录滚动 |
| 认证设计评审 | docs/architecture/2026-W2-auth-tenant-rbac-design.md | 认证/多租户/RBAC 详细设计；ER/字段/API/时序图 |
| Day 3 归档 | docs/decisions/2026-0531-week2-day3-complete.md | Week 2 Day 3 滚动累积版 |
| Day 4 归档（本文件） | docs/decisions/2026-0601-week2-day4-complete.md | Week 2 Day 4 滚动累积版 |

### 后端目录结构（最新态）

    backend/boxbase/
      core/
        base.py          ← AuditMixin + DeclarativeBase
        config.py        ← pydantic-settings；新增 refresh_rotation_grace_seconds=10
        database.py      ← async engine + session factory；新增 SQLite BEGIN IMMEDIATE 全局事件钩子
        dependencies.py  ← RequestContext / get_db / apply_*_filter / require_permission(lazy import)
        exceptions.py    ← ErrorResponse + ErrorCode 常量 + 异常处理器
        security.py      ← hash/verify/JWT/get_current_user；rotate_refresh_token(仅测试用，端点不调)
        router.py        ← 平台路由总入口（聚合 admin + demo + health）
      zones/admin/
        models/          ← 8 张基础表；refresh_token.py 新增 revoked_at/revoked_reason/successor_jti
        routers/         ← auth.py / users.py / roles.py / admin.py(新增清理端点)
        services/        ← auth.py(rotation 重写+清理函数) / users.py / roles.py
        router.py / schemas.py(新增 CleanupResponse + MembershipResponse 扩 tenant_name/tenant_slug) / service.py
      zones/demo/        ← 示例扩展模块
      tools/seed.py
      main.py
    backend/alembic/versions/  ← e0757aa877d0(revoked_at/reason) + a1b2c3d4e5f6(successor_jti)
    frontend/
      src/api/client.ts            ← authFetch + refreshAccessToken(单飞锁)；access 内存 / refresh localStorage
      src/contexts/AuthContext.tsx ← AuthProvider+useAuth；init useEffect useRef 去重；login/logout/register
      src/components/RootLayout.tsx ← 挂 AuthProvider
      src/pages/  LoginPage / RegisterPage / DashboardPage(租户名显示) / HomePage(重定向)
      src/router.tsx
      e2e/auth.spec.ts             ← playwright B1~B6 回归用例
      playwright.config.ts；package.json(devDep @playwright/test 1.60.0 + test:e2e script)
    mise.toml（根目录唯一启动配置：dev / dev:frontend / dev:backend）

### 关键签名 / 约束（查文档才知道的细节）

| 项 | 细节 |
|---|---|
| core/security.py | create_access_token(user_id:UUID, active_tenant_id:UUID, username:str)；create_refresh_token(jti:str, user_id:UUID)；decode_access_token / decode_refresh_token（无通用 decode_token）；get_current_user(token,db) 超管 short-circuit + active membership 校验 |
| RequestContext | 字段 user_id / active_tenant_id / is_superadmin（无 jti） |
| RefreshToken 模型 | jti 明文 UUID + ix_refresh_token_jti UNIQUE 索引；status active/revoked；revoked_at(DateTime tz)；revoked_reason("rotation"/"logout")；successor_jti(String(64) nullable，仅存 jti 不存 token 原文) |
| services/auth.py refresh_token | SELECT...with_for_update()；Branch A(status=active)→revoke+写 successor_jti+INSERT 新 active 行；Branch B(revoked+reason=rotation+宽限内)→读 successor_jti 重签、不 INSERT；reason≠rotation 或超窗口→401；successor_jti 为 None→401 |
| services/auth.py cleanup_expired_refresh_tokens | DELETE WHERE expires_at<now()，返回删除条数；只删过期、不动在用 |
| services/auth.py switch_tenant | 路由传 current_jti=None（实际不 revoke）；若 revoke 则 reason=rotation 但不设 successor_jti（故旧 jti 宽限内仍 401，语义正确） |
| 清理端点 | POST /api/admin/maintenance/cleanup-refresh-tokens；superadmin only；返回 CleanupResponse{deleted:int}；普通用户 403 |
| 前端 token 存储 | access→内存 React Context（刷新即失效，正常）；refresh→localStorage（尊重 7 天）；启动 init 静默换发；axios/fetch 401 拦截器自动 refresh + rotation 覆盖 localStorage |
| SQLite 串行化钩子 | connect 事件 isolation_level=None（阻止 do_begin 发 DEFERRED BEGIN）+ begin 事件 exec_driver_sql("BEGIN IMMEDIATE")；全局生效；PG 不注册此钩子，用 with_for_update() |
| config 配置项 | database_url / secret_key / superadmin_username(默认"") / access_token_expire_minutes=30 / refresh_token_expire_days=7 / refresh_rotation_grace_seconds=10 |
| 17 admin 端点 | auth(register/login/refresh/logout/switch-tenant/tenants) + users/me + users(GET/POST) + memberships(PATCH/DELETE) + roles(GET/POST/{id}/permissions) + permissions + admin(tenants/users)；Day 4 新增 maintenance/cleanup 端点 |

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| mise（本次） | 根目录启动 | mise run dev 并行起前后端；首跑因 frontend 未 pnpm install 失败，手动装一次后正常 |
| playwright（本次） | 前端 e2e + 竞态实测 | 扶正进 frontend devDep；B1~B6 全过；多标签页并发用 context.newPage() 共享 localStorage |
| pytest（本次） | 后端回归 | 61→64→66→68→70 全过 |
| pytest-cov（本次） | 覆盖率 | 全局 94%（门禁 80%）/ security 100%（门禁 95%） |
| 诊断日志（本次） | 定位竞态根因 | 加临时 console.log 抓到 StrictMode 双挂载 + 同 jti 并发；修复后已回退 |
| alembic（本次） | 迁移 | e0757aa877d0 + a1b2c3d4e5f6；upgrade/downgrade 往返验证；运行库漏迁移致 login 500，补 upgrade head 修复 |
| ruff/mypy/tsc（本次） | 静态检查 | 全过；SQLAlchemy 类型用 type:ignore[arg-type/union-attr] 精确标记 |
| curl（本次） | API 排查 | e2e 失败时 curl 定位到 login 500 真因=运行库缺 successor_jti 列 |

## 5. 决策与结论（含历史累积）

### Week 2 Day 4 决策（本次，长期有效）

1. 根目录启动用 mise.toml（dev/dev:frontend/dev:backend，dev 用 depends 并行），不放根 package.json。
2. 前端 token 存储：access 内存、refresh localStorage（尊重后端 7 天会话，刷新/关标签页不失效），启动静默换发。
3. refresh 竞态三层修复：①前端 init useRef 去重 ②客户端 refreshAccessToken 单飞锁 ③后端 rotation 宽限放行。
4. 孤儿根除（方案 C）：B 治本 = SQLite BEGIN IMMEDIATE / PG FOR UPDATE 串行化 rotation + successor_jti 指针（Branch A 唯一插入、Branch B 纯读重签同 jti）；A 兜底 = 删过期 token；手动 superadmin 清理端点，不引调度器。
5. successor_jti 只存 jti 不存 token 原文（守"token 原文不落库"纪律）；jti UNIQUE 索引作并发插入兜底。
6. switch_tenant 不设 successor_jti，旧 jti 宽限内 refresh 仍 401（语义正确）。
7. 租户名显示走前端额外请求 /api/auth/tenants（MembershipResponse 扩 tenant_name/tenant_slug）。
8. playwright 扶正为 frontend devDep + frontend/e2e/ 回归资产，不留根目录 npm 临时产物。

### 历史决策（Day 1-3，长期有效，保留结论）

1. 模块化架构：core/ 基础设施 + zones/ 业务；禁模块间横向 import；禁 core/ 反向 import zone；每模块唯一 router.py+service.py 入口；端点>8 拆 routers/，service>10 拆 services/。
2. 多租户隔离：Row-level + tenant_id；ORM with_loader_criteria 强制过滤（tenant + deleted_at）；PG RLS v1.0 不启用、预留 hook。
3. 认证：DIY security 薄层（pyjwt+pwdlib）；HS256；refresh 存库可撤销 + rotation；access 30min/refresh 7d；全局用户模型（User 全局唯一，经 membership 入多租户，token 带 active_tenant_id）。
4. 超管：配置注入 username + 系统保留租户 + short-circuit 绕过 tenant 过滤与 RBAC。
5. RBAC：简化三表 + resource:action；seed 固定权限（user:read/write、role:read/write/assign）+ 默认角色（owner/admin/member）；对象级放 service 层。
6. AuditMixin 5 字段（created_at/updated_at/created_by/updated_by/deleted_at）；id 用 Uuid；软删 deleted_at 与 ORM 过滤联动。
7. coverage 必须配 source=["boxbase"]+concurrency=["thread","greenlet"]；seed.py omit。
8. 前端栈：React 19.2 + Vite 8 + TS 6 + AntD v6 + react-router-dom v7；pnpm 10.33；Node 22(mise)；Pro Components 延后。

### 已知技术债 / 设计记录（Week 3 评估）

1. 全局 SQLite BEGIN IMMEDIATE 事务变更：所有 SQLite 写事务升级为 IMMEDIATE，单用户 dev / 低并发可接受（WAL 下读不阻塞）；多 worker / 高并发生产需重新评估锁粒度（仅串行化 refresh 而非全局）。
2. 孤儿 token 已从根上解决（successor_jti + 串行化），但 rotation 宽限窗口（10s）机制本身保留，作为设计记录。
3. 历史扩展点（v1.0 不实现）：部门/分组（通用 group + membership_groups 挂 membership 层）；PG RLS 第二防线；access token 即时吊销；ABAC/五表 RBAC。

## 6. 错误与修正（含历史累积）

| 错误/偏差 | 修正/教训 |
|---|---|
| 本次：mise.toml dev:frontend 未先装依赖致启动失败 | 手动 pnpm install 一次；不必每次 install |
| 本次：前端 token 存储首版设计成刷新即失效（破坏 7 天会话）| 改为 refresh 存 localStorage + 启动静默换发 |
| 本次：refresh 并发竞态（StrictMode 双挂载同 jti）| 三层修复；e2e B1 从 67% 失败→0 失败 |
| 本次：宽限放行产生孤儿 token | 改 successor_jti 指针 + 串行化，Branch B 纯读不插入 |
| 本次：Part B 首版绕过 STOP 点自行实现（"State assumptions and continue"）| 用户纠正；后续两次 STOP 均守住；立为强纪律 |
| 本次：并发测试用 :memory:+StaticPool 被假串行化，却归因为"测试问题"宣布可行 | 用户驳回；改用确定性 Branch B 测试（造 revoked+successor 态→旧 jti 二次 refresh→验 active 行数不变） |
| 本次：运行库漏跑 successor_jti 迁移致 login 500 | curl 定位真因 + alembic upgrade head 修复；e2e 随即 6/6（诚实排查，未甩锅）|
| 本次：根目录残留临时 npm 产物（playwright 临时装）| 扶正进 frontend devDep + e2e/，清理根目录，精确 git add 不用 -A |
| 历史：coverage 异步追踪失效虚低 75.93% | 加 source+concurrency → 93.83% |
| 历史：派工模板与实际签名不符 | 本地 AI IDE 执行前先读源码确认，主动适配 |
| 历史：department_id 错放 USER 表 | 部门归位 membership 层，v1.0 不建 |
| 历史：alembic.ini 中文注释 GBK 失败 | 注释必须 ASCII |

## 7. 讨论演变（文字描述）

Day 4 开场用户提供 Day 3 归档 + 两份架构文档同步上下文，顾问复述同步点。用户先强调两条纪律（未放行不擅自派工、提示词单独成可复制块）。确定 Day 4 三件事全做（前端页 + API 测试 + 复盘规划），用户砍掉 API 手动测试（自动化已覆盖）。讨论启动脚本时顾问起初建议根目录放 package.json，用户纠正应用 mise.toml（mise 支持 task），且 SDK 用 mise 管理。期间用户质疑"为什么 AI 记不住"，顾问解释 LLM 无跨会话记忆、靠滚动归档恢复，并借此完善归档提示词（加 git 状态/函数签名/纪律不淡出/目录树用缩进四条）。

切片推进：切片1 mise.toml（commit 前演示 mise run dev 因前端未装依赖失败，手动装修复）→ 切片2 前端登录注册 Dashboard（首版静默存储破坏 7 天会话被用户纠正）。联调后发现刷新页面偶发 401 掉登录态，顾问设 STOP 点要求先排查根因——本地 AI IDE 稳定复现 + 毫秒日志 + DB 佐证，定位 StrictMode 双挂载同 jti 并发竞态。修复设计为三层，实现后 e2e B1~B6 全过、多标签页并发覆盖。验收中顾问指出宽限放行产生"孤儿 token"，用户决定不留债，确定方案 C 根除。

孤儿根除碰会话安全语义，顾问严设 STOP：要求本地 AI IDE 先核实 SQLite/PG 行锁行为、写方案再实现。首版本地 AI IDE 绕过 STOP 自行实现被用户驳回；二版守住 STOP 出方案（isolation_level=None+BEGIN IMMEDIATE / FOR UPDATE + successor_jti + Branch A 插入/B 纯读）。顾问审出"并发测试用 :memory 假串行化却宣称可行"的漏洞，要求改确定性测试。三版本地 AI IDE 按要求做确定性 Branch B 验证（active 行数 before=after=1 证无孤儿）、如实标注全局 IMMEDIATE 变更、中途自查修复运行库漏迁移致 login 500。全程 70/70 + e2e 6/6 + 覆盖率 94%/100%，验收通过 commit 9bfc11b。

## 8. 当前状态与后续步骤

### Git 状态

- 最新 commit：9bfc11b（fix(auth): eliminate orphan refresh tokens via successor_jti pointer + serialized rotation; add expired-token cleanup endpoint）
- Day 4 提交链：22c8bcd（竞态三层修复 + 登录注册 Dashboard + mise + e2e）→ 9bfc11b（孤儿根除 + 清理端点）
- 待提交：本归档 docs/decisions/2026-0601-week2-day4-complete.md（由本地 AI IDE 存盘 + commit，建议 message：docs: add Week 2 Day 4 archive）；架构规范文档可追加变更记录（SQLite BEGIN IMMEDIATE 全局事务 / successor_jti 字段 / refresh_rotation_grace_seconds 配置）
- 仓库状态干净，无临时产物

### Completed

- Week 1 全闭环（dadf307，tag week1-complete @ 07ee750）
- Week 2 Day 1 架构评审；Day 2 ORM/security/seed（21/21）；Day 3 core+zones+17 端点（61/61，93.83%/100%）
- Week 2 Day 4：mise 启动脚本 + 登录注册 Dashboard 页 + refresh 竞态三层修复 + 租户名显示 + playwright e2e + 孤儿 token 根除 + 过期清理端点；70/70 后端 + e2e 6/6，覆盖率 94%/100%

### Next Steps（Week 2 Day 5 / Week 3，新会话）

- 新会话同时提供本归档 + 平台架构规范 + 认证设计文档三份；AI 开场先复述同步点 + 确认角色边界 + 等用户明确放行才写派工。
- 候选任务（待用户拍板）：Week 2 复盘收尾；基于 demo zone 扩展第一个真实业务模块（billing 或其他，由用户定）；评估全局 IMMEDIATE 事务在生产多 worker 下的锁粒度；可选后台清理调度器。

### 工程纪律（含历史累积，覆盖至 Day 4，不得淡出）

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
20. 【Day 4 新立】安全敏感改动（碰会话/rotation/锁/token 语义）必须先出方案给用户确认（STOP 点）再实现，禁止"State assumptions and continue"擅自动手。
21. 【Day 4 新立】验收不得只看代码、不得用"假环境/会被自动串行化的测试"充当证据，必须实跑；失败的验证不得随意归因为"测试级问题"放过，必须查到真因（用确定性用例兜底）。
22. 【Day 4 新立】token 原文绝不落库，只存 jti / successor_jti 指针；前端 access 存内存、refresh 存 localStorage 且必须尊重后端 refresh 有效期语义。
23. 【Day 4 新立】影响全局行为的改动（如 SQLite BEGIN IMMEDIATE 升级所有写事务）必须在代码处注释说明并在交付汇报中明确告知，记入技术债待生产环境重评估。
