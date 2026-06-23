# BoxBase v1.0 Week 2 复盘 — 认证 / 多租户 / RBAC + 前端联调

- **范围**：Week 2 Day 1（2026-05-30 架构评审）→ Day 5 Session 1（2026-06-23 文档归真）。共 5 个工作日 + 3 周缓冲期内追加文档归真。
- **基线**：Week 1 收官 dadf307 / Week 2 收官 3fc9642。
- **产品经理**：baihw（GitHub: HarveyBai）。
- **关联文档**：docs/architecture/2026-W2-auth-tenant-rbac-design.md、docs/architecture/2026-W2-platform-architecture-design.md（v1.1）、docs/decisions/2026-0601-week2-day4-complete.md、docs/decisions/2026-0623-week2-day5-session1.md。

---

## 1. 量化指标

| 维度 | Week 1 收官 | Week 2 收官 | 增量 |
|---|---|---|---|
| commit 数（main 分支） | 至 07ee750 | 至 3fc9642 | +30 笔（含 23 笔功能切片 + 4 笔归档/规范 + 3 笔 housekeeping/格式化） |
| 后端测试 | 3 passed | 70 passed | +67 用例（覆盖 auth / users / roles / admin / demo / security 单元） |
| 前端 e2e（playwright） | 0 | 6 passed | B1~B6（注册 / 登录 / 刷新 / refresh 竞态 / 登出 / 多标签页并发） |
| 全局覆盖率 | n/a | 94% | 门禁 80%，超 14pp |
| `boxbase.core.security` 覆盖率 | n/a | 100% | 门禁 95%，超 5pp |
| API 端点（admin zone） | 0 | 17 + 1（含 Day 4 maintenance/cleanup） | 全部挂 `/api` 前缀 |
| 数据库表 | 0 | 8（User / Tenant / Membership / Role / Permission / MembershipRole / RolePermission / RefreshToken） | + 关联表 |
| Alembic 迁移 | baseline | + 6 笔 + 2 笔 Day 4 字段补登（revoked_at/reason、successor_jti） | upgrade/downgrade 往返均验证 |
| CI 状态 | Run #14 全绿 | Run #20 全绿（lint-and-test 36s / Frontend Lint & Typecheck 22s / Secret Scan 9s，总 39s） | 3 job 并行，无 deprecation 累积 |
| 文档（架构 + 归档 + retrospective） | 1 份 | 5 份（auth-tenant-rbac-design / platform-architecture-design v1.1 / Day 4 归档 / Day 5 Session 1 归档 / 本 retrospective） | — |

---

## 2. 关键决策回顾

### 2.1 架构与选型（Day 1，长期影响）

- **认证库 → DIY 薄层（PyJWT + pwdlib[argon2]）​**：联网核实 fastapi-users 15.0.5 已进入维护模式、authx 仍 Beta，且两者抽象都需迁就；DIY 薄层在性能 / 依赖最小 / 可替换三项最优，安全不打折（哈希与 JWT 库与主流方案同款）。这是 Week 2 最关键的"刻意例外"决策——开源优先原则下唯一明确写入纪律的 DIY 项。
- **多租户 → Row-level + tenant_id（共享库共享表）​**：SQLite/PG 一致性纪律 + 跨租户高频查询 + 独立部署逃生通道；ORM 用 `with_loader_criteria` 强制注入 `tenant_id` + `deleted_at IS NULL` 双条件过滤，PG RLS 第二防线 v1.0 不启用、预留 hook。
- **RBAC → 简化三表 + `resource:action`​**：放弃 ABAC / 五表细粒度方案；对象级 / 关系级授权下沉到 service 层，不进 RBAC 表；超管走配置注入 + short-circuit。
- **模块化 → core/ + zones/ 垂直切分（Day 3 落地）​**：每 zone 唯一 `router.py` + `service.py` 入口；端点 > 8 拆 `routers/`、service 函数 > 10 拆 `services/`；禁模块间横向 import、禁 core/ 反向 import zone。模块契约写入平台架构规范章节 3。

### 2.2 Day 4 的两件硬仗（认证安全语义）

- **refresh 并发竞态修复**：StrictMode 双挂载致同 jti 并发 refresh，rotation 一次性语义把后到的合法请求误杀。三层修复 = 前端 init `useRef` 去重 + 客户端 `refreshAccessToken` 单飞锁 + 后端 rotation 宽限放行。e2e B1 从 67% 失败降到 0 失败。
- **孤儿 token 根除（方案 C）​**：宽限放行的副作用是孤儿 active 行悬空到 7 天过期；治本方案 = 串行化 rotation（SQLite `BEGIN IMMEDIATE` 全局事件钩子 / PG `with_for_update()` 行锁）+ `successor_jti` 指针让 Branch A 唯一插入、Branch B 纯读重签同 jti；兜底方案 = superadmin-only 过期清理端点（手动触发，不引调度器）。这一仗确立了纪律 20（安全敏感改动必须 STOP 点）/ 21（验收禁假环境）/ 22（token 原文不落库）/ 23（全局行为变更必须注释 + 汇报）。

### 2.3 Day 5 Session 1 的扫除（文档归真）

- 抓出三处"文档 vs 现实"对齐项：AGENTS.md 描述幻影架构（org_id / Casbin / fastapi-users 优先 / `auth-tenant-rbac-modules` 目录）、平台架构规范缺 Day 4 变更记录、Day 4 归档已入库但状态脏。
- 5 处外科手术式修订 AGENTS.md（Project Identity / Core Design Principles / File Organization / API Routing / Current Phase）+ 1 次 amend 修正 Module Contract 引用错指。
- 平台架构规范 v1.1 补登：4.4 新配置项、5.1.1 事务串行化新小节、5.2 RefreshToken 三字段 + Branch A/B、6.1 流程摘要更新、变更记录表追加。
- 立纪律 24（文档归真 STOP 点）/ 25（AGENTS.md 单一真相源 + 双向 grep 自检）/ 26（编号绝不编造，无源用 `#TBD`）/ 27（写稿与提交分轮）/ 28（历史累积顾问主笔，本地 AI IDE 不得概述压缩）。

---

## 3. 教训与 Week 3 行动项

### 3.1 What went well（保持）

- **决策密度匹配产出**：Day 1 一天评审锁定 D1~D10 + ER 细化 + 字段拍板，后续 4 天无大返工；表明"评审先于代码"纪律值得继续。
- **联网核实版本号**：fastapi-users 15.0.5 维护模式、authx 1.6.0 Beta、依赖锁版均贴 PyPI/GitHub Releases 实际字符串，无幻觉。
- **覆盖率结构性约束**：`source=["boxbase"] + concurrency=["thread","greenlet"]` 一次配对，异步覆盖率从 75.93% 真实跃升至 93.83%/94%；security 100% 不是凑数，而是 hash/JWT/rotation/get_current_user 全路径单测撑起来的。
- **STOP 点真正阻止过事故**：Day 4 Part B 首版绕过 STOP 自行实现被驳回、Day 5 Session 1 派工写稿失守被预案接住，证明 STOP 不是装饰。

### 3.2 What didn't（改进）

- **本地 AI IDE 反复在"verbatim 贴回"上失守**：Day 5 Session 1 归档第一稿丢失工程纪律 1~23 条；Day 5 Session 2 架构规范派工 Stage A 用概述替代源码原文、Stage B 跳过顾问审 diff 直接 commit + push（结果对但流程违纪）。共性是把"贴回 / 检查"理解成"我读过、我帮你总结"。需在派工里把"原样输出 + 顾问审过 + 明确放行"三段切死，单独 enforce。
- **覆盖率虚低教训迟到**：Day 3 才发现配错 `source/concurrency` 致 75.93%，应在 Day 1 Alembic baseline 时就把覆盖率配置写对；Week 3 新模块前先 review 一次。
- **Playwright 配置认知盲区**：playwright.config.ts 无具名 project 致调用必须不带 `--project`，本会话 e2e 在新 HEAD 上未回归；下次会话开场顺手补一次。
- **Model docstring 与实现脱节**：`RefreshToken.revoked_reason` model docstring 写三值（rotation/logout/switch_tenant），auth.py 实际只写两值并靠 `successor_jti=NULL` 区分 switch_tenant 语义。这是 Week 2 唯一遗留代码不一致，Day 5 Session 2 核源码时抓到。

### 3.3 已知技术债（Week 3 评估，不阻塞功能开发）

1. **SQLite `BEGIN IMMEDIATE` 全局事务**：当前升级所有 SQLite 写事务；多 worker / 高并发生产部署需重评估锁粒度，目标仅串行化 refresh rotation 路径。
2. **​`RefreshToken.revoked_reason` 文档实现脱节**：建议改 model docstring 对齐实现（三值改两值 + 加一句"switch_tenant 复用 rotation，靠 successor_jti=NULL 区分"），不动 auth.py，避免新增字面量让 Branch B 判定逻辑多分支。
3. **rotation 宽限窗口（10s）机制本身保留**：v1.0 接受为防误杀的设计选择；高并发场景需观察其实际触发频率与孤儿率（虽已经 successor_jti 兜底，仍值得监控）。
4. **历史扩展点（v1.0 不实现）​**：部门/分组（通用 group + membership_groups 挂 membership 层）、PG RLS 第二防线、access token 即时吊销、ABAC / 五表 RBAC——均作为按需扩展点记录在 auth-tenant-rbac-design.md 章节 8.2。

### 3.4 Week 3 候选（待 Week 3 kickoff 拍板，本文档不规划）

- 基于 `zones/demo/` 起首个真实业务模块（计费 / 通知 / 文件 / 任务 等，由产品经理定）。
- refresh rotation 锁粒度精化（SQLite 路径限定）。
- 前端 e2e 在最新 HEAD 上回归 + 视情补充覆盖。
- 可选后台清理调度器（替代当前手动 cleanup 端点）。
- model docstring 修正（轻量，单 commit 顺手清）。

---

## 4. 一句话收尾

Week 2 把 BoxBase 从"Week 1 工程地基"推到"可用的多租户认证骨架 + 前端联调最小闭环"，决策密度高、返工低、安全语义在两次硬仗中被压力测试通过；遗留的不是功能债而是流程债（本地 AI IDE 的 verbatim 纪律 + 一处 docstring 不一致），Week 3 顺手清。
