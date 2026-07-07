from services.doctor_service import DoctorService


class TestDoctorService:
    def setup_method(self):
        self.service = DoctorService()

    def test_get_recommendations_returns_all(self):
        results = self.service.get_recommendations()
        assert len(results) == 8

    def test_filter_by_specialty(self):
        results = self.service.get_recommendations(specialty="Cardiologist")
        assert all("Cardiologist" in d["specialty"] for d in results)

    def test_filter_by_location(self):
        results = self.service.get_recommendations(location="Ludhiana")
        assert all(d["location"] == "Ludhiana" for d in results)

    def test_filter_by_query(self):
        results = self.service.get_recommendations(query="Sharma")
        assert len(results) > 0
        assert results[0]["name"] == "Dr. Sharma"

    def test_sort_by_rating_desc(self):
        results = self.service.get_recommendations(sort_by="rating", sort_order="desc")
        ratings = [d["rating"] for d in results]
        assert ratings == sorted(ratings, reverse=True)

    def test_sort_by_rating_asc(self):
        results = self.service.get_recommendations(sort_by="rating", sort_order="asc")
        ratings = [d["rating"] for d in results]
        assert ratings == sorted(ratings)

    def test_limit_results(self):
        results = self.service.get_recommendations(limit=3)
        assert len(results) == 3

    def test_get_specialty_for_disease(self):
        assert self.service.get_specialty_for_disease("Influenza") == "General Physician"
        assert self.service.get_specialty_for_disease("Heart Attack") == "Cardiologist"
        assert self.service.get_specialty_for_disease("Stroke") == "Neurologist"

    def test_get_specialty_unknown_disease(self):
        assert self.service.get_specialty_for_disease("Unknown") == "General Physician"

    def test_get_specialties(self):
        specialties = self.service.get_specialties()
        assert "Cardiologist" in specialties
        assert len(specialties) >= 5

    def test_get_locations(self):
        locations = self.service.get_locations()
        assert "Ludhiana" in locations
        assert len(locations) == 4

    def test_explain_recommendation(self):
        explanation = self.service.explain_recommendation("Dr. Sharma", "Influenza")
        assert "Dr. Sharma" in explanation
        assert "General Physician" in explanation
        assert "matches" in explanation

    def test_explain_recommendation_no_disease(self):
        explanation = self.service.explain_recommendation("Dr. Sharma")
        assert "Dr. Sharma" in explanation

    def test_explain_recommendation_unknown_doctor(self):
        assert self.service.explain_recommendation("Dr. Unknown") == ""
