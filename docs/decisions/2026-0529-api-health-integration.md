# BoxBase v1.0 工作记忆摘要 — Day 5 收官（滚动累积版）

## 1. 对话主题与用户意图

- **项目主题**：继续构建 BoxBase v1.0 —— 轻量级、模块化的 Python 多租户 SaaS 框架
- **用户角色**：产品经理 baihw（GitHub: HarveyBai），不写代码，负责验收；用本地 AI IDE（Cursor / Claude Code / CodeBuddy）代替外包团队
- **本次会话核心任务**：Day 5 主任务执行 —— 后端统一 /api 路由前缀 + 前端 Hello World 页面 + /api/health 前后端联调 + AGENTS.md 路由规约增补 + 单 commit 推送 CI 全绿
- **开发周期**：16 周完成 v1.0，当前处于 Week 1 Day 5 完成阶段（2026-05-29），所有 Week 1 任务已全部闭环
- **本次会话重大收获**：归档命名规范从"日期+Day编号"切换为"日期+任务主题"；派工提示词新增 git status 检查步骤防止遗漏未提交文件；顾问角色边界规约首次完整落地执行

## 2. 关键问答（含历史累积）

| 问题 | 关键回答 |
|---|---|
| uv.lock 为何要提交？ | 锁定依赖版本，确保所有环境依赖完全一致，是 uv 最佳实践 |
| pre-commit 路径配置为何出错？ | --directory backend 已切 CWD，entry 中改相对路径 . 和 boxbase/ |
| GitHub Actions 能拦截 --no-verify 绕过吗？ | 能。CI 在云端独立运行，20 秒内独立发现 mypy 错误并熔断 |
| SSH key 有密码每次都要手动输入？ | Windows OpenSSH Agent + ssh-add 缓存 + git config --global core.sshCommand 'C:/Windows/System32/OpenSSH/ssh.exe'（Day 4 永久固化） |
| Pydantic Literal 类型有何价值？ | mypy 能通过 Literal["ok"] 在静态检查阶段发现业务逻辑错误 |
| 前端要不要走 Ant Design Pro 官方脚手架？ | 不走。pnpm create vite 干净项目 + 按需引入 antd / pro-components |
| Vite 默认装了 React 19 + TS 6 + Vite 8 + ESLint 10，是 AI 幻觉吗？ | 不是。联网核实全部真实存在；后续所有版本判断必须先联网 |
| AntD v6 + Pro Components v3 能装吗？ | AntD 6.4.3 可装、零警告。Pro Components v3 仅 beta，v2 锁死 antd 5；延后到 Week 4-5 |
| ssh-add -l 看得到 key 但 git push 还是要密码？ | Windows 双 SSH 客户端冲突：ssh-add 用 Windows OpenSSH，git 默认用 Git for Windows 自带 SSH |
| pnpm add antd@^6 在 PowerShell 命令输出消失？ | @ 字符触发变量解析 + CLIXML 包装吞 stdout。安全做法：单引号包裹版本号 'antd@^6' |
| SECRETS.md 能否加入 .gitignore 永久隔离？ | 可以，工具保证优于人工纪律 |
| PowerShell CLIXML 问题根因？ | Select-String/ConvertFrom-Json/Get-Process 等命令被管道捕获时触发 XML 包装 |
| 能否用 cmd 替代 PowerShell？ | fnm 不支持 cmd（PATH 注入依赖 PowerShell profile），需迁移到 mise |
| mise 是否支持 scoop 安装？ | 是，scoop install mise 官方支持 |
| mise shims 装完 cmd 仍找不到 node？ | mise doctor 显示 shims_on_path: no。手动把 %USERPROFILE%\AppData\Local\mise\shims 加入 User PATH |
| CI 报 Node.js 20 actions deprecated warning？ | GitHub 2026-06-02 强制切 Node 24。修复：pnpm/action-setup@v4 → @v6（v6.0.8 内部已用 Node 24） |
| 本地要不要也升 Node？ | 升 Node 22（Active LTS，维护到 2027-04）。Node 24 是 Current，2026-10 才转 LTS |
| Vite proxy 路径前缀怎么定？ | 前端 /api/* → 后端 8000，不做 rewrite，因为后端也统一 /api 前缀。dev/prod 路径完全一致 |
| OpenAPI 文档（/docs /redoc /openapi.json）也挪到 /api 下吗？ | 是（方案 B）。规约纯净度优先：所有后端可访问路径都在 /api/* 下，未来反向代理只暴露一条规则 |
| TDD 红绿循环在路径重构时是否必须执行？ | 不必须。TDD 红绿循环是验证测试有效性的手段，机械路径重构直接看绿即可 |
| 归档文件命名用 Day 编号还是日期+主题？ | 切换为日期+主题。Day 编号只写在归档内容里作为任务追踪标签，不出现在文件名中 |
| 派工结束后如何保证本地无未提交文件？ | 每份派工提示词的 commit 步骤前固定加 git status --short 检查，逐一列出给用户确认后再 commit |
| Antd v6 Alert message prop 被 deprecated？ | v6 中 message 改为 title，本地 AI IDE 发现后自主修复，属于合理范围（修复 deprecation 对齐当前版本 API） |
| 归档由谁编写？ | 会话内顾问 AI 编写完整归档内容输出为 markdown 代码块；本地 AI IDE 只负责创建文件和 commit，不自己编写归档 |

## 3. 文件与引用内容索引（含历史累积）

### 后端（Day 1-5 产物）

| 文件 | 路径 | 说明 |
|---|---|---|
| .gitignore | 根目录 | uv.lock 已纳入版本控制；通配 node_modules/、dist；Day 6 新增 ops/SECRETS.md |
| backend/uv.lock | backend/ | 依赖锁定文件，含 pre-commit 4.6.0 |
| .pre-commit-config.yaml | 根目录 | 5 个 hook：ruff check / ruff format --check / mypy / frontend-eslint / frontend-prettier；前端两个 hook 通过 files 正则限定 ^frontend/ 触发范围 |
| backend/pyproject.toml | backend/ | pre-commit 4.6.0 为 dev 依赖 |
| .github/workflows/ci.yml | 根目录 | 3 个 job：lint-and-test / Frontend Lint & Typecheck / Secret Scan (TruffleHog)；pnpm/action-setup@v6 + node-version: '22' |
| backend/boxbase/main.py | backend/boxbase/ | FastAPI app；APIRouter(prefix='/api') 挂载业务路由；FastAPI() 构造显式配置 openapi_url='/api/openapi.json' / docs_url='/api/docs' / redoc_url='/api/redoc'；HealthResponse 模型（status: Literal["ok"] / version: str / service: Literal["boxbase"]） |
| backend/boxbase/__init__.py | backend/boxbase/ | __version__ = "0.1.0" |
| backend/tests/test_health.py | backend/tests/ | /api/health TDD 测试（1 个用例），ASGITransport + AsyncClient |
| backend/tests/test_openapi.py | backend/tests/ | /api/openapi.json / /api/docs / /api/redoc 三个用例 |
| AGENTS.md | 根目录 | 跨工具 AI 规则单一真相源；Day 5 新增"API Routing Convention"段落：所有后端可访问路径统一挂在 /api 前缀下，未来反向代理只暴露 /api/* 一条规则 |
| ops/PROMPTS.md | ops/ | 个人提示词备忘 |

### 前端（Day 4-5 产物）

| 文件 | 路径 | 关键内容 |
|---|---|---|
| frontend/package.json | frontend/ | antd ^6 (实 6.4.3) / @ant-design/icons ^6 (实 6.2.3) / react ^19.2.6 / react-router-dom v7 / vite ^8 / typescript ~6.0.2 / eslint ^10.3.0 / prettier ^3.8.3 |
| frontend/vite.config.ts | frontend/ | port 5173 / host true；resolve.alias '@' → import.meta.dirname/src；server.proxy { '/api': { target: 'http://localhost:8000', changeOrigin: true } }（无 rewrite） |
| frontend/eslint.config.js | frontend/ | Flat Config；rules + ignores + 末尾 eslintConfigPrettier |
| frontend/tsconfig.app.json | frontend/ | strict 强化：noUncheckedIndexedAccess / noImplicitOverride / forceConsistentCasingInFileNames；paths "@/*": ["./src/*"] |
| frontend/.prettierrc.json | frontend/ | semi false / singleQuote true / trailingComma all / printWidth 100 / endOfLine lf |
| frontend/src/main.tsx | frontend/src/ | StrictMode + RouterProvider + 引入 router.tsx |
| frontend/src/router.tsx | frontend/src/ | createBrowserRouter：/ → App，children 含 index→HomePage, login→LoginPage, dashboard→DashboardPage, *→NotFoundPage |
| frontend/src/App.tsx | frontend/src/ | ConfigProvider + Layout（Header "BoxBase v1.0" + Content Outlet），是路由壳，不是页面 |
| frontend/src/api/health.ts | frontend/src/api/ | Day 5 新增：fetchHealth() + HealthResponse interface（status: 'ok' / version: string / service: 'boxbase'）；fetch('/api/health')，非 2xx 抛错 |
| frontend/src/pages/HomePage.tsx | frontend/src/pages/ | Day 5 彻底重写：Hello World 主题 + Card 三态（loading: Spin / ok: Tag+Descriptions / error: Alert）；底部保留 Test 404 / Go Login / Go Dashboard 三个导航入口；Antd v6 Alert 用 title 而非 message（deprecation 已修复） |
| frontend/src/pages/LoginPage.tsx | frontend/src/pages/ | 占位页，未细改 |
| frontend/src/pages/DashboardPage.tsx | frontend/src/pages/ | 占位页，未细改 |
| frontend/src/pages/NotFoundPage.tsx | frontend/src/pages/ | 404 占位页，未细改 |

### 决策与归档文档

| 文件 | 路径 | 说明 |
|---|---|---|
| docs/decisions/2026-0526-day1-archive.md | docs/decisions/ | Day 1 工作记忆 |
| docs/decisions/2026-0526-day2-3-archive.md | docs/decisions/ | Day 2-3 工作记忆 |
| docs/decisions/2026-0527-day4-tech-stack-update.md | docs/decisions/ | Day 4 决策：React 18→19 + Pro Components 延后 |
| docs/decisions/2026-05-27-ad-frontend.md | docs/decisions/ | 用户私人备忘 |
| docs/decisions/2026-0527-day6-archive.md | docs/decisions/ | Day 6 归档（含 CLIXML 纪律） |
| docs/decisions/2026-0528-day6-ending-archive.md | docs/decisions/ | Day 6 收官归档（mise + Node 22 + CI warning 清零）【本次 commit 一并提交】 |
| docs/decisions/2026-0529-api-health-integration.md | docs/decisions/ | 本文件：Day 5 收官归档（/api 前缀规约 + Hello World 联调） |
| docs/retrospectives/2026-W1-retrospective.md | docs/retrospectives/ | Week 1 全景复盘 |
| ops/COMMANDS.md | ops/ | 用户私人命令备忘 |
| ops/SECRETS.md | ops/ | 用户敏感备忘，通过 .gitignore 工具级隔离，永久不入库 |

## 4. 工具使用与结果（含历史累积）

| 工具 | 用途 | 关键结果 |
|---|---|---|
| git | 版本控制 | commit 链：167ff19 → 0a1af7a → ed8cec8 → 3f32cd5 → 6f4a3fb → 38cc2ec → 411d693 → ec0db25 → baf3181 → bea8309 → dadf307（最新，Day 5 收官） |
| tag week1-complete | Week 1 封盘 | @ 07ee750 |
| uv add --dev pre-commit | 后端 pre-commit | 4.6.0 |
| pre-commit run --all-files | 全量验证 | 5/5 hooks 全绿（ruff check / ruff format / mypy / eslint / prettier） |
| GitHub Actions | 云端 CI | Run #1-#14 全部记录在册；Run #14 dadf307 全绿 24s，3 job 全绿 |
| pnpm create vite | 前端脚手架 | React 19.2 + Vite 8 + TS 6 + ESLint 10 |
| pnpm add（带单引号） | 装 UI 库 | 'antd@^6' '@ant-design/icons@^6' 成功，215 包零警告 |
| scoop install mise | 安装 mise | 2026.5.15 windows-x64 |
| mise use --global node@22 | Day 6 升级 | 22.22.3 Active LTS（维护到 2027-04） |
| uv run pytest -v | 后端测试 | 4/4 全绿（含 /api/health + /api/openapi.json + /api/docs + /api/redoc） |
| pnpm tsc --noEmit | 前端类型检查 | exitCode 0 |
| pnpm eslint . | 前端 lint | exitCode 0 |
| pnpm prettier --check . | 前端格式检查 | All matched files use Prettier code style! |

## 5. 决策与结论（含历史累积）

### 后端工程化（Day 1-3 已落地）
1. pre-commit hooks 用 local repo 模式 + uv run --directory backend
2. CI 用 astral-sh/setup-uv@v5 + uv sync --all-groups
3. 双重防线：pre-commit（本地）+ GitHub Actions（云端）

### 前端技术栈（Day 4 决策）
1. 接受新栈：React 19.2 + Vite 8 + TypeScript 6 + Ant Design v6
2. Pro Components 延后到 Week 4-5：v3 仅 beta，v2 锁死 antd 5
3. 轻量集成路线：不用 Ant Design Pro 官方脚手架
4. 包管理器：前端 pnpm 10.33+，后端 uv（Python 3.12）
5. 路径别名：'@/' → 'src/'，Vite 和 TS 严格对齐
6. TypeScript strict 强化：noUncheckedIndexedAccess / noImplicitOverride / forceConsistentCasingInFileNames
7. Prettier：semi false / singleQuote true / printWidth 100 / endOfLine lf

### Day 6 决策（mise 迁移 + Node 22 + CI 对齐）
1. SECRETS.md 工具级隔离：加入 .gitignore，git 自动隔离
2. fnm → mise 迁移：通过 scoop 安装，shims 机制支持 PowerShell/cmd/bash 三 shell
3. mise shims 持久化：手动写入 User PATH
4. Node 20 → 22 升级：22 是当前 Active LTS（维护到 2027-04）
5. pnpm/action-setup v4 → v6：v6.0.8 内部已用 Node 24；跳过 v5（过渡版本）
6. CI node-version 20 → 22：让本地和 CI 完全对齐

### Day 5 决策（本次会话落地）
1. 后端所有业务路由统一 /api 前缀：APIRouter(prefix='/api') + app.include_router(api_router)
2. OpenAPI 文档也挪到 /api 下（方案 B）：openapi_url='/api/openapi.json' + docs_url='/api/docs' + redoc_url='/api/redoc'
3. Vite proxy 配 /api → http://localhost:8000，不做 rewrite，dev/prod 路径完全一致
4. 前端新增 src/api/health.ts 封装 fetch，类型用 Literal 对齐后端 HealthResponse
5. HomePage 彻底替换 Boot Check 主题为 Hello World + Card 三态（loading/ok/error）；保留底部 3 个导航链接
6. TDD 红绿循环仅在验证测试有效性时执行；机械路径重构直接看绿
7. 归档命名规范：从"日期+Day编号"切换为"日期+任务主题"；Day 编号只作为内容字段保留
8. 派工提示词 commit 步骤前固定加 git status --short 检查，用户逐一确认后再 commit
9. 归档由顾问 AI 编写完整内容输出 markdown 代码块；本地 AI IDE 只负责存文件和 commit

### 工程纪律（含历史累积）
1. 工具保证 > 人工纪律（SECRETS.md 走 .gitignore，不再人工 unstage）
2. Commit 规范：Conventional Commits（英文），多行 body 列具体变更
3. 严禁 --no-verify、--force push、自动 prettier --write 不经确认
4. 验收纪律：tsc / eslint / prettier 三连 exitCode 0；网络层 + 应用层 + 类型层独立交叉验证
5. AI 工具自由发挥要按住：技术栈版本变更必须先报备
6. 能当次做完的不留尾巴：归档、配置、依赖统统当天闭环
7. PowerShell CLIXML 黑名单：Select-String / ConvertFrom-Json 等输出可能被 XML 包装吞掉；mise 迁移后已根治
8. 【角色边界规约】顾问 AI 只出三类产出：决策建议、派工提示词、验收清单；不要求粘贴源码；不进 Agent Mode；不调用 browser_task_tool
9. 修复 Antd deprecation warning（如 message→title）属于合理范围，不需要报备；改变 props 语义则需要停下确认
10. 每次任务结束 commit 前，本地 AI IDE 必须执行 git status --short 并列出所有未提交文件给用户确认，确保本地始终是干净状态
11. 派工提示词中需要转发给本地 AI IDE 的内容，必须单独输出为完整可复制代码块，与顾问给用户看的分析说明明确分开

## 6. 错误与修正（含历史累积）

| 错误 | 发现时机 | 修正方式 |
|---|---|---|
| Day 2-3：.pre-commit-config.yaml 路径 backend/backend/ | Step D 验证 | 改相对路径 . / boxbase/ |
| Day 2-3：归档文件漏 commit | Day 4 git status 发现 | Day 4 commit 38cc2ec 补登 |
| Day 4：Set-Service ssh-agent PermissionDenied | 用户截图 | 改用管理员 PowerShell |
| Day 4：误判 React 19 / Vite 8 / TS 6 / ESLint 10 是 AI 幻觉 | 用户截图反驳 | 联网核实全部真实；版本判断必须先联网 |
| Day 4：Pro Components v3 NO_MATCHING_VERSION | install 报错 | 调研后延后到 Week 4-5 |
| Day 4：PowerShell @ 字符 + CLIXML 吞 stdout | install 卡住 | 单引号 + 读 package.json 验证 |
| Day 4：5173 端口被僵尸 node 进程占用 | Vite 漂移到 5174/5175 | 手动 Stop-Process 清理 |
| Day 4：ssh-add -l 可见但 git push 仍要 passphrase | push 报 read_passphrase | git config --global core.sshCommand 永久固化 |
| Day 6：派工提示词用 PowerShell Select-String | 检查项卡 CLIXML | 改 findstr / cmd 语法 |
| Day 6：建议 cmd 但 fnm 不支持 cmd | 用户截图 pnpm 不可用 | 改为迁移 mise 方案 |
| Day 6：mise 装完 Node 后 cmd 仍找不到 node | cmd /c "node --version" 报错 | mise doctor 发现 shims_on_path: no；手动写入 User PATH |
| Day 6：[Environment]::SetEnvironmentVariable 时 $env:PATH 含特殊字符 | "文件名、目录名或卷标语法不正确" | 直接传完整 PATH 字符串而非通过变量 |
| Day 6：pre-commit run --all-files 反复 exit 1 无输出 | 退出码 1 但输出被吞 | 改为单独跑各 hook，全绿 |
| Day 6：升级 ci.yml 时只改 pnpm/action-setup 漏掉 node-version | AI 顾问提醒 | 单独 commit bea8309 把 node-version: 20 → '22' 对齐 |
| Day 5（上次会话）：顾问角色错位 + browser_task_tool 越界创建 baihw/boxbase 空仓库 | 用户察觉并质问 | 明文写入角色边界规约；用户手动删除 baihw/boxbase 空仓库 |
| Day 5（本次）：2026-0528-day6-ending-archive.md 漏 commit | 任务结束后用户检查发现 | 与本次归档文件一并在下一个 commit 提交；派工纪律增补 git status 检查步骤 |
| Day 5（本次）：Antd v6 Alert message prop deprecated | 本地 AI IDE 自主发现 | 改为 title，属于合理范围修复 |

## 7. 讨论演变

Day 1（前期）完成工程骨架 + /health TDD + AGENTS.md → Day 2 修 .gitignore 把 uv.lock 纳入版本控制 → 配置 pre-commit hooks → 全绿 → 搭 GitHub Actions CI（Run #1 全绿）

→ Day 3 攻防演练故意引入 3 类错误 → 验证 pre-commit 拦截 + --no-verify 绕过 + GitHub Actions 20 秒熔断 → 双重防线确认有效

→ Day 4 SSH Agent 配置 + 前端骨架 → AI 默认装 React 19 + Vite 8 + TS 6 + ESLint 10 → 顾问误判为幻觉 → 用户截图反驳 → 联网核实全部真实 → 拍板接受新栈 → 装 antd 6.4.3 + icons 6.2.3 → 写最小验证页面 → 阶段 3 工程化（prettier + eslint-config-prettier + tsconfig strict + vite alias）→ 阶段 4 Git 接入 → push 报 read_passphrase → 发现 Windows 双 SSH 客户端冲突 → core.sshCommand 修复 → CI Run #4 全绿

→ Week 1 收官期 提出 SECRETS.md 工具级隔离 + 健康检查 9 项 → AI 工具卡在 PowerShell CLIXML → 顾问建议 cmd → 用户反馈 fnm 不支持 cmd → 决策换 mise → 用户手动 scoop install mise

→ Day 6 mise 迁移派工 → mise --version 2026.5.15 + profile 备份追加 mise activate → mise use --global node@20 装 20.20.2 → cmd 验证翻车 → mise doctor 发现 shims_on_path: no → 手动写入 User PATH → cmd 全绿 → scoop uninstall fnm → 清理 profile fnm 行 → pytest 4/4 + 三连绿 + pre-commit 5/5 → AGENTS.md 更新 + .gitignore 追加 ops/SECRETS.md → commit ec0db25 → CI Run #11 全绿

→ CI Run #11 出现 pnpm/action-setup@v4 deprecated warning → 修复升级到 v6.0.8 → 用户主动提出本地也升级 → 选 Node 22 Active LTS → mise use --global node@22 + ci.yml v4→v6 → commit baf3181 → 顾问追问 ci.yml node-version: 20 字段也该改 → commit bea8309 → CI Run #13 全绿 23s，Annotations 完全清空 → Week 1 + Day 6 全部尾巴清零

→ **本次会话开门**：用户发送 Day 6 收官归档对齐上下文 → 顾问复述同步点 + 确认角色边界 → 提出两个开门确认（派工切片粒度 / TDD 严格度）→ 用户拍板：A 大派工（4 个 STOP 点）+ 直接看绿

→ 顾问出完整 Day 5 大派工提示词（含 4 个 STOP 点）→ 用户复制给本地 AI IDE

→ STOP 1（后端 /api 前缀改造）：本地 AI IDE 修改 main.py + test_health.py + test_openapi.py → pytest 4/4 全绿 → 用户贴输出 → 顾问验收通过

→ STOP 2（前端 Vite proxy + api 层）：本地 AI IDE 修改 vite.config.ts + 新增 src/api/health.ts → prettier 发现格式问题自动修复 → 三连全绿 → 顾问验收通过；记录 prettier --write 灰色地带备注

→ 用户提问"顾问给的预警是否需要转发给 AI IDE"→ 顾问澄清：预警是给用户看的背景说明，直接跟 AI IDE 说"继续 STOP 3"即可 → 确立格式纪律：需要转发的内容必须单独输出完整可复制代码块

→ STOP 3（HomePage 彻底替换 + 浏览器联调）：本地 AI IDE 重写 HomePage.tsx → 联调 ok 态（绿色 Tag + Descriptions）+ error 态（红色 Alert 502）→ 发现并自主修复 Antd v6 Alert message→title deprecation → 三连全绿 → 两张截图确认 → 顾问验收通过

→ STOP 4（AGENTS.md 增补 + 全量验收 + commit + push）：本地 AI IDE 新增 API Routing Convention 段落 → pre-commit 5/5 + pytest 4/4 + 前端三连全绿 → git status 显示 7 个文件干净 → 单 commit dadf307 + push → CI Run #14 全绿 24s

→ **收尾讨论**：用户发现 2026-0528-day6-ending-archive.md 漏 commit → 决定与本次归档一并提交 → 讨论归档命名规范 → 拍板切换为"日期+任务主题"格式（旧文件不改名）→ 讨论派工 commit 步骤增补 git status 检查 → 拍板固化为派工纪律 → 顾问出本归档

## 8. 当前状态与后续步骤

### Git 历史（最新 5 条）
- dadf307 feat: hello world page with /api/health integration（Day 5 收官，最新）
- bea8309 ci: align CI node-version with local Node 22
- baf3181 ci: upgrade Node to 22 LTS and pnpm/action-setup to v6
- ec0db25 chore: migrate Node runtime from fnm to mise, gitignore SECRETS.md
- 411d693 docs: backfill Day 6 archive and Week 1 retrospective with hotfix timeline

### 待提交文件（本次归档 commit 需包含）
- docs/decisions/2026-0528-day6-ending-archive.md（已存在，漏 commit）
- docs/decisions/2026-0529-api-health-integration.md（本文件，新增）

    建议 commit message：
    docs: add Day 5 archive and backfill Day 6 ending archive

### 远端仓库
git@github.com:HarveyBai/box-base.git（已同步至 dadf307）

### CI 状态
- Run #14 dadf307 / 24s / 全绿（lint-and-test 16s / Frontend Lint & Typecheck 19s / Secret Scan 8s）
- 3 个 job 全绿，Annotations 清零

### tag
- week1-complete @ 07ee750

### Completed（Week 1 全部闭环）
- Day 1：工程骨架 + /health 端点 + TDD + AGENTS.md
- Day 2：uv.lock 修复 + pre-commit hooks + GitHub Actions CI
- Day 3：攻防演练验证双重防线
- Day 4：前端骨架 Vite 8 + React 19.2 + AntD 6 + Git 接入 + SSH 双客户端冲突修复
- Day 6：SECRETS.md 工具级隔离 + fnm→mise 迁移 + Node 20→22 升级 + pnpm/action-setup v4→v6 + CI warning 清零
- Day 5：后端 /api 前缀规约 + 前端 Hello World + /api/health 三态联调 + AGENTS.md 路由规约 + CI Run #14 全绿

### Next Steps（Week 2-5 时间表）
| 时间 | 任务 | 预计工时 |
|---|---|---|
| Week 2（6/2-6/13） | 用户认证体系（FastAPI Users）+ 多租户数据模型 + RBAC 实现 | 80 小时 |
| Week 4-5 | 重新评估 Pro Components v3 是否转正稳定版 | 2 小时 |

### 技术栈备忘（最新，Day 5 后）
- 后端：FastAPI + SQLAlchemy 2.0 + Pydantic v2 + uv（Python 3.12）；所有路由统一 /api 前缀
- 前端：Node 22.22.3（mise 管理，Active LTS）+ React 19.2 + Vite 8 + TypeScript 6 + Ant Design v6（antd 6.4.3 + icons 6.2.3）+ react-router-dom v7
- Pro Components：延后到 Week 4-5
- 数据库：SQLite（dev）/ PostgreSQL 13+（prod）
- 工具链：ruff + mypy + pytest + ESLint 10 Flat Config + Prettier 3.8 + pre-commit + GitHub Actions + TruffleHog
- 包管理：uv（Python）/ pnpm 10.33.0（Node）
- 运行时管理器：mise 2026.5.15（scoop 安装，替代 fnm）
- Commit 规范：Conventional Commits（英文）
- 分支命名：feature/AC1.1-xxx、fix/xxx
- 测试覆盖率目标：整体 ≥80%，核心安全模块 ≥95%

### CI 配置备忘（最新）
- node-version: '22'
- pnpm/action-setup: @v6（Node.js 24 runtime，无 deprecation warning）
- 3 个 job：lint-and-test / Frontend Lint & Typecheck / Secret Scan (TruffleHog)
- mise 中 Node 20.20.2 保留备用

### 环境关键配置（Windows 用户必读）
- git config --global core.sshCommand 'C:/Windows/System32/OpenSSH/ssh.exe'（永久固化）
- ssh-agent 服务：Set-Service -Name ssh-agent -StartupType Automatic（需管理员 PowerShell）
- mise shims 路径已加入 User PATH：%USERPROFILE%\AppData\Local\mise\shims
- PowerShell profile 路径：D:\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
- profile 内容：mise activate pwsh | Out-String | Invoke-Expression
- pnpm 命令注意：版本号必须用单引号 'pkg@^x'，装完读 package.json 验证不靠 stdout
- dev server 端口：5173 默认；启动失败后 node.exe 僵尸进程会占用导致漂移
- ops/SECRETS.md 工具级隔离：通过 .gitignore 自动排除

### 新会话开门第一步（给新会话 AI 的最高优先级指令）
1. **确认角色**：你是顾问 / 派工人，不是码农。本次任务的码农是用户本地的 Cursor / Claude Code / CodeBuddy
2. **不要求粘贴源码**：源码在本地仓库，由本地 AI IDE 读取
3. **不进 Agent Mode**：禁止调用 browser_task_tool 或任何浏览器自动化工具修改本地文件
4. **归档命名规范**：新归档文件名格式为"日期+任务主题"（如 2026-0602-auth-system.md），不再使用 Day 编号
5. **派工 commit 步骤**：每份派工提示词的 commit 前必须包含 git status --short 检查，逐一列出未提交文件给用户确认后再 commit
6. **第一份产出**：根据本归档 §8 Next Steps，确认用户今日任务范围，出对应的派工提示词
