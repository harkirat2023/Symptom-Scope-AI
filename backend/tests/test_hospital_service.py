from services.hospital_service import HospitalService


class TestHospitalService:
    def setup_method(self):
        self.service = HospitalService()

    def test_search_returns_all(self):
        results = self.service.search()
        assert len(results) == 8

    def test_filter_by_location(self):
        results = self.service.search(location="Ludhiana")
        assert all(h["location"] == "Ludhiana" for h in results)

    def test_filter_by_specialty_maps_to_department(self):
        results = self.service.search(specialty="Cardiologist")
        assert all(
            "Cardiology" in h["specialties"]
            for h in results
        )

    def test_emergency_only(self):
        results = self.service.search(emergency_only=True)
        assert all(h["has_emergency"] for h in results)

    def test_filter_by_query(self):
        results = self.service.search(query="Apollo")
        assert len(results) == 8
        assert "Apollo" in results[0]["name"]

    def test_sort_by_rating(self):
        results = self.service.search(sort_by="rating", sort_order="desc")
        ratings = [h["rating"] for h in results]
        assert ratings == sorted(ratings, reverse=True)

    def test_sort_by_distance(self):
        results = self.service.search(sort_by="distance_km", sort_order="asc")
        distances = [h["distance_km"] for h in results]
        assert len(distances) > 0

    def test_limit_results(self):
        results = self.service.search(limit=3)
        assert len(results) == 3

    def test_get_locations(self):
        locations = self.service.get_locations()
        assert "Ludhiana" in locations
        assert len(locations) >= 4

    def test_get_specialties(self):
        specialties = self.service.get_specialties()
        assert "Cardiology" in specialties
        assert "Emergency" in specialties
