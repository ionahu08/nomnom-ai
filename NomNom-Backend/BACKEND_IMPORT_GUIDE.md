# Backend API Import Guide

**Purpose:** Prevent import errors when creating new API endpoints.

## Correct Import Patterns

### For New API Endpoints

```python
# Standard imports
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

# Authentication & Database dependencies
from src.api.deps import get_current_user, security
from src.database import get_db

# Models (ORM)
from src.models.user import User
from src.models.food_log import FoodLog

# Schemas (Pydantic request/response)
from src.schemas.food_log import FoodLogCreate, FoodLogResponse
from src.schemas.analytics import AnalyticsSummaryResponse

# Services (business logic)
from src.services.profile_service import get_effective_targets

# Repositories (data access)
from src.repositories.analytics_repository import AnalyticsRepository
```

## Module Reference

| Purpose | Module | What to Import |
|---------|--------|-----------------|
| Auth & deps | `src.api.deps` | `get_current_user`, `security` |
| Database session | `src.database` | `get_db` |
| ORM Models | `src.models.*` | Specific model classes |
| Pydantic schemas | `src.schemas.*` | Request/response schema classes |
| Business logic | `src.services.*` | Service functions |
| Data access | `src.repositories.*` | Repository classes |
| Configuration | `src.config` | Settings, environment vars |

## Common Mistakes

### ❌ WRONG: Non-existent modules
```python
from src.api.dependencies import ...  # This module doesn't exist!
from src.api import deps              # Wrong import syntax
```

### ❌ WRONG: Mixing layers
```python
from src.llm.client import ...        # Don't import LLM stuff in API
from src.models.food_log import FoodLogCreate  # Wrong! Use schemas instead
```

### ❌ WRONG: Wrong sync/async
```python
from sqlalchemy.orm import Session  # WRONG - use AsyncSession
# Should be:
from sqlalchemy.ext.asyncio import AsyncSession
```

## Checklist Before Committing New API Files

- [ ] Check all imports are from modules that exist
- [ ] Verify no imports from `src.api.dependencies` (wrong module name)
- [ ] Use `AsyncSession` not `Session` (async required)
- [ ] Use `src.api.deps` for authentication, not other modules
- [ ] Use `src.database` for get_db, not other modules
- [ ] Run `python -m uvicorn src.app:app` and verify "Application startup complete"
- [ ] Test with curl: should get response, not timeout
- [ ] Run pytest: `pytest tests/` should pass

## Example: Creating /api/v1/analytics Endpoint

```python
# analytics.py - CORRECT IMPORTS

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Annotated

# ✅ CORRECT
from src.api.deps import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.analytics import AnalyticsSummaryResponse
from src.repositories.analytics_repository import AnalyticsRepository

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_weekly_summary(
    period: Annotated[str, Query()] = "week",
    date: Annotated[str, Query()] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get weekly nutrition summary for current user."""
    # Implementation here
    pass
```

## If Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'src.api.dependencies'`

**Solution:**
1. Check analytics.py (or new file) line 7-8
2. Change `from src.api.dependencies import ...` to:
   - `from src.api.deps import get_current_user`
   - `from src.database import get_db`
3. Restart backend: `python -m uvicorn src.app:app --reload`
4. Verify: "Application startup complete" appears in console

## Backend Startup Validation

Every time you modify src/api or src/app.py:

```bash
cd NomNom-Backend
./venv/bin/python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

Should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

If you see `ModuleNotFoundError` or the process hangs, there's an import error.

---

**Last Updated:** Iteration 18, Phase 1 (after import error bug)
