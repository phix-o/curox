# Curox Backend - AI Agent Development Guide

## Project Overview
Curox is a FastAPI-based event management system. Key tech stack: **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Alembic migrations**, **Pydantic**, **JWT auth**, **FastMail**, and file storage.

## Architecture Patterns

### Feature-Based Modular Structure
The codebase follows a feature-driven directory pattern under `src/features/`:
- `auth/`, `companies/`, `events/` are independent feature modules
- Each feature has: `models.py`, `schemas.py`, `repo.py`, `dependencies.py`, `v1/router.py`, and `tests/`
- Feature isolation enables parallel development and clear separation of concerns

### Repository Pattern for Data Access
- **Base**: `src/common/repo.py` defines `RepoBase[T]` generic class with CRUD operations
- **Usage**: Each feature extends `RepoBase` (e.g., `UserRepo`, `EventsRepo`)
- **Database session injection**: Use `get_repo()` dependency factory for session management
- **Query building**: Repos expose `.query()` for complex filters using SQLAlchemy expressions

### Dependency Injection
- FastAPI dependencies in `dependencies.py` per feature (e.g., `UserRepoDep`, `EventsRepoDep`)
- Dependencies are type-hinted Annotated objects returned as function parameters
- Automatic session lifecycle management via dependency factory

### Request/Response Pattern
- **Schemas**: Pydantic models in `schemas.py` define request/response contracts
- **Custom Responses**: `build_response()` wraps all success responses in `CustomResponse[T]` from `src/common/utils/responses.py`
- **Error Handling**: Custom exceptions (`BadRequestException`, `NotFoundException`) automatically serialized via `handle_http_exception()` in `src/core/exceptions.py`

## Key Integration Points

### Authentication
- **JWT Bearer tokens**: `src/core/auth/backend.py` validates tokens via middleware
- **Token injection**: Authenticated `UserModel` injected as `request.user`
- **Protected routes**: Use `Depends(JWTBearer())` on routers requiring authentication
- Token pair creation: `create_token_pair()` from `src/core/auth`

### Database
- **Base model mixin**: All models extend from `Base` in `src/core/database.py`, which includes `id`, `created_at`, `updated_at` columns
- **Session management**: `SessionLocal()` factory from `src/core/database.py`, or use dependency injection
- **Migrations**: Alembic auto-generates from models in `src/models.py` (imports all feature models)
- **Integrity errors**: Wrapped in `UniqueValidationError` via custom `DBSession.commit()`

### File Storage
- **Backend abstraction**: `src/core/storage/backend.py` provides `StorageBackend` interface
- **Current implementation**: `FileStorageBackend` saves to `settings.static_path`, serves via `settings.static_url`
- **Upload method**: `storage_backend.upload_file(file, path)` returns file path; call `get_url(path)` for public URL
- Example: Avatar uploads in `UserRepo.update_avatar()`

### Email
- **FastMail setup**: `src/core/mail/__init__.py` configures `FastMail` with SMTP credentials from settings
- **Template support**: HTML templates in `src/core/mail/templates/`, context passed as dict
- **Async send**: `await send_email(subject, to, template_name, context)`
- Example: Password reset emails in `src/features/auth/utils.py`

## Development Workflows

### Running Locally
```bash
# Setup (one-time)
uv venv && . .venv/bin/activate && uv sync

# Migrations (before first run)
alembic upgrade head

# Start server
fastapi run src/main.py --port 8000
```

### Migrations
```bash
# Auto-generate (after model changes)
alembic revision --autogenerate -m 'description'

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing
```bash
pytest  # Runs with coverage reports (term + htmlcov/)
```
- Test files co-located in `tests/v1/test_*.py` near routers
- Use `TestClient` from `fastapi.testclient`

### Docker
```bash
docker compose up --build
```

## Codebase Conventions

### Error Handling
- Raise custom exceptions from `src/common/exceptions.py` (e.g., `BadRequestException`, `NotFoundException`, `UnauthorisedException`)
- Pass `data` dict as second arg to attach additional context to responses
- Handler automatically serializes to JSON with `error`, `message`, `data` fields

### Logging
- Use `src/core/logger.logger` for logging (configured via `configure_for_dev()` / `configure_for_prod()`)
- Info/debug calls in core services; errors caught and re-raised with context

### Model Naming
- Database models: `*Model` suffix (e.g., `UserModel`, `EventModel`)
- Schemas (Pydantic): `*Schema` suffix (e.g., `UserCreateSchema`, `EventDetailsSchema`)
- Repos: `*Repo` suffix (e.g., `UserRepo`, `EventsRepo`)

### Config
- All settings in `src/core/config.py` as `Settings` Pydantic model
- Environment variables auto-populated via `SettingsConfigDict`
- Access via `settings.db_url`, `settings.mail_host`, etc.

## Common Tasks

### Adding a New Endpoint
1. Extend feature router in `src/features/[feature]/v1/router.py`
2. Add Pydantic schema in `src/features/[feature]/schemas.py`
3. Use repo from dependencies (injected)
4. Return `build_response(data)` wrapped in `CustomResponse[YourSchema]`
5. Add test in `src/features/[feature]/tests/v1/test_router.py`

### Adding a Database Model
1. Define in `src/features/[feature]/models.py`, extend `Base`
2. Import in `src/models.py` to register with Alembic
3. Run `alembic revision --autogenerate -m 'description'`
4. Review migration, run `alembic upgrade head`

### Cross-Feature Communication
- Features access other repos via dependency injection (e.g., `StaffRepoDep` in events router)
- Avoid circular imports; use models in other features' repos if needed

## Files to Reference
- **Main app**: `src/main.py` - FastAPI setup, middleware, exception handlers
- **Base structures**: `src/common/repo.py`, `src/core/database.py`
- **Auth flow**: `src/core/auth/backend.py`, `src/features/auth/v1/router.py`
- **Example endpoint**: `src/features/events/v1/router.py` (complex queries, role checks)
