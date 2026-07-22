import pytest
from services.hospital_service import HospitalService
import utils.database as db_mod
import repositories.hospital_repository as hr_mod


def _reset_db():
    db_mod._client = None
    db_mod._db = None
    hr_mod._COLLECTION = None


class TestHospitalService:
    @pytest.mark.asyncio
    async def test_search_returns_all(self):
        _reset_db()
        service = HospitalService()
        results = await service.search()
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_filter_by_location(self):
        _reset_db()
        service = HospitalService()
        results = await service.search(location="Ludhiana")
        assert len(results) > 0
        assert all(h["location"] == "Ludhiana" for h in results)

    @pytest.mark.asyncio
    async def test_filter_by_specialty_maps_to_department(self):
        _reset_db()
        service = HospitalService()
        results = await service.search(specialty="Cardiology")
        assert len(results) > 0
        assert all("Cardiology" in h["specialties"] for h in results)

    @pytest.mark.asyncio
    async def test_emergency_only(self):
        _reset_db()
        service = HospitalService()
        results = await service.search(emergency_only=True)
        assert len(results) > 0
        assert all(h["emergency"] for h in results)

    @pytest.mark.asyncio
    async def test_filter_by_query(self):
        _reset_db()
        service = HospitalService()
        results = await service.search(query="Apollo")
        assert len(results) > 0
        assert "Apollo" in results[0]["name"]

    @pytest.mark.asyncio
    async def test_sort_by_rating(self):
        _reset_db()
        service = HospitalService()
        results = await service.search(sort_by="rating", sort_order="desc")
        ratings = [h["rating"] for h in results]
        assert ratings == sorted(ratings, reverse=True)

    @pytest.mark.asyncio
    async def test_sort_by_distance(self):
        _reset_db()
        service = HospitalService()
        results = await service.search(sort_by="distance_km", sort_order="asc")
        distances = [h["distance_km"] for h in results]
        assert len(distances) > 0

    @pytest.mark.asyncio
    async def test_limit_results(self):
        _reset_db()
        service = HospitalService()
        results = await service.search(limit=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_locations(self):
        _reset_db()
        service = HospitalService()
        locations = await service.get_locations()
        assert "Ludhiana" in locations
        assert len(locations) >= 4

    @pytest.mark.asyncio
    async def test_get_specialties(self):
        _reset_db()
        service = HospitalService()
        specialties = await service.get_specialties()
        assert "Cardiology" in specialties
        assert "Emergency" in specialties
