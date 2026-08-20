import pytest

import repositories.doctor_repository as dr_mod
import utils.database as db_mod
from services.doctor_service import DoctorService


def _reset_db():
    """Reset cached database/repo globals to avoid event loop conflicts."""
    db_mod._client = None
    db_mod._db = None
    dr_mod._COLLECTION = None


class TestDoctorService:
    @pytest.mark.asyncio
    async def test_get_recommendations_returns_all(self):
        _reset_db()
        service = DoctorService()
        results = await service.get_recommendations()
        assert len(results) == 15

    @pytest.mark.asyncio
    async def test_filter_by_specialty(self):
        _reset_db()
        service = DoctorService()
        results = await service.get_recommendations(specialty="Cardiologist")
        assert all("Cardiologist" in d["specialty"] for d in results)

    @pytest.mark.asyncio
    async def test_filter_by_location(self):
        _reset_db()
        service = DoctorService()
        results = await service.get_recommendations(location="Ludhiana")
        assert all(d["location"] == "Ludhiana" for d in results)

    @pytest.mark.asyncio
    async def test_filter_by_query(self):
        _reset_db()
        service = DoctorService()
        results = await service.get_recommendations(query="Sharma")
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_sort_by_rating_desc(self):
        _reset_db()
        service = DoctorService()
        results = await service.get_recommendations(sort_by="rating", sort_order="desc")
        ratings = [d["rating"] for d in results]
        assert ratings == sorted(ratings, reverse=True)

    @pytest.mark.asyncio
    async def test_sort_by_rating_asc(self):
        _reset_db()
        service = DoctorService()
        results = await service.get_recommendations(sort_by="rating", sort_order="asc")
        ratings = [d["rating"] for d in results]
        assert ratings == sorted(ratings)

    @pytest.mark.asyncio
    async def test_limit_results(self):
        _reset_db()
        service = DoctorService()
        results = await service.get_recommendations(limit=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_specialty_for_disease(self):
        _reset_db()
        service = DoctorService()
        assert await service.get_specialty_for_disease("Influenza") == "General Physician"
        assert await service.get_specialty_for_disease("Heart Attack") == "Cardiologist"
        assert await service.get_specialty_for_disease("Stroke") == "Neurologist"

    @pytest.mark.asyncio
    async def test_get_specialty_unknown_disease(self):
        _reset_db()
        service = DoctorService()
        assert await service.get_specialty_for_disease("Unknown") == "General Physician"

    @pytest.mark.asyncio
    async def test_get_specialties(self):
        _reset_db()
        service = DoctorService()
        specialties = await service.get_specialties()
        assert "Cardiologist" in specialties
        assert len(specialties) >= 5

    @pytest.mark.asyncio
    async def test_get_locations(self):
        _reset_db()
        service = DoctorService()
        locations = await service.get_locations()
        assert "Ludhiana" in locations
        assert len(locations) >= 4

    @pytest.mark.asyncio
    async def test_explain_recommendation(self):
        _reset_db()
        service = DoctorService()
        explanation = await service.explain_recommendation("Dr. Sharma", "Influenza")
        assert "Dr. Sharma" in explanation
        assert "General Physician" in explanation

    @pytest.mark.asyncio
    async def test_explain_recommendation_no_disease(self):
        _reset_db()
        service = DoctorService()
        explanation = await service.explain_recommendation("Dr. Sharma")
        assert "Dr. Sharma" in explanation

    @pytest.mark.asyncio
    async def test_explain_recommendation_unknown_doctor(self):
        _reset_db()
        service = DoctorService()
        result = await service.explain_recommendation("Dr. Unknown")
        assert "Dr. Unknown" in result
        assert "recommended" in result
