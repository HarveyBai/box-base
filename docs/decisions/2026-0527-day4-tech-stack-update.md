# Day 4 前端技术栈决策更新（2026-05-27）

## 背景

Day 1 归档原计划前端使用 React 18 + Ant Design Pro。Day 4 执行 `pnpm create vite frontend --template react-ts` 时，Vite 默认模板已升级到 React 19 + Vite 8 + TypeScript 6 全新栈。

## 决策

接受新栈，不推倒重来。理由：

1. React 19.2（2025-10 发布）已在 Meta 生产环境验证，Next.js 16 / Expo 已默认支持
2. Vite 8（2026-03-12 发布）是当前主线稳定版
3. TypeScript 6（原生重写编译器）向后兼容 5.x 语法，迁移成本接近零
4. Ant Design v6 已发布，核心定位即为"更好兼容 React 19"，时机匹配
5. 锁定 React 18 等于主动选择已进入维护期的栈，16 周生命周期内将进一步落后于生态主流

## 最终锁定栈

- 框架：React 19.2 + react-dom 19.2
- 构建：Vite 8（@vitejs/plugin-react 6）
- 类型：TypeScript 6
- Lint：ESLint 10
- UI 库：antd 6 + @ant-design/icons 6（Pro Components 延后，见下方补充决策）
- 包管理：pnpm 10.33

## 受影响文档

- AGENTS.md：已同步更新前端技术栈段落
- docs/decisions/2026-0526-day2-3-archive.md 第 8 节"技术栈备忘"：已同步更新前端部分

## 后续注意

- React 19 + AntD 6 不再需要 @ant-design/v5-patch-for-react-19 补丁
- @ant-design/icons 必须和 antd 主版本对齐（都是 6），否则构建会报错

## 补充决策：Pro Components 延后（同日发现）

### 触发原因

执行 `pnpm add @ant-design/pro-components@^3` 时报错 `ERR_PNPM_NO_MATCHING_VERSION`：Pro Components v3 当前仅有 beta 版（3.1.12-0，发布于 2026-03-29），稳定版最新为 v2.8.10。

### 关键事实

1. ProComponents 官方迁移文档明示：v2 仅兼容 antd 4/5，v3 才适配 antd 6+
2. GitHub Issue #9629 记录：即使 v3 beta 装在 antd 6 项目上，`npx antd doctor` 仍报 10 个 peerDependency 失败
3. v2.8.10 发布于 2025-07-17，peer 锁定 antd ^5.x，无法与今日采用的 antd 6 共存

### 决策

Day 4 不引入 `@ant-design/pro-components`。验证页面改用原生 antd 6 组件（Layout / Typography / Button / Space / Icons）。

### 后续重新评估时间表

- Week 2-3：用户认证 + 多租户数据模型阶段，原生 antd 6 已满足前端需求
- Week 4-5：RBAC 后台管理列表阶段，重新评估 Pro Components v3 是否已转正稳定版
  - 如已转正：正常引入
  - 如仍 beta：用 antd 6 原生 Table + Form 自行封装替代品

### 教训与环境备忘

技术选型教训：

- 昨日定栈时只核实了 antd 6 的发布状态，未核实 `@ant-design/pro-components` v3 的 npm 实际发布状态。后续选型必须同时核实"主包"和"配套包"两侧。

PowerShell + pnpm 环境备忘（Day 4 实战观察）：

- 直接执行 `pnpm add antd@^6` 时，PowerShell 会因 `@` 字符或 CLIXML 包装导致 stdout 输出被吞，AI 工具误判为命令失败而反复重试。安全做法：版本号用单引号包裹，且执行后立即 `Get-Content package.json` 直接验证依赖是否真的写入，不靠命令 stdout 推断。
- `pnpm dev` 启动失败或被中断后，node.exe 后台进程可能残留，占用 5173 端口导致下次启动自动漂移到 5174/5175。Day 4 实测出现该现象。Commit 前必须执行 `Get-Process | Where-Object { $_.ProcessName -like "*node*" }` 检查，有僵尸进程则 `Stop-Process -Force` 杀掉。
- `node_modules` 内含 native 模块（如 `.node` 文件）在 dev server 运行期间被锁定，`Remove-Item -Recurse` 会失败。删除前必须先杀进程。

视觉层验收（2026-05-27 实测）：

- 浏览器访问 localhost:5175（因 5173 被僵尸进程占用自动漂移），AntD 6 + React 19 + StrictMode 渲染零 console error / zero warning，Vite HMR 握手正常。AntD 6 默认主题色 #1677ff 加载正确。结论：技术栈组合在你的 Windows 环境下完整可用。
