<!-- This file is the SINGLE SOURCE OF TRUTH for all AI coding agents working on BoxBase.
     Cursor, Claude Code, GitHub Copilot, Codex, Trae, and others all read this file.
     Do NOT duplicate rules in tool-specific files; reference this file instead. -->

# BoxBase Project AI Working Rules

You are assisting in the development of BoxBase — a lightweight, modular Python framework for multi-tenant SaaS.

## Project Identity

- Project: BoxBase v1.0
- Languages: Python 3.12 (backend), TypeScript 5 (frontend)
- Backend stack: FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2
- Frontend stack: React 18 + Ant Design Pro + Vite + Ant Design X (for the AI module)
- Database: SQLite (dev) / PostgreSQL 13+ (prod)
- Package managers: uv (Python), pnpm (Node)

## Core Design Principles

1. **Modular First**: Every feature should be implementable as a self-contained module under `modules/`.
2. **Multi-tenancy is mandatory**: All business tables MUST have an `org_id` column. Use SQLAlchemy event listeners to auto-inject `WHERE org_id` filters.
3. **Permission abstraction**: All permission checks go through the `PermissionChecker` interface. Business code MUST NOT call Casbin or any concrete implementation directly.
4. **Open-source reuse over reinvention**: Prefer FastAPI Users, fastapi-mail, slowapi, secure, sse-starlette, LiteLLM. If you choose to write something from scratch, justify it in the PR description.
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

- `backend/boxbase/core/` — Core abstractions (interfaces, base classes)
- `backend/boxbase/auth/` — Authentication (FastAPI Users integration)
- `backend/boxbase/tenant/` — Multi-tenancy (org, membership, isolation)
- `backend/boxbase/rbac/` — Role-based access control
- `backend/boxbase/modules/` — Module loader and lifecycle
- `backend/boxbase/audit/` — Audit logging
- `backend/tests/` — All backend tests, mirroring the source structure
- `frontend/src/` — React admin UI
- `frontend/tests/` — React admin UI tests
- `modules/` — Example user-developed modules
- `docs/` — Sphinx documentation source (in Chinese)
- `scripts/` — Cross-platform project scripts (written in Python to avoid bash/PowerShell drift)

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

We are in **Week 1: Engineering Foundation**. Focus only on:
- Project skeleton (`pyproject.toml`, `package.json`)
- Linting, formatting, type checking (ruff, mypy, prettier, eslint)
- CI/CD pipelines (GitHub Actions)
- Test framework setup (pytest, Playwright)
- Pre-commit hooks
- One Hello World endpoint and one Hello World test

**Do NOT start implementing business features (auth, tenant, RBAC, modules, audit) until I explicitly say "begin Week 2".​**

## When in Doubt

Ask me. I am the product owner. **Better to ask 10 clarifying questions than to write 100 lines of wrong code.​**
