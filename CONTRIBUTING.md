# BoxBase 开发贡献指南

本文档面向新加入的开发者，提供从 clone 代码到提交 PR 的完整操作指引。

## 环境要求

| 工具 | 版本要求 | 说明 |
|---|---|---|
| Python | 3.12+ | 通过 uv 管理，禁止直接使用 pip |
| uv | 最新版 | Python 包管理器，[安装方法](https://docs.astral.sh/uv/getting-started/installation/) |
| Node.js | 20+ | 通过 pnpm 管理（前端搭建后启用） |
| pnpm | 最新版 | 前端包管理器 |
| Git | 2.40+ | 版本控制 |
| IDE | Cursor（主力）/ VS Code | 推荐安装 Ruff、Mypy 插件 |

## 快速开始（第一次 clone 后）

### 1. 克隆仓库

```sh
git clone git@320312396.github.com:HarveyBai/box-base.git
cd box-base
```

### 2. 安装 Python 依赖

```sh
cd backend
uv sync
```

`uv sync` 会自动：
- 根据 `pyproject.toml` 安装所有生产依赖和开发依赖
- 创建 `.venv/` 虚拟环境
- 生成 `uv.lock` 锁定依赖版本（该文件不入库，每次 `uv sync` 自动生成）

### 3. 安装前端依赖

> TODO：Week 8+ 前端搭建后补充。届时执行 `cd frontend && pnpm install`。

### 4. 启动开发服务器

```sh
# 后端（端口 8000）
cd backend && uv run uvicorn boxbase.main:app --reload
```

启动成功后访问：
- `http://localhost:8000/health` → JSON 健康检查响应
- `http://localhost:8000/docs` → 自动生成的 Swagger API 文档

### 5. 验证环境

执行以下三条命令，确认全部通过：

```sh
cd backend
uv run pytest -v          # 应显示 1 passed
uv run ruff check .       # 应显示 All checks passed!
uv run mypy boxbase/      # 应显示 Success: no issues found
```

## 日常开发命令

### 后端

| 操作 | 命令 | 说明 |
|---|---|---|
| 启动服务 | `cd backend && uv run uvicorn boxbase.main:app --reload` | `--reload` 启用了热重载 |
| 运行测试 | `uv run pytest -v` | 使用 `pytest` + `pytest-asyncio` + `httpx` |
| 代码检查 | `uv run ruff check .` | 检查格式与 lint 规则 |
| 自动修复 | `uv run ruff check --fix .` | 自动修复可解决的问题 |
| 类型检查 | `uv run mypy boxbase/` | 严格模式：`disallow_untyped_defs` + `check_untyped_defs` |
| 添加依赖 | `uv add <package>` | 禁止使用 `pip install` |
| 添加开发依赖 | `uv add --dev <package>` | 仅用于开发/测试的依赖 |

> TODO：数据库迁移命令（`uv run alembic revision`、`uv run alembic upgrade head`）将在 Week 2 引入 Alembic 后补充。

### 前端

> TODO：Week 8 前端搭建后补充。届时将包含 `pnpm dev`、`pnpm test`、`pnpm lint` 等命令。

## 代码提交规范

本项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

| 前缀 | 用途 | 示例 |
|---|---|---|
| `feat:` | 新功能 | `feat: add user registration endpoint` |
| `fix:` | 修复 bug | `fix: resolve token refresh race condition` |
| `chore:` | 工程化/杂项 | `chore: update ruff to 0.15` |
| `docs:` | 文档变更 | `docs: add API authentication guide` |
| `test:` | 测试变更 | `test: add edge cases for health endpoint` |
| `refactor:` | 重构 | `refactor: extract permission checker interface` |
| `perf:` | 性能优化 | `perf: optimize tenant query with index` |
| `ci:` | CI/CD 变更 | `ci: add pytest to GitHub Actions` |

**重要规则**：

- Commit message 必须使用 **英文**
- 单个 commit 改动建议 **≤ 200 行**，超过时拆分
- 禁止提交密钥、密码等敏感信息到 Git
- 禁止直接 push 到 `main` 分支

### 代码风格

- Python Docstring 使用**中文 Google 风格**，必须包含参数（Args）/ 返回值（Returns）/ 异常（Raises）/ 示例（Example）段落
- TypeScript JSDoc 使用**中文**
- 行内注释（`#` / `//`）使用**中文**，解释"为什么"而非"是什么"
- 变量名、函数名、类名、文件名使用**英文**

## Pull Request 流程

### 分支命名

```
feature/AC1.1-register-user   # 功能分支，关联验收标准（AC）编号
fix/auth-token-refresh        # 修复分支
chore/update-deps             # 工程化分支
refactor/tenant-isolation     # 重构分支
```

### PR 描述模板

```markdown
## 概述
（一句话说明这个 PR 做了什么）

## 关联 AC
- AC1.x — xxx

## 变更清单
- 新增文件：...
- 修改文件：...
- 删除文件：...

## 测试
- [ ] 所有测试通过（`uv run pytest -v`）
- [ ] 代码检查通过（`uv run ruff check .`）
- [ ] 类型检查通过（`uv run mypy boxbase/`）
- [ ] 新增用例覆盖了对应 AC 的边界条件

## 截图/验证
（如有 UI 变更或 API 响应变更，贴截图或 curl 输出）
```

### Review 要求

- 每个 PR 只对应 **一个明确目标**（一个 AC 或一项重构）
- 必须至少通过 CI 流水线（测试 + lint + type check）
- 合并前需要至少一人 Review 批准
- Review 关注点：测试是否覆盖 AC、是否有安全风险、是否符合模块化设计原则

## 构建与打包

> TODO：Week 14 补充打包与部署相关内容。

## 常见问题

### Q1：Windows 终端下 uv 命令输出乱码？

**原因**：Windows 默认终端编码（如 GBK）与 uv/pytest 的 UTF-8 输出不兼容。

**解决方案**：

```powershell
# 临时设置（当前终端窗口）
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 永久设置（推荐）
# 在 PowerShell 配置文件（$PROFILE）中添加上述命令
```

或在 VS Code / Cursor 中使用内置终端，通常已默认配置为 UTF-8。

### Q2：uv sync 提示镜像 403 错误？

**原因**：部分国内镜像（如清华 TUNA）可能对 uv 的请求返回 403。

**解决方案**：在 `backend/` 目录执行时显式指定官方源：

```sh
uv add <package> --default-index https://pypi.org/simple/
```

`pyproject.toml` 中已配置 `[[tool.uv.index]]` 指向 PyPI 官方源，正常情况下 `uv sync` 会自动使用。
