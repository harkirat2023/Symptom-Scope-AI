from fastapi import APIRouter, Depends, Query, Request
from schemas.hospital_schema import HospitalResponse, HospitalSearchResponse
from services.hospital_service import HospitalService
from auth.dependency import get_current_user
from utils.rate_limit import limiter

router = APIRouter()


@router.get("/hospitals", response_model=HospitalSearchResponse)
@limiter.limit("30/minute")
async def search_hospitals(
    request: Request,
    q: str | None = Query(None, max_length=200, description="Free-text search across name, location, specialties"),
    location: str | None = Query(None, max_length=100, description="Filter by city/location"),
    specialty: str | None = Query(None, max_length=100, description="Filter by medical specialty (e.g., Cardiologist)"),
    emergency_only: bool = Query(False, description="Show only hospitals with emergency services"),
    sort_by: str | None = Query(None, description="Sort field: rating, distance_km"),
    sort_order: str = Query("desc", description="Sort direction: asc or desc"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    _: str = Depends(get_current_user),
    hospital_service: HospitalService = Depends(),
):
    results = await hospital_service.search(
        query=q,
        location=location,
        specialty=specialty,
        emergency_only=emergency_only,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
    )
    return HospitalSearchResponse(
        hospitals=[HospitalResponse(**h) for h in results],
        total=len(results),
        locations=await hospital_service.get_locations(),
    )


@router.get("/hospitals/locations", response_model=list[str])
@limiter.limit("30/minute")
async def get_hospital_locations(
    request: Request,
    _: str = Depends(get_current_user),
    hospital_service: HospitalService = Depends(),
):
    return await hospital_service.get_locations()
