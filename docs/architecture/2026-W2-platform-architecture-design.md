# BoxBase v1.0 平台架构设计规范

- **文档状态**：规范稿（持续演进，每次架构变更在此更新）
- **创建日期**：2026-05-31
- **基线 commit**：e09ab0d（Week 2 Day 2 收官，21/21 绿，全局覆盖率 96% / security 100%）
- **产品经理**：baihw（GitHub: HarveyBai） / **顾问**：会话内 AI
- **远端**：git@github.com:HarveyBai/box-base.git
- **关联文档**：
  - `docs/architecture/2026-W2-auth-tenant-rbac-design.md`（认证/多租户/RBAC 详细设计）
  - `docs/decisions/2026-0530-week2-day2-slice1-9-complete.md`（Week 2 Day 2 归档）

> 本文档是 BoxBase 平台架构的单一真相源。所有模块开发、扩展点实现、架构演进均以本文档为准。变更须先更新本文档，再出派工。

---

## 章节 1：整体架构原则

### 1.1 设计哲学

BoxBase 是轻量级、模块化的 Python 多租户 SaaS 框架。架构设计遵循以下核心原则：

1. **模块自治**：每个业务模块是独立的垂直切片，拥有自己的 models / routers / services / schemas，模块内部结构对平台透明。
2. **核心与业务分离**：平台基础设施（认证、依赖注入、数据库、配置）集中在 `core/`，业务逻辑归属各 `zones/` 模块，不得反向依赖。
3. **单向依赖**：扩展模块可依赖 `core/` 和 `zones/admin/`（基础管理数据），禁止模块间横向依赖。
4. **统一规则，自由实现**：平台对模块只约定对外接口规则（`router.py` / `service.py` 入口），不限制模块内部实现细节。
5. **可测试优先**：service 层独立于 router 层，业务逻辑必须可单独单测，不依赖 HTTP 上下文。

### 1.2 技术栈（锁定版本）

| 层 | 技术 | 版本 |
|---|---|---|
| 后端框架 | FastAPI | 当前 uv 锁定版 |
| ORM | SQLAlchemy | 2.0 async |
| 数据校验 | Pydantic | v2 |
| 包管理 | uv | Python 3.12 |
| 迁移 | Alembic | 1.18.4 |
| 异步驱动 | aiosqlite(dev) / asyncpg(prod) | 0.22.1 / 0.31.0 |
| 配置管理 | pydantic-settings | 2.14.1 |
| 哈希 | pwdlib[argon2] | 0.3.0 |
| JWT | PyJWT | 2.13.0 |
| 覆盖率 | pytest-cov / coverage | 7.1.0 / 7.14.1 |
| 前端框架 | React + Vite + TypeScript | 19.2 / 8 / 6 |
| UI 组件库 | Ant Design | 6.4.3 |
| 路由 | react-router-dom | v7 |
| 前端包管理 | pnpm | 10.33 |
| 运行时管理 | mise | 2026.5.15，Node 22.22.3 |
| 代码质量 | ruff + mypy + ESLint 10 + Prettier 3.8 | — |
| CI | GitHub Actions + TruffleHog | — |

---

## 章节 2：目录结构规范

### 2.1 完整目录结构

```
box-base/
├── backend/
│   ├── boxbase/
│   │   ├── core/                    ← 平台基础设施，全局共享
│   │   │   ├── __init__.py
│   │   │   ├── base.py              ← AuditMixin + DeclarativeBase
│   │   │   ├── config.py            ← pydantic-settings 配置
│   │   │   ├── database.py          ← async engine + session factory
│   │   │   ├── dependencies.py      ← RequestContext / get_db / tenant filter
│   │   │   ├── exceptions.py        ← ErrorResponse + 全局异常类
│   │   │   ├── security.py          ← hash / JWT / get_current_user
│   │   │   └── router.py            ← 平台路由总入口（聚合各模块 router.py）
│   │   ├── zones/                   ← 业务模块目录
│   │   │   ├── admin/               ← 平台基础管理模块（内置，不可删除）
│   │   │   │   ├── models/          ← 8 张基础表
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user.py
│   │   │   │   │   ├── tenant.py
│   │   │   │   │   ├── membership.py
│   │   │   │   │   ├── role.py
│   │   │   │   │   ├── permission.py
│   │   │   │   │   ├── membership_role.py
│   │   │   │   │   ├── role_permission.py
│   │   │   │   │   └── refresh_token.py
│   │   │   │   ├── routers/         ← 端点多，拆子目录
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py      ← /api/auth/*
│   │   │   │   │   ├── users.py     ← /api/users/*
│   │   │   │   │   ├── roles.py     ← /api/roles/*, /api/permissions/*
│   │   │   │   │   └── admin.py     ← /api/admin/*
│   │   │   │   ├── services/        ← 业务逻辑，拆子目录
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   └── roles.py
│   │   │   │   ├── router.py        ← 聚合 routers/，对外唯一入口
│   │   │   │   ├── schemas.py       ← 所有 Pydantic request/response schema
│   │   │   │   └── service.py       ← 聚合 services/，对外唯一入口
│   │   │   └── demo/                ← 示例扩展模块（开发参考）
│   │   │       ├── models/
│   │   │       ├── router.py        ← 端点少时直接单文件
│   │   │       ├── schemas.py
│   │   │       └── service.py
│   │   └── main.py                  ← FastAPI app 初始化，极简
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_security.py
│   │   └── zones/
│   │       ├── admin/
│   │       │   ├── test_auth.py
│   │       │   ├── test_users.py
│   │       │   └── test_roles.py
│   │       └── demo/
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── .env                         ← 演示配置，入库
├── frontend/
│   └── ...（Week 1 产物，Week 4-5 扩展）
├── docs/
│   ├── architecture/                ← 架构设计文档（本文件所在目录）
│   └── decisions/                   ← 会话归档
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── AGENTS.md
└── ops/SECRETS.md
```

### 2.2 目录职责边界

| 目录 | 职责 | 可被谁依赖 |
|---|---|---|
| `core/` | 平台基础设施，无业务逻辑 | 所有模块 |
| `zones/admin/` | 平台基础管理业务（用户/租户/认证/RBAC） | 其他扩展模块（单向） |
| `zones/demo/` | 扩展模块开发示例 | 不被其他模块依赖 |
| `zones/<自定义>/` | 用户扩展业务模块 | 不被其他模块依赖 |

**禁止**：扩展模块之间横向 import；任何模块反向 import `main.py`；`core/` import 任何 zone 模块。

---

## 章节 3：模块规范（Zone Contract）

### 3.1 模块必须遵守的规则

每个 zone 模块（无论内置还是用户扩展）必须满足以下约定，平台以此为接口契约：

**规则 1：对外暴露唯一路由入口 `router.py`​**
- `core/router.py` 只 include 各模块的 `router.py`，不感知模块内部结构
- `router.py` 必须导出名为 `router` 的 `APIRouter` 实例

**规则 2：对外暴露唯一 service 入口 `service.py`​**
- 模块内部可拆 `services/` 子目录，但对外统一由 `service.py` 聚合导出
- 其他模块需要调用本模块业务逻辑时，只从 `service.py` import

**规则 3：models 归模块自身**
- 每个模块的数据表定义放在模块自身的 `models/` 目录下
- 所有 model 必须继承 `core.base.AuditMixin`
- `models/__init__.py` 统一导出本模块所有 model（供 Alembic autogenerate 识别）

**规则 4：端点路径前缀**
- 所有端点统一挂 `/api` 前缀（由 `core/router.py` 统一注入，模块内不重复声明）
- admin 模块路径规范：`/api/auth/*` / `/api/users/*` / `/api/roles/*` / `/api/permissions/*` / `/api/admin/*`
- 扩展模块路径建议：`/api/<module-slug>/*`

**规则 5：内部拆分自由，规模门槛**
- 端点 ≤8 个：`router.py` 单文件即可
- 端点 >8 个：拆 `routers/` 子目录，`router.py` 负责聚合
- service 函数 ≤10 个：`service.py` 单文件即可
- service 函数 >10 个：拆 `services/` 子目录，`service.py` 负责聚合

### 3.2 平台路由注册方式

```python
# core/router.py
from fastapi import APIRouter
from boxbase.zones.admin.router import router as admin_router
from boxbase.zones.demo.router import router as demo_router
# 新增模块只需在此追加一行

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(demo_router)
```

```python
# main.py
from fastapi import FastAPI
from boxbase.core.router import api_router

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.include_router(api_router, prefix="/api")
```

### 3.3 模块内部 router 聚合示例（admin zone）

```python
# zones/admin/router.py
from fastapi import APIRouter
from boxbase.zones.admin.routers.auth import router as auth_router
from boxbase.zones.admin.routers.users import router as users_router
from boxbase.zones.admin.routers.roles import router as roles_router
from boxbase.zones.admin.routers.admin import router as admin_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(roles_router, tags=["Roles"])
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
```

---

## 章节 4：核心基础设施规范（core/）

### 4.1 AuditMixin（core/base.py）

所有业务表必须继承 `AuditMixin`，提供统一审计字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | `Uuid` | 主键，默认 uuid4 |
| `created_at` | `DateTime` | 创建时间，默认 now() |
| `updated_at` | `DateTime` | 更新时间，onupdate now() |
| `created_by` | `Uuid` nullable | 创建人 user_id，service 层写入 |
| `updated_by` | `Uuid` nullable | 更新人 user_id，service 层写入 |
| `deleted_at` | `DateTime` nullable | 软删除时间戳，null = 未删除 |

### 4.2 ErrorResponse（core/exceptions.py）

所有端点错误响应统一使用 `ErrorResponse` schema：

```python
class ErrorResponse(BaseModel):
    code: str      # 机器可读错误码，如 "AUTH_INVALID_TOKEN"
    message: str   # 人类可读错误描述
```

HTTP 状态码通过 `HTTPException` 的 `status_code` 传递，`detail` 字段使用 `ErrorResponse` 的 dict 形式。

### 4.3 依赖注入链（core/dependencies.py）

```
get_db → AsyncSession
RequestContext(user_id, active_tenant_id, is_superadmin)
apply_tenant_filter(query, tenant_id) → with_loader_criteria
apply_soft_delete_filter(query) → with_loader_criteria(deleted_at IS NULL)
get_current_user → RequestContext（含超管 short-circuit + active membership 校验）
```

### 4.4 配置项（core/config.py）

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `database_url` | sqlite+aiosqlite:///./boxbase.db | 数据库连接串 |
| `secret_key` | — | JWT 签名密钥，必须在 .env 设置 |
| `superadmin_username` | superadmin | 超管用户名，配置注入 |
| `access_token_expire_minutes` | 30 | access token 有效期 |
| `refresh_token_expire_days` | 7 | refresh token 有效期 |

### 4.5 安全模块（core/security.py）

| 函数 | 说明 |
|---|---|
| `hash_password(plain)` | argon2 哈希 |
| `verify_password(plain, hashed)` | 验证密码 |
| `create_access_token(user_id, active_tenant_id, ...)` | 签发 access token（HS256，30min）|
| `create_refresh_token(jti, ...)` | 签发 refresh token（HS256，7d）|
| `decode_token(token)` | 解码验签，过期/篡改抛异常 |
| `get_current_user(token, db)` | 超管 short-circuit → active membership 校验 → 返回 RequestContext |

---

## 章节 5：数据模型规范

### 5.1 多租户隔离策略

- **隔离方式**：Row-level + `tenant_id`（共享库共享表）
- **ORM 强制过滤**：`apply_tenant_filter` 通过 `with_loader_criteria` 注入，所有查询自动附加 `tenant_id = active_tenant_id`
- **软删除过滤**：`apply_soft_delete_filter` 自动附加 `deleted_at IS NULL`
- **PG RLS**：预留 hook，v1.0 不启用

### 5.2 admin 模块基础表（zones/admin/models/）

详见 `docs/architecture/2026-W2-auth-tenant-rbac-design.md` 章节 3。

表清单：`User` / `Tenant` / `Membership` / `Role` / `Permission` / `MembershipRole` / `RolePermission` / `RefreshToken`

关键约束：
- `User`：username / email / phone 各自单列全局唯一索引；phone nullable
- `Tenant`：slug 全局唯一索引；`is_system=true` 标记系统/默认租户（同一条）
- `Membership`：`UniqueConstraint(tenant_id, user_id)`；`is_default` 应用层保证每用户至多一条 active
- `Role` / `Permission`：tenant-scoped，`UniqueConstraint(tenant_id, name/code)`
- `RefreshToken`：jti 明文 UUID 唯一索引；status active/revoked

### 5.3 扩展模块 model 规范

- 必须继承 `core.base.AuditMixin`
- 业务表必须带 `tenant_id`（FK → Tenant.id，NOT NULL）走 row-level 隔离
- `models/__init__.py` 必须导出所有 model，确保 Alembic autogenerate 可识别
- 迁移文件由 Alembic autogenerate 生成，禁止手写迁移逻辑

---

## 章节 6：认证与权限规范

> 详细时序图见 `docs/architecture/2026-W2-auth-tenant-rbac-design.md` 章节 4。

### 6.1 认证流程摘要

- **注册**：全局用户 → 默认加入系统租户 → 强制赋 member 角色 → 不自动登录
- **登录**：定活跃租户（指定 > is_default > 唯一）→ 签发 access（30min）+ refresh（7d）→ refresh 落库
- **refresh**：验签 → 查 jti active → 旧 jti revoked + 新 refresh + 新 access（rotation）
- **logout**：当前 jti → revoked
- **switch-tenant**：校验目标 membership active → 重签 token

### 6.2 权限校验链

```
Bearer token → decode_token → 超管 short-circuit（is_superadmin=True 全通）
→ 校验 active_tenant_id 有 active membership（防伪造 token）
→ require_permission("resource:action")
→ membership → role → permission（tenant-scoped）
→ 放行 or 403
```

### 6.3 RBAC 规范

- **粒度**：`resource:action` 字符串，如 `user:read` / `role:assign`
- **seed 固定权限集**：`user:read` / `user:write` / `role:read` / `role:write` / `role:assign`
- **seed 默认角色**：`owner` / `admin` / `member`
- **三层访问控制**：① ORM 租户隔离 ② RBAC 角色权限 ③ service 层对象级所有权
- **超管**：配置注入 username，short-circuit 绕过所有 RBAC，`/api/admin/*` 专属

---

## 章节 7：API 规范

### 7.1 路径规范

- 所有端点统一 `/api` 前缀
- admin 模块：`/api/auth/*` / `/api/users/*` / `/api/roles/*` / `/api/permissions/*` / `/api/admin/*`
- 扩展模块：`/api/<module-slug>/*`
- OpenAPI 文档：`/api/docs` / `/api/redoc` / `/api/openapi.json`

### 7.2 响应规范

- 成功响应：标准 HTTP 状态码 + Pydantic response model
- 错误响应：`HTTPException(status_code=xxx, detail=ErrorResponse(...).dict())`
- 错误码命名规范：`<DOMAIN>_<ERROR>`，全大写下划线，如 `AUTH_INVALID_TOKEN` / `USER_NOT_FOUND` / `PERMISSION_DENIED`

### 7.3 端点清单（admin 模块，Week 2 Day 3 交付）

| 路径 | 方法 | 权限 | 优先级 |
|---|---|---|---|
| /api/auth/register | POST | 公开 | P0 |
| /api/auth/login | POST | 公开 | P0 |
| /api/auth/refresh | POST | 有效 refresh | P0 |
| /api/auth/logout | POST | self | P0 |
| /api/auth/switch-tenant | POST | self + 目标 membership | P2 |
| /api/auth/tenants | GET | self | P1 |
| /api/users/me | GET | self | P0 |
| /api/users | GET | user:read | P1 |
| /api/users | POST | user:write | P1 |
| /api/memberships/{id} | PATCH | user:write | P1 |
| /api/memberships/{id} | DELETE | user:write | P2 |
| /api/roles | GET | role:read | P1 |
| /api/roles | POST | role:write | P1 |
| /api/roles/{id}/permissions | PUT | role:assign | P1 |
| /api/permissions | GET | role:read | P2 |
| /api/admin/tenants | GET | superadmin | P1 |
| /api/admin/users | GET | superadmin | P2 |

---

## 章节 8：测试规范

### 8.1 覆盖率门禁（CI 强制）

| 范围 | 门禁 | 当前实际 |
|---|---|---|
| 全局 | ≥80% | 96% |
| `boxbase.core.security` | ≥95% | 100% |

- pytest-cov 路径必须用 Python 模块路径（`--cov=boxbase.core.security`），不能用文件系统路径
- `tools/` 目录 omit 出覆盖率统计

### 8.2 测试分层

- **单元测试**：service 层函数独立测试，不依赖 HTTP；security 模块 hash/JWT/rotation 全路径
- **集成测试**：各端点 happy path + 401/403；超管/普通用户两分支
- **安全场景测试**：跨租户访问被挡；token 篡改必败；logout/rotation 后旧 refresh 失效；全局唯一冲突被拒

### 8.3 测试目录规范

```
tests/
  conftest.py          ← 全局 fixture（db_session 等）
  test_security.py     ← core/security.py 单元测试
  zones/
    admin/
      test_auth.py
      test_users.py
      test_roles.py
    demo/
      test_demo.py
```

---

## 章节 9：工程化规范

### 9.1 迁移规范

- Alembic 单目录 `backend/alembic/`，SQLite/PG 通过 config 切换 URL
- 迁移文件由 autogenerate 生成，禁止手写迁移逻辑（除空 baseline）
- `script.py.mako` 模板必须包含 `op` / `sa` import 块
- `alembic.ini` 注释必须用 ASCII（Windows encoding="locale" 会 GBK 解码失败）
- 每次新增模块 model 后必须生成对应迁移文件并验证 upgrade/downgrade 往返

### 9.2 代码质量规范

- commit 前必须通过 pre-commit 三关：ruff check / ruff format / mypy
- ruff 负责 import 排序和格式化，不得手动跳过
- 禁止 `--no-verify` / `--force push` / 未经确认的 `prettier --write`

### 9.3 版本管理规范

- 依赖版本变更必须先联网核实并报备，锁定实际字符串
- 带日期文件名以 `current-time` 为准，不得凭直觉顺延
- 归档为滚动替换式：合并历史 + 本次，老内容压缩成结论/纪律

---

## 章节 10：扩展模块开发指南

### 10.1 新建扩展模块步骤

1. 在 `boxbase/zones/` 下新建模块目录，如 `zones/billing/`
2. 按模块规范（章节 3.1）创建必要文件：`models/` / `router.py` / `schemas.py` / `service.py`
3. 所有 model 继承 `core.base.AuditMixin`，业务表带 `tenant_id`
4. `models/__init__.py` 导出所有 model
5. 运行 `alembic revision --autogenerate -m "feat: add billing models"` 生成迁移
6. 验证 `alembic upgrade head` 和 `alembic downgrade -1` 往返
7. 在 `core/router.py` 追加一行 include 新模块 router
8. 为新模块编写单元测试和集成测试，确保全局覆盖率不低于 80%

### 10.2 demo 模块作用

`zones/demo/` 是官方示例模块，展示最小可用扩展模块的完整实现，包括：
- 带 `tenant_id` 的业务表 model
- 带权限校验的 CRUD 端点
- 对应的 service 层和 schemas
- 对应的测试用例

新开发者参考 demo 模块即可快速上手扩展开发。

---

## 变更记录

| 日期 | 版本 | 变更内容 | 关联会话 |
|---|---|---|---|
| 2026-05-31 | v1.0 | 初版，确立 core/ + zones/ 模块化架构规范 | Week 2 Day 3 开工前 |

