# Backend Repositories

Data access layer for SymptomScope AI.

## Pattern

All database queries go through repositories — routes never access MongoDB directly.

| Repository | Collection | Key Methods |
|------------|------------|-------------|
| `prediction_repository.py` | `predictions` | `create()`, `find_by_user()`, `find_by_id()` |

## Usage

```python
@router.post("/predict")
async def predict(
    repo: PredictionRepository = Depends(),
):
    record = await repo.create(user_id=..., symptoms=..., ...)
```

## MongoDB Collections

- `users` — managed by Clerk
- `predictions` — indexed on `userId`, `userId+timestamp`, `timestamp`
- `reports` — aggregated report data
- `doctors` — static curated database (Phase 1)
- `hospitals` — static curated database (Phase 1)
- `alerts` — future notification records
