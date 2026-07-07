from fastapi import APIRouter, Depends, Query, Request
from schemas.symptom_schema import SymptomSearchResponse, SymptomResult
from services.symptom_search_service import SymptomSearchService
from auth.dependency import get_current_user
from utils.rate_limit import limiter

router = APIRouter()


@router.get("/symptoms/search", response_model=SymptomSearchResponse)
@limiter.limit("30/minute")
async def search_symptoms(
    request: Request,
    q: str | None = Query(None, max_length=200, description="Search query"),
    category: str | None = Query(None, max_length=100, description="Filter by symptom category"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    _: str = Depends(get_current_user),
    symptom_service: SymptomSearchService = Depends(),
):
    results = symptom_service.search(query=q, category=category, limit=limit)
    categories = symptom_service.get_categories()
    return SymptomSearchResponse(
        results=[
            SymptomResult(
                id=r["id"],
                name=r["name"],
                category=r["category"],
                relevance_score=r.get("relevance_score") if q else None,
            )
            for r in results
        ],
        total=len(results),
        categories=categories,
    )


@router.get("/symptoms/categories", response_model=list[str])
@limiter.limit("30/minute")
async def get_symptom_categories(
    request: Request,
    _: str = Depends(get_current_user),
    symptom_service: SymptomSearchService = Depends(),
):
    return symptom_service.get_categories()


@router.get("/symptoms", response_model=SymptomSearchResponse)
@limiter.limit("30/minute")
async def list_all_symptoms(
    request: Request,
    _: str = Depends(get_current_user),
    symptom_service: SymptomSearchService = Depends(),
):
    results = symptom_service.get_all()
    categories = symptom_service.get_categories()
    return SymptomSearchResponse(
        results=[
            SymptomResult(id=r["id"], name=r["name"], category=r["category"])
            for r in results
        ],
        total=len(results),
        categories=categories,
    )
