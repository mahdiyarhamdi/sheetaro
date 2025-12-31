# ADR-20251213: Initial Architecture Decisions

## Status

**Accepted**

## Context

We needed to build a Telegram bot for ordering labels and business cards with a backend API. The system must handle:
- User registration and profile management via Telegram
- Order processing (future)
- Integration with Telegram Bot API
- Scalability for future features

## Decision

### 1. Backend Framework: FastAPI

**Chosen**: FastAPI over Flask/Django

**Rationale**:
- Native async support for high concurrency
- Automatic OpenAPI documentation
- Pydantic integration for validation
- Modern Python 3.12 features
- Excellent performance

### 2. Database: PostgreSQL with SQLAlchemy 2.x (Async)

**Chosen**: PostgreSQL + asyncpg + SQLAlchemy 2.x

**Rationale**:
- PostgreSQL: Robust, ACID-compliant, excellent JSON support
- Async: Required for FastAPI async handlers
- SQLAlchemy 2.x: Modern ORM with full async support
- Alembic: Battle-tested migration tool

### 3. Architecture: Layered (Clean Architecture)

**Chosen**: Router → Service → Repository → Model

**Rationale**:
- Clear separation of concerns
- Testable layers in isolation
- Business logic decoupled from framework
- Easy to extend without refactoring

### 4. Bot Framework: python-telegram-bot

**Chosen**: python-telegram-bot 21.x

**Rationale**:
- Official-style library, well maintained
- Full async support (asyncio)
- Comprehensive Telegram API coverage
- Good documentation and community

### 5. Containerization: Docker Compose

**Chosen**: Docker Compose for all services

**Rationale**:
- Consistent development environment
- Easy local setup
- Production-like testing
- Service isolation

### 6. Communication: REST API (not direct DB access)

**Chosen**: Bot communicates with Backend via HTTP REST API

**Rationale**:
- Decoupled services
- Backend can be scaled independently
- API can serve other clients (web, mobile)
- Cleaner service boundaries

## Consequences

### Positive

- Clean, maintainable codebase
- Easy onboarding for new developers
- Scalable architecture
- Framework-agnostic business logic

### Negative

- More boilerplate than monolithic approach
- HTTP overhead between bot and backend
- Need to maintain API contracts

### Risks

- Over-engineering for MVP scope
- Complexity may slow initial development

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Django | Heavier, sync-first, not needed for API-only |
| Flask | Less structured, no native async |
| Direct DB from bot | Tight coupling, no API reuse |
| MongoDB | No clear benefit, team has PostgreSQL experience |
| GraphQL | Overkill for current requirements |

---

**Date**: 2024-12-13  
**Author**: Development Team




