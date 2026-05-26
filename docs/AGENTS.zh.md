<!-- This file is the SINGLE SOURCE OF TRUTH for all AI coding agents working on BoxBase.
     Cursor, Claude Code, GitHub Copilot, Codex, Trae, and others all read this file.
     Do NOT duplicate rules in tool-specific files; reference this file instead. -->

# BoxBase 项目 AI 工作规则

你正在协助开发 BoxBase —— 一个轻量级、模块化的 Python 多租户 SaaS 框架。

## 项目身份

- 项目名：BoxBase v1.0
- 语言：Python 3.12（后端）、TypeScript 5（前端）
- 后端技术栈：FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2
- 前端技术栈：React 18 + Ant Design Pro + Vite + Ant Design X（用于 AI 模块）
- 数据库：SQLite（开发）/ PostgreSQL 13+（生产）
- 包管理器：uv（Python）、pnpm(Node)

## 核心设计原则

1. **模块化优先**：每个功能都应能作为 `modules/` 目录下的独立模块实现
2. **多租户强制**：所有业务表必须包含 `org_id` 字段。使用 SQLAlchemy event listener 自动注入 `WHERE org_id` 过滤条件
3. **权限抽象**：所有权限检查必须通过 `PermissionChecker` 接口。业务代码绝不能直接调用 Casbin 或任何具体实现
4. **优先复用开源**：优先使用 FastAPI Users、fastapi-mail、slowapi、secure、sse-starlette、LiteLLM。如果选择自写，必须在 PR 描述中说明理由
5. **简单胜过聪明**：避免过度抽象。除非绝对必要，不使用工厂模式、依赖注入容器、抽象基类

## 编码规范

### Python
- 使用 Python 3.12 语法。**所有地方使用类型注解**
- 每个文件顶部加 `from __future__ import annotations`
- 使用 Pydantic v2 语法（model_validator、field_validator、ConfigDict）
- 使用 SQLAlchemy 2.0 语法（Mapped、mapped_column、async session）
- I/O 操作默认 async，纯计算才用 sync
- 用 ruff 格式化，行宽 120
- Docstring 使用**中文 Google 风格**，所有公开函数/类必须有，必须包含参数（Args）/ 返回值（Returns）/ 异常（Raises）/ 示例（Example）段落
- 行内注释（`# ...`）使用 **中文**，解释"为什么"而非"是什么"

### TypeScript
- 严格模式开启。除非有明确注释说明，否则不允许 `any`
- 只用函数式组件，不用 class 组件
- 全局状态用 Zustand，服务端状态用 React Query
- 用 prettier 格式化，行宽 120
- JSDoc 注释使用 **英文**，行内注释使用 **中文**

## 测试驱动开发（TDD）—— 强制要求

实现任何功能时：
1. **必须先写测试，再写实现**
2. **先把测试展示给我，等我批准后再写实现**
3. 测试必须对应 PRD 中的具体验收标准（AC）编号
4. 每个测试文件的 docstring 中必须标注对应的 AC ID
5. 后端测试用 pytest + pytest-asyncio + httpx
6. 端到端测试用 Playwright
7. 覆盖率目标：**整体 ≥ 80%，认证/权限/多租户/加密代码 ≥ 95%​**
8. **覆盖率不是唯一指标——测试是否真实覆盖 AC、是否检验了边界条件和异常路径，比覆盖率数字更重要**
9. 禁止"虚假通过"测试（如 `assert True`、`assert response is not None` 这类无效断言）

## 文件组织

- backend/boxbase/core/ —— 核心抽象（接口、基类）
- backend/boxbase/auth/ —— 认证（FastAPI Users 集成）
- backend/boxbase/tenant/ —— 多租户（组织、成员、隔离）
- backend/boxbase/rbac/ —— 基于角色的权限控制
- backend/boxbase/modules/ —— 模块加载器与生命周期
- backend/boxbase/audit/ —— 审计日志
- backend/tests/ —— 后端所有测试，目录结构镜像源码
- frontend/src/ —— React 管理后台
- frontend/tests/ —— React 管理后台测试集
- modules/ —— 用户开发的示例模块
- docs/ —— Sphinx 文档源（中文）
- scripts/ —— 跨平台项目脚本（用 Python 编写，避免 bash/PowerShell 差异）

## 命令规范（避免命令混乱）

- 安装 Python 依赖：**只用 `uv add <pkg>`​**，禁止 `pip install`
- 运行 Python 命令：**只用 `uv run <cmd>`​**（如 `uv run pytest`、`uv run alembic`）
- 安装前端依赖：**只用 `pnpm add <pkg>`​**，禁止 `npm install` 或 `yarn add`
- 项目级任务：通过 `scripts/` 下的 Python 脚本或 `Makefile`/`make.ps1` 触发，禁止散落的 shell 命令

## Git 与协作规范

- Commit 遵循 [Conventional Commits](https://www.conventionalcommits.org/)：`feat:`、`fix:`、`chore:`、`docs:`、`test:`、`refactor:`、`perf:`、`ci:`
- Commit message 使用 **英文**（便于自动化 changelog 与国际协作）
- 单个 commit 改动建议 ≤ 200 行；超过时应拆分
- 每个 PR 对应一个明确目标（一个 AC 或一项重构）
- 分支命名：`feature/AC1.1-register-user`、`fix/auth-token-refresh`、`chore/update-deps`
- 禁止直接 push 到 main 分支，必须通过 PR

## 沟通规则

1. **写任何非平凡代码前，先提出方案**：列出要创建/修改的文件、关键决策、潜在风险，等我批准
2. **改动以 diff 形式展示给我审阅**，不要自动应用大块修改
3. **实现功能时引用 AC 编号**（例如"这是实现 AC1.5"）
4. **使用第三方 API 时引用官方文档 URL**，防止 AI 编造
5. **不确定时直接说"我不确定"​**，不要猜，建议进一步调研
6. **绝不编造 API**。如果某个方法不存在，明确告诉我
7. **修改文件前，先完整读取该文件**；跨文件修改前，先用 Grep 搜索所有引用点
8. **上下文不足时停下来问我**，而不是基于猜测继续

## 禁止行为

### 工程纪律
- 禁止未告知就安装依赖
- 禁止未明确指示就修改 CI/CD 配置
- 禁止编写没有测试的生产代码
- 禁止用 `any`、`# type: ignore`、`noqa` 回避类型/lint 错误，必须修复根因
- 禁止增加顶层依赖前不说明"为什么不能用现有依赖"
- 禁止在文档化目录结构之外创建文件

### 安全红线（违反即拒绝合并）
- 禁止把密钥（API key、JWT secret、DB 密码）硬编码到代码或提交到 git
- 禁止使用 MD5/SHA1/明文处理密码，必须用 argon2 或 bcrypt
- 禁止 SQL 字符串拼接，必须用参数化查询或 ORM
- 禁止用 `print()` 输出敏感信息（密码、token、邮箱、PII）
- 禁止"为方便测试"跳过权限检查或鉴权中间件
- 禁止在前端代码中保存任何敏感信息

## 语言策略

| 内容类型 | 语言 | 理由 |
|---|---|---|
| 与我对话 | 中文 | 我的母语 |
| AI 思考过程 | 任意（建议英文以提升推理质量） | 模型英文推理质量略高 |
| 变量名、函数名、类名、文件名 | 英文 | 编程惯例 |
| 行内注释（# / //） | 中文 | 解释"为什么这么做" |
| Docstring / JSDoc | 中文（Google 风格） | 项目负责人以中文为主要工作语言 |
| Commit message | 英文（Conventional Commits） | 自动化 changelog 与国际协作 |
| docs/ 项目文档 | 中文 | 主要给中文团队读 |
| 后端日志、异常 message | 英文 | 运维工具兼容性 |
| API 错误返回（给前端） | 英文 code + i18n key | 前端按用户语言渲染 |
| 前端 UI 文案 | 中文（默认）+ i18n 结构 | 主要用户群体 |

## 中文沟通约定

1. 提问时先用中文给出**结论**，再展开技术细节
2. 首次出现的英文术语用括号标注中文（例如 "middleware（中间件）"）
3. 拒绝我的不合理请求时**直接说"不建议这么做，原因是……"​**
4. 给多个方案时，明确标出"我推荐方案 X，理由是……"
5. 任何代码改动前，先用 1-2 段中文说明"为什么改、改什么、有什么风险"

## 当前阶段

我们在 **Week 1：工程化底座搭建**。当前阶段只关注：
- 项目骨架（pyproject.toml、package.json）
- 代码检查、格式化、类型检查（ruff、mypy、prettier、eslint）
- CI/CD 流水线（GitHub Actions）
- 测试框架配置（pytest、Playwright）
- pre-commit hooks
- 一个 Hello World 接口与一个 Hello World 测试

**在我明确说"开始 Week 2"之前，绝不开始实现业务功能（auth、tenant、RBAC、modules、audit）​**。

## 不确定时

问我。我是产品负责人。**与其写 100 行错代码，不如问 10 个澄清问题**。
