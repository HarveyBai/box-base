# BoxBase v1.0 工作记忆摘要 — Week 2 Day 1 收官（滚动累积版）

## 1. 对话主题与用户意图

- **项目**：BoxBase v1.0 —— 轻量级、模块化 Python 多租户 SaaS 框架
- **用户角色**：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收拍板；用本地 AI IDE（Cursor / Claude Code / CodeBuddy）代替外包团队
- **本次会话核心任务**：Week 2 Day 1 架构评审 —— 认证 + 多租户 + RBAC，产出设计评审文档，**不写代码、不装依赖、不改源码**
- **开发周期**：16 周完成 v1.0；当前 Week 2 Day 1（2026-05-30，比原计划 6/2 提前 3 天启动）
- **本次会话重大收获**：用逐点拍板（D1–D10 + Q1–Q5 + Q-A~Q-E）方式在写代码前彻底定型架构主干；用户两次纠正 AI 结构性偏差（全局唯一用户模型、department 归位）；新立"写文档前先问清待确认项"纪律
- **历史阶段（Week 1，已闭环）​**：Day 1 工程骨架 + /health TDD + AGENTS.md；Day 2 uv.lock 入库 + pre-commit + GitHub Actions CI；Day 3 攻防演练验证双防线；Day 4 前端骨架（Vite 8 + React 19.2 + AntD 6）+ SSH 双客户端修复；Day 6 fnm→mise + Node 22 + CI warning 清零；Day 5 后端 /api 前缀 + 前端 Hello World + /api/health 联调（基线 dadf307）

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| 多租户隔离选哪种？ | Row-level + tenant_id。轻量定位 + SQLite/PG 一致性纪律 + 跨租户查询高频；Schema/DB 隔离否决（SQLite 无 schema） |
| 超管怎么设计？ | break-glass：配置文件注入 superadmin **username**（非自增ID）；归属系统保留租户（tenant_id NOT NULL）；请求上下文层集中 short-circuit 豁免 |
| 角色是租户内还是全局？ | tenant-scoped（Role 带 tenant_id）；每租户 seed 默认角色；超管硬编码全通过 short-circuit 不进 RBAC |
| RBAC 用几张表？ | 简化三表 + `resource:action` 权限串；权限 seed 固定（租户只组合不新建）；对象级所有权放 service 层 |
| 未来"只能改自己创建的/同部门读"怎么办？ | 三层访问控制模型：①租户隔离(ORM) ②RBAC(角色能否调操作) ③对象级/关系级(service 层 created_by / 同 group)；不逼升级五表/ABAC |
| 认证库选哪个？ | DIY 薄层（pyjwt + pwdlib + FastAPI 原生依赖注入）。联网核实 fastapi-users 15.0.5 **已维护模式**、authx 1.6.0 **Beta**；架构自主，现成库需迁就抽象 |
| 后期还能换认证方案吗？ | DIY 是唯一真满足"可最小代价更换"的，无上游生命周期；封装独立 security 模块，换库只动一个文件 |
| 密码哈希 / JWT 库？ | pwdlib[argon2] / pyjwt[crypto]（fastapi-users 15.0.5 内部同款）；算法 HS256，RS256 延后 |
| refresh token 策略？ | 方案 C 存库可撤销：jti 白名单(明文不落库) + 带 tenant_id + rotation + logout 真吊销；access 无状态接受 ≤30min 窗口 |
| 后期能平滑升级到 access 即时吊销吗？ | 能，近零返工：jti 表复用 + get_current_user 单点增查 + access 带 session jti；代价每请求一次会话查询，可加 Redis |
| Alembic 何时引入？ | Day 2 首件，先空 baseline 再写表；避免追认迁移；env.py 读 config；SQLite/PG 双跑 |
| 覆盖率门槛？ | pytest-cov 分层：全局 ≥80% / security+RBAC ≥95%，CI 强制；Day 1 仅记录不落地 |
| username/email 租户内唯一还是全局唯一？ | **全局唯一**（用户纠正）。一个自然人一个全局账号，经 membership 加入多组织 → User 去 tenant_id，新增 membership，角色挂 membership，token 带 active_tenant_id |
| department 放哪？ | **不放 User**（用户纠正）。部门是租户内 group 分组，挂 membership 层；v1.0 不建表；未来方向通用 group + membership_groups 多对多 |
| 内置默认租户与超管系统保留租户关系？ | 同一条 TENANT（is_system=true，Q-A） |
| 注册行为？ | 不自动登录、不自动建组织，默认以普通用户加入内置默认租户，强制赋默认 member 角色 |
| 审计字段怎么处理？ | 公共 Mixin 注入 created_at/updated_at/created_by/updated_by/deleted_at；软删除用 deleted_at 时间戳，与 ORM 过滤联动 |
| 明天重开会话提供什么？ | **两份都给**：本归档（过程记忆+纪律）+ 设计文档（落地蓝图）。归档记"为什么"，设计文档记"是什么"，不冗余 |
| —— 历史累积（Week 1）—— | |
| uv.lock 为何提交？ | 锁定依赖版本，uv 最佳实践 |
| GitHub Actions 能拦 --no-verify？ | 能，CI 云端独立 20 秒内熔断 mypy 错误 |
| 前端为何不走 AntD Pro 脚手架？ | pnpm create vite 干净项目 + 按需引入；Pro Components v3 仅 beta 延后 Week 4-5 |
| Vite proxy 前缀？ | 前端 /api/* → 后端 8000 不 rewrite，因后端也统一 /api，dev/prod 路径一致 |
| 归档命名规范？ | 日期+任务主题（Day 5 立）；日期以 current-time 为准 |

## 3. 文件与引用内容索引（含历史累积）

### 本次会话产出（Week 2 Day 1）
| 文件 | 路径 | 说明 |
|---|---|---|
| 认证/多租户/RBAC 设计评审文档 | docs/architecture/2026-W2-auth-tenant-rbac-design.md | **Day 2 唯一蓝图**，10 章：Scope/选型评审/ER/时序/API/测试/迁移依赖/风险/Day2预案/References。完整 ER、字段、API、Day 2 待办在此，本归档不复制 |
| 本归档 | docs/decisions/2026-0530-week2-day1-auth-design-review.md | Week 2 Day 1 收官（滚动累积版） |

### 后端（Week 1 产物，dadf307）
| 文件 | 路径 | 说明 |
|---|---|---|
| backend/boxbase/main.py | backend/boxbase/ | FastAPI app；APIRouter(prefix='/api')；openapi/docs/redoc 均挂 /api 下；HealthResponse(Literal) |
| backend/tests/test_health.py / test_openapi.py | backend/tests/ | /api/health + /api/openapi.json/docs/redoc 共 4 用例 |
| .pre-commit-config.yaml | 根目录 | 5 hook：ruff check / ruff format / mypy / frontend-eslint / frontend-prettier |
| .github/workflows/ci.yml | 根目录 | 3 job：lint-and-test / Frontend Lint & Typecheck / Secret Scan(TruffleHog)；pnpm/action-setup@v6 + node 22 |
| backend/pyproject.toml | backend/ | uv 管理，Python 3.12，dev 含 pre-commit |
| AGENTS.md | 根目录 | 跨工具 AI 规则单一真相源；含 API Routing Convention（所有后端路径挂 /api） |
| ops/SECRETS.md | ops/ | 敏感备忘，.gitignore 工具级隔离，永不入库 |

### 前端（Week 1 产物）
| 文件 | 路径 | 说明 |
|---|---|---|
| frontend/package.json | frontend/ | antd 6.4.3 / icons 6.2.3 / react 19.2 / react-router-dom v7 / vite 8 / typescript 6 / eslint 10 / prettier 3.8 |
| frontend/vite.config.ts | frontend/ | port 5173；proxy /api → localhost:8000 不 rewrite |
| frontend/src/api/health.ts | frontend/src/api/ | fetchHealth()，类型对齐后端 |
| frontend/src/pages/HomePage.tsx | frontend/src/pages/ | Hello World + Card 三态（loading/ok/error）；AntD v6 Alert 用 title |

### 决策与归档历史
| 文件 | 路径 | 说明 |
|---|---|---|
| docs/decisions/2026-0529-api-health-integration.md | docs/decisions/ | Day 5 收官归档（上一份滚动归档来源） |
| docs/retrospectives/2026-W1-retrospective.md | docs/retrospectives/ | Week 1 全景复盘 |

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| web_search / web_fetch | 本次认证库联网核实 | fastapi-users **15.0.5**(2026-03-27, **维护模式**, 依赖 pyjwt[crypto] >=2.12.0 + pwdlib[argon2,bcrypt])；authx **1.6.0**(2026-04-30, **4-Beta**)；横评 WorkOS 2026；版本号均贴实际字符串 |
| git（历史） | 版本控制 | 最新基线 dadf307（Day 5 收官）；tag week1-complete @ 07ee750 |
| GitHub Actions（历史） | 云端 CI | Run #14 dadf307 全绿 24s，3 job 全绿，Annotations 清零 |
| pre-commit / pytest / 前端三连（历史） | 验收 | pre-commit 5/5；pytest 4/4；tsc/eslint/prettier exitCode 0 |
| mise（历史） | 运行时管理 | 2026.5.15，node@22.22.3（Active LTS）；替代 fnm |

## 5. 决策与结论（含历史累积）

### Week 2 架构决策（本次会话，A/B/C 档 + Q）
1. **D2 隔离**：Row-level + tenant_id；RLS 第二防线 Week 2 不启用、预留 hook
2. **超管**：配置注入 superadmin username；系统保留租户(路B)；请求上下文层集中 short-circuit
3. **D4 角色**：tenant-scoped；每租户 seed 默认角色(方案A)；超管硬编码全通过(路A)
4. **D3 RBAC**：简化三表 + resource:action；权限 seed 固定；对象级放 service 层；三层访问控制模型
5. **D1 认证库**：DIY 薄层(pyjwt+pwdlib+FastAPI 依赖注入)，独立 security 模块；fastapi-users/authx 附证据保留为候选
6. **D5/D6**：pwdlib[argon2] / pyjwt[crypto]；HS256，RS256 延后
7. **D7 refresh**：方案C 存库可撤销，jti 白名单 + rotation + logout 真吊销；access 无状态 ≤30min 窗口；预留升级 access 即时吊销；access 30min/refresh 7d 为启动配置项
8. **D8 Alembic**：Day 2 首件，空 baseline 优先；**D9 覆盖率**：分层 80%/95% CI 强制；**D10 admin**：单列 /api/admin/* 走 short-circuit
9. **Q1–Q5**：UUID 主键 / 关联表全带 tenant_id / 注册不自动登录默认加入内置租户 / refresh rotation / Department 只留概念不建表
10. **全局用户模型（用户纠正一）​**：User 全局唯一(username/email/phone 单列唯一)，去 tenant_id；新增 MEMBERSHIP 核心表；角色挂 membership；token 带 active_tenant_id；多租户切换最小版 /api/auth/switch-tenant
11. **department 归位（用户纠正二）​**：从 User 删除；部门=租户内 group 挂 membership 层；v1.0 不建表；未来方向通用 group + membership_groups 多对多
12. **Q-A~Q-E**：内置默认租户=超管系统保留租户同一条(is_system) / membership 强制默认 member / 提供 switch-tenant(P2) / phone nullable 但全局唯一 / membership 加 is_default 登录未指定进 default
13. **审计字段**：公共 Mixin 注入五字段；软删除 deleted_at 时间戳与 ORM 过滤联动；TENANT 保留 slug 全局唯一索引(子域名预留)

### 工程化决策（Week 1 历史，长期有效）
1. pre-commit local repo 模式 + uv run --directory backend；CI 用 setup-uv + uv sync
2. 双重防线：pre-commit(本地) + GitHub Actions(云端)
3. 前端栈：React 19.2 + Vite 8 + TS 6 + AntD v6；Pro Components 延后 Week 4-5；包管理 pnpm 10.33 / 后端 uv
4. 运行时 mise(scoop 装)管 Node 22；SECRETS.md 走 .gitignore 工具级隔离
5. 后端所有路由统一 /api 前缀（含 openapi/docs/redoc）；Vite proxy 不 rewrite，dev/prod 一致

## 6. 错误与修正（含历史累积）

| 错误/偏差 | 发现时机 | 修正 |
|---|---|---|
| 本次：w2-day1.txt 草案落后当前进度(commit/日期/CI/命名 5处) | 顾问核对 | 列硬伤，对齐后再用 |
| 本次：AI 草图用"租户内唯一"User 模型 | 用户纠正 | 重构全局唯一 + membership |
| 本次：AI 把 department_id 放 USER 表 | 用户纠正 | 移除；部门归位 membership 层，v1.0 不建 |
| 本次：AI 文档写完后才抛 Q-A~Q-E | 用户批评 | 立纪律：写文档前先问全再动笔 |
| 本次：AI 首版收尾归档未按提示词做滚动累积（只写当天、丢历史、格式不符） | 用户察觉对比变短 | 重做为合规滚动累积版（本文件） |
| 历史：误判 React19/Vite8/TS6/ESLint10 为幻觉 | 用户截图反驳 | 联网核实，版本判断必先联网 |
| 历史：ssh-add 可见但 push 仍要 passphrase | push 报错 | git config core.sshCommand 永久固化 |
| 历史：mise 装完 cmd 找不到 node | mise doctor shims_on_path:no | 手动写 User PATH |
| 历史：PowerShell CLIXML 吞 stdout | install 卡住 | 单引号包版本号 / 改 findstr；mise 迁移后根治 |
| 历史：Day 5 顾问角色错位 + browser_task_tool 越界建空仓库 | 用户质问 | 明文写入角色边界规约 |

## 7. 讨论演变（文字描述）

本次会话开门：用户提供 Day 5 收官归档对齐上下文 → 提供早期草拟的 w2-day1.txt 派工草案 → 顾问核对发现其落后当前进度（commit 07ee750/日期5-28/CI Run#9/旧命名），判定需对齐补丁，但骨架（角色边界、联网核实纪律、不写代码、10 章结构）可保留 → 用户决定先把所有有歧义的决策点逐一过完再写文档。

决策推进按依赖从底向上：D2 隔离（拍 Row-level + 超管三子项）→ D4 角色作用域（tenant-scoped + 超管 short-circuit）→ D3 RBAC（三表 + resource:action，用户追问 ownership/同部门 → 顾问给三层访问控制模型）→ D1 认证库（用户给四判据，顾问联网核实发现 fastapi-users 维护模式，倾向翻转为 DIY 薄层）→ D5/D6 随 D1 隐含锁定 → D7 refresh（用户加码到方案C 存库可撤销，追问可否平滑升级 access 即时吊销，顾问论证可近零返工）→ D8/D9/D10 工程细节一次过。

用户补充关键纪律：在用户明确放行前不得擅自写派工提示词。随后进入 Q1–Q5 拍板，再进入 ER 细化：用户提出 username/email/phone 全局唯一（推翻 AI 草图租户内唯一模型）→ 顾问重构为 User 全局实体 + membership 核心表 + 角色挂 membership + token 带 active_tenant_id；用户指出 department 放错（应是租户内 group）→ 顾问归位到 membership 层、v1.0 不建表、未来通用 group 方案。顾问首版文档写完后才抛出 Q-A~Q-E，被用户批评 → 立"写文档前先问清"纪律。Q-A~Q-E 拍定后顾问更新文档至完整版。

收尾：用户确认无大问题，要求写 Day 1 收尾归档，今日由本地 AI IDE 一并提交保持仓库干净，明日重开会话进 Day 2。用户询问明天需提供几份文件 → 顾问答"两份"（归档=过程记忆、设计文档=蓝图）。顾问首版归档未按归档提示词做滚动累积（只写当天、丢失 Week1/Day5 历史、格式不符）→ 用户察觉变短并质疑是否按提示词执行 → 顾问承认偏差、确认提示词无需修改、重做为本合规滚动累积版。

## 8. 当前状态与后续步骤

### Git 状态
- 基线 dadf307（Week 1 全闭环，CI Run #14 全绿，tag week1-complete @ 07ee750）
- **待提交**（用户将让本地 AI IDE 一并 commit 保持干净）：
  - docs/architecture/2026-W2-auth-tenant-rbac-design.md（评审文档）
  - docs/decisions/2026-0530-week2-day1-auth-design-review.md（本归档）
- Day 1 评审无源码变更
- 建议 commit message：docs: add Week 2 Day 1 auth/tenant/RBAC design review and archive

### Completed
- Week 1 全部闭环（Day 1-6）
- Week 2 Day 1：认证+多租户+RBAC 架构主干全部决策点闭环；设计评审文档落地

### Next Steps（Day 2，新会话）
- **明天重开会话同时提供本归档 + 设计文档两份**；新会话 AI 开场先复述同步点 + 确认角色边界
- 依设计文档**章节 9 Day 2 待办预案**（9 个 30min 切片）出派工：Alembic baseline → 审计 Mixin + USER/TENANT → MEMBERSHIP → ROLE/PERMISSION/关联表 → REFRESH_TOKEN → ORM 强制过滤(tenant+deleted_at)+请求上下文 → security 模块(含 active membership 校验) → seed → pytest-cov 首批单测
- 待 Day 2 复核（设计文档 8.3）：系统/默认租户合并 seed、is_default 唯一约束实现、switch-tenant 是否 rotation

### 技术栈备忘（最新）
- 后端：FastAPI + SQLAlchemy 2.0 + Pydantic v2 + uv（Python 3.12）；统一 /api 前缀
- Week 2 待装（Day 2）：pwdlib[argon2]、pyjwt[crypto]（HS256）、alembic、pytest-cov
- 隔离：Row-level + tenant_id，ORM 强制过滤(tenant + deleted_at)
- 认证：DIY 薄层 security 模块；refresh 存库可撤销 + rotation
- 前端：Node 22.22.3(mise) + React 19.2 + Vite 8 + TS 6 + AntD 6.4.3 + react-router-dom v7
- 数据库：SQLite(dev) / PostgreSQL(prod)，双环境迁移一致
- 工具链：ruff + mypy + pytest + ESLint 10 + Prettier 3.8 + pre-commit + GitHub Actions + TruffleHog；mise 2026.5.15

### 工程纪律（含历史累积）
1. 顾问只出决策建议/派工提示词/验收清单；不粘源码、不进 Agent Mode、不调 browser_task_tool
2. 【本次新立】写文档/派工前先把待确认项问全，用户拍完再动笔，不得事后补问题
3. 设计文档/归档由顾问写完整内容（markdown），本地 AI IDE 只存文件 + commit，不创作
4. commit 前本地 AI IDE 执行 git status --short 列出文件给用户确认；保持仓库干净
5. 版本号必须联网核实并贴实际字符串；技术栈版本变更先报备
6. 带日期文件名以 current-time 为准（不凭直觉顺延）
7. 归档为滚动替换式：合并历史 + 本次，老内容压缩成结论/纪律，新会话只读这一份
8. 严禁 --no-verify / --force push / 自动 prettier --write 不经确认
9. PowerShell CLIXML 黑名单（Select-String/ConvertFrom-Json 等输出可能被吞）；mise 迁移后已根治
10. 修复 deprecation warning（如 AntD message→title）属合理范围；改 props 语义需停下确认
