# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

OmniTool is a Flask multi-tool web app (weather, currency converter, to-do list, file/document conversion, YouTube channel browser) with user authentication. Server-rendered Jinja templates styled with Tailwind + DaisyUI. SQLite in development, PostgreSQL in production.

## Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run (dev) — FLASK_APP defaults to app.py via the module-level `app = create_app()`
flask run                    # http://127.0.0.1:5000
python run.py                # alternative entrypoint

# Run (production)
gunicorn app:app             # `app` is the WSGI callable in app.py

# Database migrations (Flask-Migrate / Alembic)
flask db migrate -m "describe change"   # generate migration after editing models.py
flask db upgrade                        # apply to DB
flask db downgrade                      # revert last migration
```

There is **no test suite** in the repo (a `TestingConfig` exists in [config.py](config.py) but no tests are written yet). There is no separate lint/build step; `.prettierignore` exists but Prettier is not wired into a script.

## Architecture

**App factory + blueprints.** [app.py](app.py) defines `create_app(config_name)` which wires extensions, registers blueprints, and installs global handlers. A module-level `app = create_app()` is the WSGI/Flask-CLI entrypoint. `config_name` resolves from `FLASK_ENV` (default `development`).

**Extensions are singletons** instantiated unbound in [extensions.py](extensions.py) (`db`, `migrate`, `login_manager`, `csrf`, `limiter`) and bound to the app inside `create_app`. Import extensions from here, never re-instantiate them.

**Configuration** ([config.py](config.py)) is class-based, selected via the `config` dict (`development`/`production`/`testing`/`default`). `ProductionConfig.init_app` enforces `SECRET_KEY` + `DATABASE_URL` presence, rewrites `postgres://` / `postgresql://` URIs to `postgresql+psycopg://`, and hardens session cookies. All secrets/API keys come from environment variables (see [.env.example](.env.example)).

**Each feature is a blueprint** in [modules/](modules/), registered in `create_app`:
- `auth` — registration/login/logout/account ([modules/auth.py](modules/auth.py))
- `weather` — OpenWeatherMap forecast, public (no login) ([modules/weather.py](modules/weather.py))
- `currency` — ExchangeRate-API conversion, login-required, logs history ([modules/currency.py](modules/currency.py))
- `todo` — task CRUD, login-required ([modules/todo.py](modules/todo.py))
- `conversion` — image + PDF/DOCX/TXT tools, public ([modules/conversion.py](modules/conversion.py))
- `youtube` — YouTube Data API channel feed with infinite scroll ([modules/youtube.py](modules/youtube.py))

**Models** ([models.py](models.py)): `User` (Flask-Login `UserMixin`, werkzeug password hashing) plus per-user `CurrencyLog`, `FavoriteCurrencyPair`, `Todo`, `FavoriteWeatherLocation`. After any model change, generate and apply a migration.

**Forms.** Shared WTForms live in [forms.py](forms.py); the conversion module defines its own forms inline in [modules/conversion.py](modules/conversion.py). Use `FlaskForm` so CSRF tokens are included automatically.

## Conventions & constraints

- **CSRF is enforced globally.** All state-changing routes are POST-only and require a CSRF token (rendered via the form). Complete/delete actions (e.g. `/todo/complete/<id>`, `/todo/delete/<id>`) are POST, not GET — preserve this.
- **Per-user ownership checks.** Routes that mutate user-owned rows fetch with `db.get_or_404(...)` then verify `obj.user_id == current_user.id`, calling `abort(403)` / flashing otherwise (see `_get_user_task_or_403` in todo, the favorite-pair routes in currency). Follow this pattern for any new owned resource.
- **File-upload security** (conversion module): uploads are size-capped (`MAX_FILE_SIZE` 10 MB, plus `MAX_CONTENT_LENGTH` in config) and validated by **magic bytes** (`_is_valid_image`, `_is_pdf_bytes`, `_is_zip_bytes`), not by filename/extension. PDFs are rejected if encrypted and capped at `MAX_PDF_PAGES`. Keep validating content, not trust the client.
- **Rate limiting** via `@limiter.limit(...)` decorators on auth and conversion/currency POST routes. Add limits to new sensitive or expensive endpoints.
- **Security headers + CSP** are set in `after_request` in [app.py](app.py). If you add a CDN, external script, or iframe source, update the `Content-Security-Policy` string there or it will be blocked.
- **External API calls** use `requests` with a connect/read timeout (`REQUESTS_TIMEOUT = (5, 10)` from config) and are wrapped in try/except that flashes a user-facing error and logs. Match this when adding API calls. User-supplied currency codes / video IDs / page tokens are regex-validated before use.
- **Theme** (light/dark) is stored in an httponly cookie, synced to `session["theme"]` in `before_request`, and injected into every template via the `inject_theme` context processor.
- Parts of the codebase have **Polish** docstrings/comments — both languages appear; match the surrounding file.
