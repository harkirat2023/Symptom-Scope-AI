from fastapi import APIRouter, Depends, Query, Request
from schemas.doctor_schema import DoctorResponse, DoctorSearchResponse
from services.doctor_service import DoctorService
from auth.dependency import get_current_user
from utils.rate_limit import limiter

router = APIRouter()


@router.get("/doctors", response_model=DoctorSearchResponse)
@limiter.limit("30/minute")
async def get_doctors(
    request: Request,
    q: str | None = Query(None, max_length=200, description="Free-text search across name, specialty, location"),
    specialty: str | None = Query(None, max_length=100, description="Filter by exact specialty"),
    location: str | None = Query(None, max_length=100, description="Filter by location"),
    sort_by: str | None = Query(None, description="Sort field: rating, distance_km, availability"),
    sort_order: str = Query("desc", description="Sort direction: asc or desc"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    _: str = Depends(get_current_user),
    doctor_service: DoctorService = Depends(),
):
    results = doctor_service.get_recommendations(
        specialty=specialty,
        location=location,
        query=q,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
    )
    return DoctorSearchResponse(
        results=[DoctorResponse(**d) for d in results],
        total=len(results),
        specialties=doctor_service.get_specialties(),
        locations=doctor_service.get_locations(),
    )


@router.get("/doctors/specialties", response_model=list[str])
@limiter.limit("30/minute")
async def get_doctor_specialties(
    request: Request,
    _: str = Depends(get_current_user),
    doctor_service: DoctorService = Depends(),
):
    return doctor_service.get_specialties()


@router.get("/doctors/locations", response_model=list[str])
@limiter.limit("30/minute")
async def get_doctor_locations(
    request: Request,
    _: str = Depends(get_current_user),
    doctor_service: DoctorService = Depends(),
):
    return doctor_service.get_locations()
