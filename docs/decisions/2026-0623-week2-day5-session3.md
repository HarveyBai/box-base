# BoxBase v1.0 工作记忆摘要 — Week 2 Day 5 Session 3 收官（滚动累积版）

## 1. 对话主题与用户意图

- 项目：BoxBase v1.0 —— 轻量级、模块化 Python 多租户 SaaS 框架，16 周完成 v1.0，当前 Week 2 Day 5 Session 3（2026-06-23）。
- 用户角色：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收拍板；本地 AI IDE（Cursor / Claude Code / Copilot）执行代码；会话内 AI 任顾问，只出决策建议 / 派工提示词 / 验收清单 / 归档草稿。
- 顾问交互硬规矩：①未经用户明确放行不得擅自写派工提示词；②给本地 AI IDE 的提示词指令必须放进一整段可复制的 markdown 代码块，且代码块前后**不**夹杂任何顾问对用户说的话（否则用户复制时被割裂），与给用户看的内容严格分开；③碰安全语义的改动必须先出方案给用户确认（STOP 点）再让本地 AI IDE 动手。
- Week 2 Day 5 Session 3 核心任务（按 a→b→c 顺序，全部完成）：
  - **a. 前端 e2e 在 HEAD 52ad9c6 回归验证**：补 Session 2 没跑的窟窿。本地 AI IDE Stage A 一次过；e2e 6/6 绿（B1~B6，54.1s），后端 /api/docs 200、前端 5173 200，工作区干净，无 commit，Stage B 跳过。
  - **b. revoked_reason model docstring 修正**（清技术债 #2）：单文件单 commit。Stage A 出 diff 后审出"通常"措辞需修；二次修订后又审出疑似 CJK 间空格（实为 type 命令终端列宽折行的显示伪影）；三次核实用子串布尔判定 + CJK+空格+CJK 模式扫描决定性闭环，文件干净。Stage B commit 801f9c4 + push origin/main 成功。commit message 落地有两处 here-string 损耗（路径前缀丢失 + 一处换行被吞），实质语义完整保留，记账不修补。
  - **c. Week 3 kickoff 方案讨论**：用户拍候选 1（基于 zones/demo/ 起首个真实业务模块）+ 业务方向 c（Billing / Subscription）。Day 5 Session 3 落本归档收尾，再开新会话进 Week 3。
- 历史阶段：Week 1 全闭环（基线 dadf307，tag week1-complete @ 07ee750）→ Week 2 Day 1 架构评审拍板 → Day 2 ORM/security/seed（21/21 绿）→ Day 3 core+zones 重构 + 17 端点 + demo zone（61/61 绿，覆盖率 93.83%/100%）→ Day 4 前端 + 竞态修复 + 孤儿根除（70/70 + e2e 6/6，94%/100%，commit 9bfc11b）→ Day 4 后追加 e4ab8d9 Day 4 归档入库 + 4512459 一次格式化 → Day 5 Session 1 文档归真（housekeeping 6db91dc + AGENTS.md 归真 a2eac4a + Day 5 Session 1 归档 1c69d57）→ Day 5 Session 2（架构规范 v1.1 3fc9642 + retrospective 52ad9c6）→ Day 5 Session 3（本归档，e2e 回归验证无 commit + revoked_reason docstring 修正 801f9c4）。

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| —— Week 2 Day 5 Session 3（本次）—— | |
| 今天三件事顺序？ | 用户拍 a（e2e 回归）→ b（docstring 修正）→ c（Week 3 kickoff）。 |
| e2e 命令字面量？ | `pnpm exec playwright test`，**禁带** `--project=chromium`（playwright.config.ts 无具名 project，带了报错）。可以用 `pnpm test:e2e`（Day 4 加的 script）但需汇报 script 内容。 |
| e2e 跑前需要起服务吗？ | 是。`mise run dev` 一把起后端+前端，或分两个终端 `mise run dev:backend` / `mise run dev:frontend`。 |
| revoked_reason model docstring 改成几值？ | 两值（rotation / logout），与 services/auth.py 实写字面量一致。switch_tenant 复用 "rotation" 字面量、靠 successor_jti=NULL 区分语义。**不动 auth.py**（Branch B 防御代码 `if not successor_jti: 401` 依赖此不变量）。 |
| Stage A diff 中 "通常不写 successor_jti" 措辞为什么要改？ | switch_tenant 在当前实现下**确定性**不写 successor_jti（auth.py line 350 `revoked_reason = "rotation"` 后无任何 successor_jti 赋值），不是"通常 vs 例外"。"通常"二字弱化 Branch B 防御的不变量基础，未来读者可能误以为存在例外路径而新增 "switch_tenant 也写一下 successor_jti" 的代码，那一刻 Branch B 破防。改为"但不写 `successor_jti`（保持为 NULL），靠 `successor_jti IS NULL` 与正常 rotation 区分语义。" |
| Stage A 二次核实疑似 CJK 间空格怎么处理？ | 三次核实用子串布尔判定（`'正 常' in c` 等 5 项 expect_in=False / `'正常' in c` 等 5 项 expect_in=True，10/10 一致）+ CJK+空格+CJK 模式正则扫描全文（结果 NO_CJK_SPACE_CJK_PATTERN）决定性证明文件干净。type 命令在 Windows 终端列宽边界把 repr 长字符串折行、折行处空格视觉对齐，造成显示伪影。教训：repr 输出本应单行不应有 CJK 间空格，看到了就是显示问题不是真空格；下次直接用子串布尔判定避免歧义。 |
| commit message 多行如何传？ | PowerShell here-string `@'...'@` 通过 stdin 传给 `git commit -F -`。本次落地有两处损耗：①"docs/decisions/" 路径前缀被吃 ②一处换行被吞成 4 个空格。实质语义保留，不 amend / force push 修补（违反"严禁 --force"纪律 + 远端已推进）。立纪律 32（commit 后立刻 git log -1 verbatim 核对）+ 纪律 33（任何字面量偏离派工要求必须主动声明）。 |
| Week 3 走哪条候选？ | 用户拍候选 1（基于 zones/demo/ 起首个真实业务模块）+ 业务方向 c（Billing / Subscription：订阅计划 + 用量记录，能演示跨 zone 写 admin 用户表 + billing 业务表）。候选 2（refresh rotation 锁粒度精化 SQLite 路径限定）+ 候选 3（后台清理调度器替代手动 cleanup 端点）作为 Week 3 期间待命项。 |
| —— Week 2 Day 5 Session 2（历史，保留结论）—— | |
| 架构规范补几处？怎么补？ | 5 处补登：①4.4 配置项表追加 refresh_rotation_grace_seconds=10 行 ②新增子小节 5.1.1 事务串行化嵌在 5.1 与 5.2 之间，5.2 编号不顺延 ③5.2 RefreshToken 关键约束行整行替换 ④6.1 摘要 refresh/logout/switch-tenant 三条整体替换 ⑤末尾变更记录表追加 v1.1 行。bump 至 v1.1。 |
| revoked_reason 取值是几个？ | 实写两个：rotation / logout。switch_tenant 复用 rotation 字面量、靠 successor_jti=NULL 区分。 |
| retrospective 单独成文还是并入归档？ | 单独成文 docs/retrospectives/2026-W2-retrospective.md（85 行）；不进新会话恢复集（顾问会主动读 main 上的它）。 |
| —— Week 2 Day 5 Session 1（历史，保留结论）—— | |
| 同步上下文需要哪些文件？ | 最小恢复集 = 3 份：最新滚动归档 + 平台架构规范 + 认证设计文档；AGENTS.md 不在恢复集（它是给本地 AI IDE 的执行规则）。 |
| 文档归真优先级？ | A 文档归真 > B housekeeping > C 可选 e2e 验证；实际 B → A。 |
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
| 平台架构规范 v1.1 | docs/architecture/2026-W2-platform-architecture-design.md | core/+zones/ 模块化规范单一真相源；模块契约（Zone Contract）在章节 3；含 5.1.1 事务串行化、5.2 RefreshToken 完整字段 + Branch A/B、6.1 refresh/logout/switch-tenant 摘要、变更记录表（v1.0 + v1.1）。 |
| 认证设计评审 | docs/architecture/2026-W2-auth-tenant-rbac-design.md | 认证/多租户/RBAC 详细设计；ER/字段/API/时序图；§2.1 DIY 薄层 vs fastapi-users/authx 决策证据；§8.2 历史扩展点。 |
| Week 2 retrospective | docs/retrospectives/2026-W2-retrospective.md | 一次性周复盘文档（85 行）；量化指标 + 关键决策 + 教训与 Week 3 行动项 + 一句话收尾；不进新会话恢复集。 |
| Day 5 Session 2 归档 | docs/decisions/2026-0623-week2-day5-session2.md | 上一份滚动归档（已被本归档替代为唯一会话状态源）。注：用户工作区还有同名未追踪文件 `?? 2026-0623-week2-day5-session2.md` 在仓库根目录，疑似 Day 5 Session 2 落盘到错误位置或拷贝副本，**待 Day 5 Session 3 收尾时核实并清理**。 |
| Day 4 归档 | docs/decisions/2026-0601-week2-day4-complete.md | Day 4 滚动累积版（更早，已淡出）。 |
| 本归档 | docs/decisions/2026-0623-week2-day5-session3.md | Week 2 Day 5 Session 3 滚动累积版（本文件，待落盘 + 提交）。 |
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
        models/          ← 8 张基础表；refresh_token.py 含 jti/status/expires_at/revoked_at/revoked_reason/successor_jti（docstring 已 Day 5 Session 3 对齐实现：两值 rotation/logout）
        routers/         ← auth.py / users.py / roles.py / admin.py(含 maintenance/cleanup-refresh-tokens 端点)
        services/        ← auth.py(refresh_token Branch A/B + switch_tenant 复用 rotation 不设 successor_jti + logout reason=logout) / users.py / roles.py
        router.py / schemas.py / service.py
      zones/demo/        ← 示例扩展模块（Week 3 候选 1 起业务模块的参考模板）
      tools/seed.py
      main.py
    backend/alembic/versions/  ← e0757aa877d0(revoked_at/reason) + a1b2c3d4e5f6(successor_jti)
    frontend/
      src/api/client.ts            ← authFetch + refreshAccessToken(单飞锁)
      src/contexts/AuthContext.tsx ← AuthProvider+useAuth；init useEffect useRef 去重
      src/components/RootLayout.tsx
      src/pages/  LoginPage / RegisterPage / DashboardPage(租户名显示) / HomePage
      src/router.tsx
      e2e/auth.spec.ts             ← playwright B1~B6 回归用例（Day 5 Session 3 在 HEAD 52ad9c6 上跑过 6/6 绿，54.1s）
      playwright.config.ts（无具名 project，调用时不要带 --project=chromium，直接 `pnpm exec playwright test`）
      package.json(devDep @playwright/test 1.60.0 + test:e2e script)
    mise.toml（根目录唯一启动配置：dev / dev:frontend / dev:backend）

### 关键签名 / 约束（查文档才知道的细节，长期有效）

| 项 | 细节 |
|---|---|
| core/security.py | create_access_token(user_id:UUID, active_tenant_id:UUID, username:str)；create_refresh_token(jti:str, user_id:UUID)；decode_access_token / decode_refresh_token（无通用 decode_token）；get_current_user(token,db) 超管 short-circuit + active membership 校验 |
| RequestContext | 字段 user_id / active_tenant_id / is_superadmin（无 jti，需 jti 场景传 None） |
| RefreshToken 模型 | jti: Mapped[str] = mapped_column(String(64), nullable=False) + ix_refresh_token_jti UNIQUE 索引；status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)；revoked_at: Mapped[datetime\|None] = mapped_column(DateTime(timezone=True), nullable=True)；revoked_reason: Mapped[str\|None] = mapped_column(String(16), nullable=True)（**String(16) 列**，实写两值 "rotation"/"logout"，docstring 已 Day 5 Session 3 commit 801f9c4 对齐到两值）；successor_jti: Mapped[str\|None] = mapped_column(String(64), nullable=True)（仅存 jti 不存 token 原文）。索引：ix_refresh_token_jti(unique) / ix_refresh_token_tenant_user(tenant_id,user_id) / ix_refresh_token_expires_at |
| services/auth.py refresh_token | SELECT...with_for_update() 锁定行；Branch A(status=active)→revoked + revoked_reason="rotation" + 写 successor_jti + INSERT 新 active 行；Branch B(revoked + reason=="rotation" + (now-revoked_at)<=grace + successor_jti not None)→读 successor_jti 重签 access、不 INSERT；reason!="rotation" 或超窗口或 successor_jti=None→401 |
| services/auth.py switch_tenant（line 350） | revoke 旧 refresh 时 reason="rotation" 但**不设** successor_jti（确定性行为）；故 Branch B 防御 `if not successor_jti: 401` 命中，旧 jti 宽限内仍 401（语义正确，避免切换租户后旧会话被静默续命）|
| services/auth.py logout（line 309） | revoke 当前 jti 时 reason="logout"，不写 successor_jti；永不放行 |
| services/auth.py cleanup_expired_refresh_tokens | DELETE WHERE expires_at<now()，返回删除条数；仅删过期、不动在用 |
| 清理端点 | POST /api/admin/maintenance/cleanup-refresh-tokens；superadmin only；返回 CleanupResponse{deleted:int}；普通用户 403 |
| 前端 token 存储 | access→内存 React Context（刷新即失效）；refresh→localStorage（尊重 7 天）；启动 init 静默换发；401 拦截器自动 refresh + rotation 覆盖 |
| SQLite 串行化钩子（database.py） | _set_sqlite_pragma(connect 事件)：PRAGMA journal_mode=WAL + foreign_keys=ON + dbapi_connection.isolation_level=None；_sqlite_begin_immediate(begin 事件)：conn.exec_driver_sql("BEGIN IMMEDIATE")；仅 settings.database_url.startswith("sqlite") 时注册；全局生效于所有 SQLite 写事务；PG 不注册（用 with_for_update() 行锁） |
| config 配置项 | database_url / secret_key / superadmin_username(默认"") / access_token_expire_minutes=30 / refresh_token_expire_days=7 / refresh_rotation_grace_seconds=10 |
| 17+1 admin 端点 | auth(register/login/refresh/logout/switch-tenant/tenants) + users/me + users(GET/POST) + memberships(PATCH/DELETE) + roles(GET/POST/{id}/permissions) + permissions + admin(tenants/users) + admin/maintenance/cleanup-refresh-tokens |

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| pnpm exec playwright test（本次） | 前端 e2e 在 HEAD 52ad9c6 回归 | 6 passed (54.1s)；B1~B6 全绿；后端 /api/docs 200、前端 5173 200；工作区 e2e 跑前跑后一致（M PROMPTS.md / ?? 2026-0623-week2-day5-session2.md），无 playwright 自动产物，无 commit |
| Python 子串布尔判定（本次 Stage A 三次核实） | 决定性证明 docstring 文件干净 | 10 项 expect_in 与 actual_in 全一致：'正常'/'引入'/'原文'/'字段'/'安全' True，'正 常'/'引 入'/'原 文'/'字 段'/'安 全' False |
| Python re CJK+空格+CJK 全文扫描（本次 Stage A 三次核实） | 兜底排除任何 CJK 间空格 | NO_CJK_SPACE_CJK_PATTERN |
| git commit -F -（本次 Stage B） | 多行 commit message 通过 stdin 传入 | commit 801f9c4，1 file changed, 7 insertions(+), 3 deletions(-)；message 落地有两处 here-string 损耗（路径前缀 / 一处换行）但实质语义保留 |
| git push origin main（本次 Stage B） | 推 docstring 修正 | 52ad9c6..801f9c4 main -> main 成功 |
| git（历史 Day 5 Session 2） | 5 笔 commit + push | 6db91dc → a2eac4a → 1c69d57 → 3fc9642 → 52ad9c6 |
| 源码 verbatim 读取（历史） | 核源码 | refresh_token.py / database.py / auth.py / config.py 关键片段确认 revoked_reason 是 String(16) 非枚举、auth.py switch_tenant 写 "rotation"、SQLite 钩子仅在 sqlite 注册 |
| pytest（历史 Day 5 Session 1 复跑） | 后端回归 | 70 passed / 32.86s；覆盖率 94% / boxbase.core.security 100% |
| Playwright（历史 Day 4） | e2e | B1~B6 全过；多标签页并发用 context.newPage() 共享 localStorage |
| GitHub Actions 截图（历史 Day 5 Session 1） | CI Run 编号取数 | 用户提供截图核实 Run #20，commit 4512459，39s 全绿 |
| git grep（历史 Day 5 Session 1） | 幻影词自检 | AGENTS.md 中 fastapi-users（首选）/Casbin/PermissionChecker/org_id 全部清空 |
| alembic（历史 Day 4） | 迁移 | e0757aa877d0 + a1b2c3d4e5f6；upgrade/downgrade 往返验证 |

## 5. 决策与结论（含历史累积）

### Week 2 Day 5 Session 3 决策（本次，长期有效）

1. **a 任务执行模式**：e2e 回归是只读验证、无代码改动，Stage A 一次过即闭环；Stage B 仅在出现未追踪产物需清理时启动，纯绿场景跳过。本次跑后工作区干净（playwright 配置或 .gitignore 已正确忽略 test-results/ / playwright-report/），Stage B 不需要。
2. **b 任务方案**：改 docstring 对齐实现（rotation/logout 两值），**不动 auth.py**。理由——Branch B 防御 `if not successor_jti: 401` 依赖 "switch_tenant 必然不写 successor_jti" 这个不变量；如果改成给 switch_tenant 写专属字面量 "switch_tenant"，Branch B 要从单分支判定扩展到多分支判定，安全面变大、回归风险高。轻量单 commit、单文件改动，性价比最高。
3. **b 任务措辞硬规矩**："switch_tenant 不写 successor_jti" 必须用确定性措辞（"不写"/"保持为 NULL"），不能用"通常不写"等弱化表达——弱化措辞会暗示存在例外路径，未来读者可能误以为可以特殊情况下也写一下，那一刻 Branch B 破防。
4. **b 任务字符级核查口径**：repr 长字符串在 Windows `type` 命令终端列宽边界折行会产生 CJK 间空格的显示伪影；判定字符级真伪必须用语义判定（子串布尔命中 + 正则模式扫描），不看 repr 视觉残留。
5. **commit message 不修补**：PowerShell here-string 落地两处损耗（路径前缀 docs/decisions/ 丢失 / 一处换行被吞），实质语义完整保留；amend + force push 修补成本 > 收益，且违反 "严禁 --force" 纪律 + 远端已推进，记账不修补。
6. **Week 3 走候选 1 + 业务方向 c**：Week 3 第一周做"基于 zones/demo/ 起首个真实业务模块"，业务方向 c（Billing / Subscription：订阅计划 + 用量记录）。理由——Week 2 交付的是框架，框架的价值在 Week 3 真实模块上跑出来才能验证；Billing 能演示跨 zone 写（admin 用户表 + billing 业务表）、能演示 row-level 隔离 + 软删 + 三层访问控制。候选 2（refresh rotation 锁粒度精化）+ 候选 3（后台清理调度器）作为待命项。
7. **Day 5 Session 3 滚动归档落收尾再开新会话进 Week 3**：遵循纪律 9（滚动替换式），本归档发布后即替代 Day 5 Session 2 归档作为唯一会话状态源；Week 3 kickoff 在新会话开场。

### Week 2 Day 5 Session 2 决策（保留）

1. 架构规范 v1.1 五处补登采用"追加补全、不动既有正文"策略：仅 5.2 RefreshToken 那一行整行替换、6.1 摘要三条整体替换；其它三处全是追加。
2. revoked_reason 文字采用"实写字面量"口径：架构规范 v1.1 写 "rotation" / "logout" 二值，与 auth.py 实际写入字面量一致。
3. SQLite BEGIN IMMEDIATE 写法采用"全局升级 + 技术债标注"口径：v1.1 5.1.1 小节明确"全局生效于所有 SQLite 写事务" + 技术债 callout（Week 3+ 重评估目标仅串行化 refresh rotation 路径）。
4. retrospective 单独成文：放 docs/retrospectives/2026-W2-retrospective.md（85 行），不进新会话恢复集。
5. retrospective Action Items 只列 Week 3 候选不规划 scope。
6. STOP 点纪律加强：Stage A/B 切死单独 enforce；阶段 B 必须等顾问明确放行才能执行；diff 必须完整 verbatim 贴回。

### Week 2 Day 5 Session 1 决策（保留）

1. 文档归真优先级：A > B > C，实际 B → A 避免污染。
2. AGENTS.md 归真定位为外科手术式修订：仅 5 处。
3. 幻影词清单（不得复活）：fastapi-users（作首选库）、Casbin、PermissionChecker、org_id、auth/tenant/rbac/modules/ 目录命名。
4. 多租户口径：tenant_id + with_loader_criteria 强制过滤（含 deleted_at IS NULL）。
5. RBAC 口径：简化三表 + resource:action + tenant-scoped + require_permission；Casbin v1.0 不引入。
6. Module Contract 真相源：docs/architecture/2026-W2-platform-architecture-design.md 章节 3。
7. CI Run 编号绝不编造：无源时用 #TBD 占位 + 后续补登。
8. 上下文恢复最小集 = 3 份：最新滚动归档 + 平台架构规范 + 认证设计文档。

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

1. **SQLite BEGIN IMMEDIATE 全局事务**：当前升级所有 SQLite 写事务；多 worker / 高并发生产部署需重评估锁粒度，目标仅串行化 refresh rotation 路径。Week 3 候选 2。
2. ~~revoked_reason model docstring vs 实现脱节~~ **已 Day 5 Session 3 commit 801f9c4 解决**。
3. **rotation 宽限窗口（10s）机制保留**：v1.0 接受为防误杀的设计选择；高并发场景需观察实际触发频率与孤儿率。
4. ~~前端 e2e 在 52ad9c6 上未回归~~ **已 Day 5 Session 3 跑过 6/6 绿（54.1s）​**。HEAD 现已推进到 801f9c4，但仅 docstring 改动不影响前端，e2e 结论延续有效。
5. **AGENTS.md CI Run 编号**：当前据实写 #20；后续 CI run 推进后需同步更新 Current Phase 行。
6. **commit message 落地损耗**（Day 5 Session 3 新发现）：PowerShell here-string 通过 stdin 传 git commit -F - 时偶发路径前缀 / 换行损耗；本次 commit 801f9c4 message body 有两处偏差但实质语义保留，不修补。立纪律 32 + 33（见第 8 节）。
7. **工作区根目录未追踪文件 `?? 2026-0623-week2-day5-session2.md`​**：疑似 Day 5 Session 2 归档落盘到错误位置或拷贝副本。Week 3 收尾时核实并清理（移到 docs/decisions/ 或删除）。
8. **历史扩展点（v1.0 不实现）​**：部门/分组（通用 group + membership_groups 挂 membership 层）、PG RLS 第二防线、access token 即时吊销、ABAC/五表 RBAC（详见 auth-tenant-rbac-design.md §8.2）。
9. **后台清理调度器**：替代手动 `/api/admin/maintenance/cleanup-refresh-tokens` 端点；Week 3 候选 3。

## 6. 错误与修正（含历史累积）

| 错误/偏差 | 修正/教训 |
|---|---|
| 本次（Day 5 Session 3）：派工块前后夹杂顾问对用户说的话，导致用户复制时被割裂 | 用户当场抓出（"我怎么复制给本地AI IDE？"）。立纪律 31（派工块必须是回复的最后一个内容块，前后绝不夹杂顾问对用户说的话）。重发派工块格式合规。教训：纪律 10 写过"派工与给用户看的内容严格分开"，但没切死"派工块必须是回复最后一个块"，本次落地失守，必须显式声明位置纪律。 |
| 本次：Stage A 二次核实（"通常"修订后）的 git diff 中疑似 CJK 间空格，本地 AI IDE 在三次核实结论里把锅含糊推给"原始编辑时的误插入或可见折行" | Step 1/3 的子串判定 + 模式扫描已决定性证明文件干净，正确结论是"显示伪影、文件干净"。本地 AI IDE 把不确定结论留给顾问判定属不严谨。立纪律 34（字符级核查必须给出确定性结论：用子串布尔判定 + 正则模式扫描决定，不在汇报中保留歧义）。 |
| 本次：commit message 落地有两处 here-string 损耗（"docs/decisions/" 路径前缀丢失 + 一处换行被吞），本地 AI IDE 未在汇报中主动声明 | 顾问审 git log -1 时抓出。立纪律 32（commit 后立刻 git log -1 verbatim 核对派工 message 字面量，发现损耗当场报告）+ 纪律 33（任何字面量偏离派工要求的处理必须主动声明，不得静默放过）。本次实质语义保留 + 远端已推进，不 amend + force push 修补。 |
| 历史 Day 5 Session 2：架构规范 Stage A 用概述替代源码原文 | 派工要求"原样贴回"配硬约束（不要总结、不要概述、不要 paraphrase），且回贴自检明确列条目。 |
| 历史 Day 5 Session 2：架构规范 Stage B 跳过顾问审 diff 直接 commit + push | 立纪律 29（Stage A/B 切死，阶段 B 必须等顾问明确口头放行才能 commit/push，diff 完整 verbatim 贴回不接受"已检查"）。 |
| 历史 Day 5 Session 2：retrospective 跨 STOP 点擅自落盘 | 立纪律 31（顾问发草案 ≠ 派落盘工，本地 AI IDE 在用户明确说"派工落盘"或顾问发出可复制派工块前禁止落盘）。 |
| 历史 Day 5 Session 2：retrospective 落盘擅自把"DIY 项。"改为"DIY 项."（西文句点） | 教训：本地 AI IDE 任何"自作主张修正"必须主动声明，不得静默修改。 |
| 历史 Day 5 Session 1：首版归档第一稿丢失工程纪律 1-23 条 | 顾问接手重写全文；立纪律 28（历史累积顾问主笔，本地 AI IDE 不得概述压缩）。 |
| 历史 Day 5 Session 1：首版 AGENTS.md Module Contract 引用错指 | amend 修正；落地后 git grep 双向自检（auth-tenant-rbac-design.md / platform-architecture-design.md 各自该出现的位置）。 |
| 历史 Day 4：refresh 并发竞态（StrictMode 双挂载）| 三层修复 + e2e B1 从 67% 失败→0 失败。 |
| 历史 Day 4：宽限放行产生孤儿 token | successor_jti 指针 + 串行化，Branch B 纯读不插入。 |
| 历史 Day 4：Part B 首版绕过 STOP 点 | 立纪律 20（安全敏感改动 STOP 点必须守住）。 |
| 历史 Day 4：并发测试用 :memory:+StaticPool 假串行化 | 立纪律 21（验收禁假环境，必须确定性用例）。 |
| 历史 Day 4：运行库漏跑 successor_jti 迁移致 login 500 | curl 定位 + alembic upgrade head 修复。 |
| 历史：coverage 异步追踪虚低 75.93% | 加 source+concurrency → 93.83%。 |
| 历史：派工模板与签名不符 | 本地 AI IDE 执行前先读源码确认。 |
| 历史：alembic.ini 中文注释 GBK 失败 | 注释必须 ASCII。 |

## 7. 讨论演变（文字描述）

会话开场用户发四份文档（AGENTS.md / 平台架构规范 v1.1 / 认证设计 / Day 5 Session 2 归档）让顾问同步。顾问按归档恢复上下文并复述同步点 + 边界纪律 + 列 Day 5 Session 2 第 8 节"Next Steps"四条候选（a 前端 e2e 回归 / b revoked_reason docstring 修正 / c Week 3 kickoff / d 其它）。用户拍 "按顺序来"，顾问起手 a。

a 任务派工首版顾问把派工块前后夹杂"下面这块整段复制给本地 AI IDE"和"执行完把回贴整段发回来"两段对用户说的话，导致用户复制时被割裂。用户当场抓出违纪（纪律 10），顾问承认违纪并立纪律 31（派工块必须是回复的最后一个内容块）+ 重发合规版派工块。本地 AI IDE Stage A 一次过：HEAD = 52ad9c6（与归档一致），mise run dev 起服务、curl 确认后端 /api/docs 200 + 前端 5173 200，pnpm exec playwright test 跑出 6 passed (54.1s)，工作区干净无 playwright 自动产物。顾问审过，Stage B 跳过，a 闭环。

进 b 任务，顾问出方案：改 docstring 对齐实现两值（rotation/logout）+ 不动 auth.py（Branch B 防御依赖不变量）+ 单文件单 commit。用户 OK。Stage A 派工要求 verbatim 核源码 + Q1/Q2 答案 + 出 diff 不落盘。本地 AI IDE 一次回贴完整：refresh_token.py 全文 + auth.py grep 5 处命中 + 每处 ±3 行 context + Q1 答 "rotation/logout 两值" + Q2 grep 全仓只在 services/auth.py 写入。顾问审 diff 时发现新增行写"通常不写 successor_jti"，必须改——switch_tenant 在当前实现下确定性不写、不是"通常 vs 例外"，弱化措辞侵蚀 Branch B 防御。

Stage A 修订派工去掉"通常"。本地 AI IDE 改完后回贴 git diff，顾问审时在新增的两行（行 22 / 行 25）疑似看到 CJK 间空格 "正 常" / "安 全"，怀疑是 git pager 终端宽度折行的显示伪影但不能确定。Stage A 二次核实派工：grep 两个具体串 + 读文件原文 + Python repr 输出。本地 AI IDE 回贴：两条 grep 无命中，但 Python repr 在 Windows `type` 命令下又出现 CJK 间空格，本地 AI IDE 在结论里把锅含糊推给"原始编辑时的误插入或可见折行"，留歧义给顾问。

顾问识破 type 命令的列宽折行问题，Stage A 三次核实派工换更可靠手段：①子串布尔命中（10 项 expect_in vs actual_in）②repr 落临时文件再 cat 绕过终端折行 ③CJK+空格+CJK 全文正则扫描兜底。本地 AI IDE 回贴决定性证据：10/10 子串判定一致（带空格全 False、不带空格全 True）+ NO_CJK_SPACE_CJK_PATTERN，文件干净，type 命令的视觉残留确认是显示伪影。顾问立纪律 34（字符级核查必须用子串布尔判定 + 正则扫描决定性结论）。

Stage B 派工 commit + push 直推 origin/main（按 Day 5 Session 1/2 惯例）。commit message 严格字面量含 docs/decisions/ 路径前缀、跨 9-10 行的 "leaving / successor_jti as NULL." 等。本地 AI IDE 用 PowerShell here-string `@'...'@` 通过 stdin 传 git commit -F -，commit 801f9c4 落地，push 成功 52ad9c6..801f9c4。顾问审 git log -1 时抓出两处落地损耗：①"docs/decisions/" 路径前缀丢失 ②第 9-10 行 "leaving" 后换行被吞成 4 个空格。本地 AI IDE 汇报时未主动声明这两处偏差，违纪。顾问决策不修补（实质语义保留 + 修补违反 "严禁 --force" + 远端已推进），但立纪律 32（commit 后 git log -1 立刻 verbatim 核对）+ 纪律 33（字面量偏离必须主动声明）。b 闭环。

进 c 任务，顾问出 Week 3 候选三条 + 推荐候选 1（基于 zones/demo/ 起首个真实业务模块）+ 列业务方向四个（a 笔记 / b 任务 / c 订阅 / d 文件元数据）。用户拍候选 1 + 业务方向 c（Billing / Subscription）+ 落归档收尾再开新会话进 Week 3。顾问主笔本归档（守纪律 28 历史累积顾问主笔），本归档把 Day 5 Session 3 三次违纪（派工格式失守 / 字符级核查歧义结论 / commit message 落地损耗未声明）写入第 6 节，立纪律 31 / 32 / 33 / 34。

## 8. 当前状态与后续步骤

### Git 状态

- 最新 commit：**801f9c4**（origin/main 同步，HEAD 与 origin/main 一致）。Day 5 Session 3 commit message：`docs(models): align revoked_reason docstring with implementation (rotation/logout two values)`，1 file changed, 7 insertions(+), 3 deletions(-)。
- 标签：仅 week1-complete @ 07ee750。
- Day 5 Session 3 提交链：52ad9c6 → 801f9c4（仅 1 个 commit，b 任务；a 任务无代码改动无 commit）。
- Day 5 Session 2 提交链：1c69d57 → 3fc9642 → 52ad9c6。
- Day 5 Session 1 提交链：4512459 → 6db91dc → a2eac4a → 1c69d57。
- 待提交：本归档 docs/decisions/2026-0623-week2-day5-session3.md（用户手动覆盖落盘后，由本地 AI IDE 单独派工提交，建议 message：`docs: add Week 2 Day 5 session 3 archive`）。
- 仓库状态：工作区有 `M PROMPTS.md`（用户日常笔记）+ `?? 2026-0623-week2-day5-session2.md`（疑似 Session 2 归档落盘到错误位置或拷贝副本，**Week 3 收尾时核实清理**），无其它临时产物。

### Completed

- Week 1 全闭环（dadf307，tag week1-complete @ 07ee750）。
- Week 2 Day 1 架构评审；Day 2 ORM/security/seed（21/21）；Day 3 core+zones+17 端点（61/61，93.83%/100%）；Day 4 前端 + 竞态修复 + 孤儿根除（70/70 + e2e 6/6，94%/100%，commit 9bfc11b）。
- Day 4 后追加：e4ab8d9 Day 4 归档入库 + 4512459 一次格式化。
- Week 2 Day 5 Session 1：现状盘点 + housekeeping (6db91dc) + AGENTS.md 归真 (a2eac4a) + Day 5 Session 1 归档 (1c69d57)；后端 70/70 复跑（94%/100%）。
- Week 2 Day 5 Session 2：架构规范 v1.1 (3fc9642
