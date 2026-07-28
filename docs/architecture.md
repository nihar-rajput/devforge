# DevForge Architecture

## Overview

DevForge follows **Clean Architecture** with strict dependency rules:

```
API Layer (FastAPI routes, schemas)
    ↓ depends on
Service Layer (orchestrators)
    ↓ depends on
Domain Layer (entities, ports, events, errors)
    ↑ NO dependency on infrastructure
Infrastructure Layer (SQLite, Windows Registry, subprocess)
    ↑ implements domain ports
```

## Layer Rules

1. **Domain Layer** (`src/core/`) — ZERO external dependencies. Pure Python + Pydantic only.
2. **Infrastructure Layer** (`src/database/`, `src/system/`, `src/downloader/`) — Implements abstract ports defined in domain.
3. **Service Layer** (`src/services/`, `src/installer/`, `src/detector/`) — Orchestrates domain entities and ports.
4. **API Layer** (`src/api/`) — FastAPI routes. Thin handlers that delegate to services.

## Communication

```
React UI ←→ [REST + WebSocket] ←→ FastAPI Backend
                                      ↓
                                Event Bus (in-process async)
                                      ↓
                            ┌─────────┼─────────┐
                            ↓         ↓         ↓
                      WebSocket   Event Store   Logger
                      Handler    (SQLite)     (structlog)
```

## Key Design Decisions

See [design_decisions.md](design_decisions.md) for detailed rationale.
