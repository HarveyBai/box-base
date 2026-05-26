# 2026-05-26-day1-decisions

## Week 1 Day 1

Q1: 
```txt
我们现在开始 Week 1 Day 1 的工作：初始化 BoxBase 后端 Python 项目骨架。

按照 AGENTS.md 第 91 条"先提案后实施"的规则，请你先不要写任何代码，先给我一份完整的实施计划，包括：

1. 你打算执行哪些命令（按顺序列出）
2. 你打算创建/修改哪些文件
3. 每个文件的核心内容大纲（不需要完整代码，只要关键配置项和决策）
4. 选用的依赖列表及版本（从 AGENTS.md 的"项目身份"和"优先复用开源"原则出发）
5. 潜在风险或需要我决策的点

具体要求：
- 后端目录是 backend/
- 用 uv 管理依赖，不要用 pip
- 包名：boxbase
- Python 版本要求：>=3.12
- 这一步只搭骨架，不实现任何业务功能
- 暂不需要数据库、不需要 FastAPI Users、不需要任何业务依赖
- 只需要：FastAPI 基础 + 一个返回 {"status": "ok"} 的 /health 端点 + 项目元信息

最后告诉我：你预计这一步会安装多少个 Python 依赖？哪些是必需，哪些是可以省的？

注意：在我批准之前，禁止执行任何修改文件或安装依赖的操作。
```

Q2: 
```txt
计划批准。请按以下补充指示执行：

【决策点回复】
1. AC ID 编号：使用 `AC0.1-health-endpoint`。后续 Week 1 工程化阶段全部用 AC0.x 前缀（区分于 Week 2+ 业务的 AC1.x 等）。test_health.py 的 docstring 必须明确写 "AC ID: AC0.1-health-endpoint"。
2. mypy：采纳你的渐进式方案（disallow_untyped_defs + check_untyped_defs），先不开 strict。
3. ruff 配置：放 pyproject.toml，不要单独 ruff.toml。
4. pre-commit：今天 Day 1 不配，留给 Day 2。
5. .gitignore：仓库根目录已经有 .gitignore，backend/ 下不需要再加。如果有 backend 特定的忽略项（如 .venv/、.mypy_cache/），添加到仓库根的 .gitignore 即可。

【补强 1 处】
/health 端点请按以下方式实现（不要只返回简单 dict）：
- 用 Pydantic v2 BaseModel 定义 HealthResponse 类，字段：status: Literal["ok"]、version: str、service: Literal["boxbase"]
- 端点签名：`async def health() -> HealthResponse`
- 用 FastAPI 的 response_model 参数：`@app.get("/health", response_model=HealthResponse)`
- 从 boxbase.__version__ 读取 version 字段
- 测试用例相应断言 3 个字段都正确

理由：Week 1 就把 Pydantic 响应模型纳入习惯，避免 Week 2 改 API 契约的成本，同时让 OpenAPI 文档从 Day 1 就完整。

【命令执行约定】
- 创建文件请直接用你的 write 工具，不要用 shell 命令（New-Item / touch）创建空文件再编辑。
- 创建目录用 `mkdir backend`（PowerShell 和 Bash 都支持）。
- uv 命令保持不变。
- 每完成一个文件，给我看 diff，我确认后再进行下一个。

【执行顺序约定（TDD 强制）】
先按以下 TDD 顺序进行：
Step A. 初始化项目骨架（uv init / pin / add 依赖 + pyproject.toml 配置）
Step B. 先写测试 tests/test_health.py（含 HealthResponse 字段断言）
Step C. 跑 pytest，应该失败（因为还没实现）
Step D. 给我看失败结果，确认测试逻辑无误
Step E. 我批准后再写 boxbase/main.py 和 boxbase/__init__.py
Step F. 跑 pytest，应该通过
Step G. 跑 ruff check 和 mypy，应该 0 errors
Step H. 给我最终验证报告

开始执行 Step A。
```
