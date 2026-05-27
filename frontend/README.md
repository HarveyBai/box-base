# BoxBase Frontend

## 1. Project Overview

BoxBase v1.0 前端骨架，基于轻量集成路线搭建。技术栈：React 19.2 + Vite 8 + TypeScript 6 + Ant Design 6.4.3 + react-router-dom 7.x。未引入 Ant Design Pro（延后到 Week 4-5 重评估），当前用原生 Ant Design v6 满足所有需求。

## 2. Prerequisites

- **Node.js 20 LTS+** — 推荐 20.x 或 22.x LTS 版本
- **pnpm 10.33+** — 推荐 `corepack enable` 启用，或 `npm i -g pnpm`
- **Git** — Windows 用户参考章节 11 SSH 配置

## 3. Initial Setup

```bash
git clone git@github.com:HarveyBai/box-base.git
cd frontend
pnpm install
```

必须使用 pnpm 安装依赖。npm / yarn 的 lockfile 不通用，会破坏依赖一致性。

## 4. Development

```bash
pnpm dev
```

启动 Vite dev server，默认端口 **5173**。浏览器访问 http://localhost:5173。

端口被占用时，参考章节 11 Troubleshooting。

## 5. Code Quality

| 命令 | 说明 | 触发时机 |
|---|---|---|
| `pnpm exec tsc --noEmit` | TypeScript 类型检查 | CI / 手动 |
| `pnpm exec eslint .` | ESLint 代码检查 | pre-commit / CI / 手动 |
| `pnpm exec prettier --check .` | Prettier 格式检查 | pre-commit / CI / 手动 |
| `pnpm format` | Prettier 自动格式化 | 手动（基线对齐） |
| `pnpm format:check` | 同 prettier --check | 手动 |

## 6. Project Structure

```
frontend/src/
├── main.tsx               # 应用入口，RouterProvider 包裹路由
├── App.tsx                 # 全局 Layout 外壳（ConfigProvider + Header + <Outlet />）
├── router.tsx              # createBrowserRouter 路由表
├── pages/
│   ├── HomePage.tsx        # 首页（/），Boot Check 内容 + 路由验证
│   └── NotFoundPage.tsx    # 404 页面（*），AntD Result 组件
├── index.css               # 全局样式
└── vite-env.d.ts           # Vite 类型声明
```

## 7. Routing (react-router-dom v7)

路由表定义在 `src/router.tsx`，使用 `createBrowserRouter`。

**加新页面三步：**
1. 建 `src/pages/XxxPage.tsx`
2. 在 `router.tsx` 中注册 path
3. 浏览器验证

`App.tsx` 是全局 Layout 外壳，`<Outlet />` 渲染当前路由内容。

## 8. Path Alias

`@/` → `src/`，配置在两处：

- **vite.config.ts**：`resolve.alias`
- **tsconfig.app.json**：`baseUrl` + `paths`

加新别名必须两处同步修改，缺一不可。

## 9. Commit Workflow

### pre-commit hooks（本地）

- **backend**：ruff check / ruff format check / mypy
- **frontend**：eslint / prettier --check

### GitHub Actions（云端）

- `lint-and-test`：backend 检查（ruff + mypy + pytest）
- `frontend-quality`：前端检查（tsc + eslint + prettier --check）
- 两个 job **并行执行**，互不依赖

### 规范

- Conventional Commits，英文
- **严禁** `git commit --no-verify` 跳 hook
- **严禁** `git push --force`

## 10. PowerShell Gotchas（Windows 用户必读）

### pnpm 装包

版本号必须用单引号包裹，避开 PowerShell `@` 字符解析 + CLIXML 吞 stdout：

```powershell
pnpm add 'antd@^6'         # 正确
pnpm add antd@^6           # 错误，输出被吞
```

装完用 `Get-Content package.json` 验证版本号，不要依赖 pnpm 命令的 stdout。

### 僵尸进程清理

```powershell
Get-Process | Where { $_.ProcessName -like "*node*" } | Stop-Process -Force
```

## 11. Troubleshooting

### dev server 端口漂到 5174/5175

node 僵尸进程占用 5173。按章节 10 的 PowerShell 命令清理僵尸进程后重启。

### git push 要求 passphrase

Windows 双 SSH 客户端 Agent 不通。永久修复：

```bash
git config --global core.sshCommand 'C:/Windows/System32/OpenSSH/ssh.exe'
```

### ssh-agent 服务未启动

以**管理员**身份运行 PowerShell：

```powershell
Set-Service -Name ssh-agent -StartupType Automatic
Start-Service ssh-agent
```

### Pro Components 装不上

v3 仅 beta，v2 锁死 antd 5 与 antd 6 peer 冲突。当前用原生 antd 6 满足需求，Week 4-5 重评估。

## 12. References

- [../docs/decisions/2026-0527-day4-tech-stack-update.md](../docs/decisions/2026-0527-day4-tech-stack-update.md) — 技术栈选型完整决策
- [../AGENTS.md](../AGENTS.md) — AI 工具协作规则
- [Vite 官方文档](https://vitejs.dev/)
- [Ant Design 官方文档](https://ant.design/)
- [react-router-dom 官方文档](https://reactrouter.com/)
