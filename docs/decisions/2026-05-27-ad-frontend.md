# 2026-05-27-ad

## Week 1 Day 2

Q1: 
```txt
任务:在 BoxBase v1.0 项目根目录创建 frontend/ 目录,并初始化 Vite + React 18 + TypeScript 项目。

上下文:
- 项目根目录:D:\git-repo\github\box-base
- 现有结构:根目录已有 backend/ 子目录(Python/FastAPI),前端要平级创建 frontend/
- 包管理器:pnpm 10.33.0(已安装)
- 路线:轻量集成路线,不使用 Ant Design Pro 官方脚手架

执行步骤:
1. 切换到项目根目录,确认当前目录是 box-base
2. 执行:pnpm create vite frontend --template react-ts
3. cd frontend
4. pnpm install
5. 在 vite.config.ts 中将 server.port 设为 5173(默认值,显式声明),host 设为 true(允许局域网访问)
6. 执行 pnpm dev,确认终端输出 Local: http://localhost:5173

验收输出:
- frontend/package.json 内容
- frontend/vite.config.ts 内容
- pnpm dev 终端最后 5 行输出

约束:
- 不要修改 backend/ 目录任何文件
- 不要执行 git add/commit,Git 操作我会单独验收
- 如果 pnpm create vite 询问 Package name / framework / variant,自动选择 react / TypeScript(非 SWC 版本,先用基础版)

```

Q2: 
```txt

```
