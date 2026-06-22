<!-- This file is the SINGLE SOURCE OF TRUTH for all AI coding agents working on BoxBase.
     Cursor, Claude Code, GitHub Copilot, Codex, Trae, and others all read this file.
     Do NOT duplicate rules in tool-specific files; reference this file instead. -->

# BoxBase Project AI Working Rules

You are assisting in the development of BoxBase — a lightweight, modular Python framework for multi-tenant SaaS.

## Project Identity

- Project: BoxBase v1.0
- Languages: Python 3.12 (backend), TypeScript 6 (frontend)
- Backend stack: FastAPI + SQLAlchemy 2.0 (async) + Alembic + Pydantic v2 + pydantic-settings; auth via DIY thin layer (PyJWT + pwdlib[argon2]), HS256, access 30min / refresh 7d with DB-backed rotation
- Frontend stack: React 19.2 + Vite 8 + Ant Design v6 + react-router-dom v7 + Ant Design X (for the AI module). Pro Components 暂未引入，延后至 Week 4-5 重新评估，详见 docs/decisions/2026-0527-day4-tech-stack-update.md
- Database: SQLite (dev) / PostgreSQL 13+ (prod)
- Package managers: uv (Python), pnpm >=10 (Node)
- Node.js runtime managed by: mise (scoop install, replaced fnm on 2026-05-28)
- CI toolchain: actions/checkout@v6 / actions/setup-node@v6 / pnpm/action-setup@v4 / astral-sh/setup-uv@v7 / trufflesecurity/trufflehog@main
- CI: GitHub Actions, 3 job 并行（lint-and-test / frontend-quality / secret-scan）；详见 .github/workflows/ci.yml
- Known accepted warning: Node 20 deprecation（accepted until 2026-09-16 deadline；see docs/decisions/2026-0527-day6-archive.md section 5 for upgrade principle）
- Dependency upgrade principle: CI toolchain upgrades require explicit triggers (deprecation < 30d, security vulnerability, required new feature). Do NOT upgrade just for "zero warning" or "latest version". See docs/decisions/2026-0527-day6-archive.md section 5 for details.

## Shell Environment (mise migration, 2026-05-28)

- Node.js runtime is managed by **mise** (installed via scoop, replaced fnm)
- mise uses shims to make `node`/`npm`/`pnpm` available in **PowerShell**, **cmd**, and **bash**
- Migration reason: fnm only supports PowerShell; its CLIXML output caused frequent AI tool parse timeouts. mise shims eliminate this issue entirely.
- AI tools can freely use `node` and `pnpm` in PowerShell or cmd — no special workarounds needed.
- mise shims PATH: `%USERPROFILE%\AppData\Local\mise\shims` (persisted in User PATH)
- `ops/SECRETS.md` is permanently excluded via `.gitignore` — tool-enforced, no manual discipline required.

## Core Design Principles

1. **Modular First**: Every feature should be implementable as a self-contained module under `modules/`.
2. **Multi-tenancy is mandatory**: All business tables MUST have a `tenant_id` column (Row-level isolation, shared DB / shared tables). ORM enforces filtering globally via SQLAlchemy `with_loader_criteria` (tenant_id + soft-delete `deleted_at IS NULL`). PostgreSQL RLS is reserved as a second line of defense, not enabled in v1.0.
3. **Permission abstraction**: RBAC is a simplified three-table model (Role / Permission + roles attached to Membership) with `resource:action` permission strings, tenant-scoped. All permission checks go through the `require_permission` dependency. Casbin is NOT used in v1.0; do not introduce it without an explicit decision record.
4. **Open-source reuse over reinvention** (with measured DIY): Prefer mature small libraries (PyJWT, pwdlib, slowapi, secure, sse-starlette, LiteLLM, fastapi-mail) over building from scratch. Auth is an intentional exception: a thin DIY `core/security` layer (PyJWT + pwdlib) was chosen over fastapi-users / authx — see docs/architecture/2026-W2-auth-tenant-rbac-design.md §2.1.
5. **Simplicity over cleverness**: Avoid premature abstraction. No factory patterns, DI containers, or abstract base classes unless absolutely necessary.

## Coding Standards

### Python
- Python 3.12 syntax. Use type hints **everywhere**.
- Add `from __future__ import annotations` at the top of every file.
- Use Pydantic v2 syntax (`model_validator`, `field_validator`, `ConfigDict`).
- Use SQLAlchemy 2.0 syntax (`Mapped`, `mapped_column`, async session).
- Async by default for I/O. Sync only for pure computation.
- Format with ruff. Line length 120.
- Docstrings: **Chinese, Google style**. Required for all public functions/classes.
      Must include Args / Returns / Raises / Example sections in Chinese.
- Inline comments (`# ...`): **Chinese**, explaining the "why" not the "what".

### TypeScript
- Strict mode ON. No `any` without an explicit comment justifying it.
- Functional components only. No class components.
- Zustand for global state, React Query for server state.
- Format with prettier. Line length 120.
- JSDoc in **English**. Inline comments in **Chinese**.

## Test-Driven Development (TDD) — MANDATORY

For any feature implementation:
1. **Always write tests BEFORE implementation.​**
2. **Show me the tests first, wait for my approval before writing the implementation.​**
3. Tests must map to specific Acceptance Criteria (AC) IDs from the PRD.
4. Each test file's docstring must reference the corresponding AC IDs.
5. Backend tests: pytest + pytest-asyncio + httpx.
6. End-to-end tests: Playwright.
7. Coverage targets: **overall ≥ 80%, auth / permission / multi-tenancy / cryptography code ≥ 95%​**.
8. **Coverage is not the only metric** — whether tests truly cover ACs, edge cases, and exception paths matters more than the percentage.
9. No "fake-passing" tests (e.g. `assert True`, `assert response is not None` as the only assertion).

## File Organization

- `backend/boxbase/core/` — Platform infrastructure (AuditMixin, config, database, dependencies, exceptions, security, router aggregator). No business logic.
- `backend/boxbase/zones/` — Business modules (vertical slices). Each zone owns its own `models/`, `router.py`, `schemas.py`, `service.py`.
- `backend/boxbase/zones/admin/` — Built-in platform admin module: User / Tenant / Membership / Role / Permission / RefreshToken (8 base tables) + auth/users/roles/admin routers. Cannot be removed.
- `backend/boxbase/zones/demo/` — Reference example for extension module authors.
- `backend/boxbase/main.py` — Minimal FastAPI app bootstrap.
- `backend/alembic/` — Single migrations directory; SQLite (dev) / PostgreSQL (prod) via config-switched URL.
- `backend/tests/` — Mirrors source structure (`tests/test_security.py`, `tests/zones/admin/`, `tests/zones/demo/`).
- `frontend/src/` — React admin UI (Week 1 baseline + Week 2 Day 4 login/register/dashboard).
- `frontend/e2e/` — Playwright e2e tests.
- `docs/architecture/` — Architecture specs (single source of truth per topic).
- `docs/decisions/` — Rolling session archives.
- `scripts/` — Cross-platform Python scripts.

**Module contract (Zone Contract)​**: Each zone exposes exactly one `router.py` (route entry) and one `service.py` (business logic entry). Internal split rules: routers split into `routers/` subdirectory when endpoints > 8; services split into `services/` subdirectory when functions > 10. Cross-zone horizontal imports are forbidden; `core/` MUST NOT import from any zone. New zones are registered by appending one line in `core/router.py`. See docs/architecture/2026-W2-platform-architecture-design.md for the full spec.

### API Routing Convention

All backend HTTP-accessible paths — both business APIs and OpenAPI documentation
(`/openapi.json`, `/docs`, `/redoc`) — are mounted under the `/api` prefix.

Implementation:
- Business routes use `APIRouter(prefix="/api")` and are included via `app.include_router()`.
- OpenAPI documentation paths are explicitly configured: `openapi_url="/api/openapi.json"`,
  `docs_url="/api/docs"`, `redoc_url="/api/redoc"`.

Implementation lives in `backend/boxbase/core/router.py`, which aggregates each zone's `router.py` under the `/api` prefix.

Rationale: Future reverse proxy / ingress only needs to expose a single rule (`/api/*`),
no per-endpoint allowlist. Dev (Vite proxy) and prod path layout are identical, so no
rewrite logic anywhere in the stack.

## Command Conventions (avoid command drift)

- Install Python deps: **​`uv add <pkg>` only**; never `pip install`.
- Run Python commands: **​`uv run <cmd>` only** (e.g. `uv run pytest`, `uv run alembic`).
- Install frontend deps: **​`pnpm add <pkg>` only**; never `npm install` or `yarn add`.
- Project tasks: invoke via Python scripts under `scripts/` or `Makefile` / `make.ps1`. No scattered shell commands.

## Git & Collaboration

- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`, `perf:`, `ci:`.
- Commit messages in **English** (for automated changelog and international collaboration).
- Each commit should change ≤ 200 lines; split when larger.
- Each PR addresses one clear goal (one AC or one refactor).
- Branch naming: `feature/AC1.1-register-user`, `fix/auth-token-refresh`, `chore/update-deps`.
- No direct pushes to `main`; always go through PRs.

## Communication Rules

1. **Before any non-trivial code change, propose a plan first** — files to create/modify, key decisions, potential risks. Wait for my approval.
2. **Show diffs for review.​** Do not auto-apply large changes.
3. **Reference AC IDs** when implementing features (e.g. "This implements AC1.5").
4. **Cite official doc URLs** when using third-party APIs to prevent hallucination.
5. **Say "I'm not sure"​** instead of guessing. Suggest investigation.
6. **Never invent APIs.​** If a method does not exist, say so.
7. **Read the full file before modifying it.​** For cross-file changes, run Grep to find all references first.
8. **Stop and ask me when context is insufficient**, rather than continuing on assumptions.

## Forbidden Actions

### Engineering discipline
- Do not install dependencies without telling me.
- Do not modify CI/CD configs without explicit instruction.
- Do not write production code without tests.
- Do not silence type/lint errors with `any`, `# type: ignore`, `noqa`. Fix the root cause.
- Do not add top-level dependencies without justifying why existing ones are insufficient.
- Do not create files outside the documented directory structure.

### Security red lines (violation = PR blocked)
- No hardcoded secrets (API keys, JWT secrets, DB passwords) in code or git.
- No MD5/SHA1/plain-text password handling. Use argon2 or bcrypt.
- No SQL string concatenation. Use parameterized queries or ORM.
- No `print()` of sensitive data (passwords, tokens, emails, PII).
- Do not skip permission checks or auth middleware "for testing convenience".
- Do not store any sensitive data in frontend code.

## Language Policy

| Content type | Language | Reason |
|---|---|---|
| Conversation with me | Chinese | My native language |
| AI's internal reasoning | Any (English preferred for quality) | Models reason slightly better in English |
| Variable / function / class / file names | English | Programming convention |
| Inline comments (# or //) | Chinese | Explain "why" |
| Docstrings / JSDoc | Chinese (Google style) | Owner prefers Chinese for maintainability |
| Commit messages | English (Conventional Commits) | Automated changelog & international collaboration |
| `docs/` project documentation | Chinese | Primarily for Chinese team |
| Backend logs & exception messages | English | Ops tooling compatibility |
| API error responses (to frontend) | English code + i18n key | Frontend renders per user language |
| Frontend UI copy | Chinese (default) + i18n structure | Primary user base |

## Chinese Communication Conventions

When chatting with me in Chinese:

1. Lead with the **conclusion**, then expand on technical details.
2. Annotate first occurrences of English technical terms with Chinese (e.g. "middleware（中间件）").
3. When refusing my unreasonable request, **say directly "不建议这么做，原因是……"​**.
4. When offering multiple options, clearly mark "我推荐方案 X，理由是……".
5. Before any code change, give 1–2 Chinese paragraphs explaining "why change, what changes, and what the risks are".

## Current Phase

**Week 2 Day 4: Authentication & Multi-tenancy backend + frontend baseline COMPLETE** (HEAD baseline: 9bfc11b). Backend 70/70 green, e2e 6/6 green at Day 4 sign-off, coverage global 94% / `boxbase.core.security` 100% (gates: 80% / 95%). CI Run #20 green.

Delivered in Week 2:
- Day 1: Architecture review (auth / multi-tenancy / RBAC) — see docs/architecture/2026-W2-auth-tenant-rbac-design.md.
- Day 2: ORM models (8 base tables) + `core/security` (PyJWT + pwdlib argon2) + seed.
- Day 3: `core/` + `zones/` modular refactor + 17 admin endpoints + `zones/demo/` reference module.
- Day 4: Frontend login/register/dashboard + `mise.toml` root dev task + Playwright e2e + refresh rotation race-condition fix (frontend dedup + single-flight lock + backend rotation grace) + orphan refresh-token elimination via `successor_jti` pointer + serialized rotation (SQLite `BEGIN IMMEDIATE` / PG `FOR UPDATE`) + superadmin-only expired-token cleanup endpoint.

We are now in **Week 2 Day 5: retrospective & wrap-up**. Focus:
- Week 2 retrospective document.
- Documentation reconciliation (this update + architecture spec changelog for Day 4).
- Tech-debt registry confirmation (global SQLite `BEGIN IMMEDIATE` to be re-evaluated for production multi-worker concurrency).
- Decide Week 3 scope (candidates: first real business module on top of `zones/demo/` template; lock-granularity refinement for refresh rotation).

**Day 5 discipline: documentation and retrospective FIRST, no new feature code until Week 3 scope is approved.**
See docs/decisions/2026-0601-week2-day4-complete.md for the latest rolling archive.

## When in Doubt

Ask me. I am the product owner. **Better to ask 10 clarifying questions than to write 100 lines of wrong code.​**
