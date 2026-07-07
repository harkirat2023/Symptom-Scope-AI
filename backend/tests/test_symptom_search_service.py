from services.symptom_search_service import SymptomSearchService


class TestSymptomSearchService:
    def setup_method(self):
        self.service = SymptomSearchService()

    def test_get_all_returns_all_symptoms(self):
        results = self.service.get_all()
        assert len(results) > 0
        assert all("id" in r and "name" in r and "category" in r for r in results)

    def test_search_no_query_returns_limited_results(self):
        results = self.service.search(limit=5)
        assert len(results) == 5

    def test_search_by_query(self):
        results = self.service.search(query="fever")
        assert len(results) > 0
        assert any("fever" in r["id"] for r in results)

    def test_search_by_category(self):
        results = self.service.search(category="Respiratory")
        assert all(r["category"] == "Respiratory" for r in results)

    def test_search_with_query_and_category(self):
        results = self.service.search(query="cough", category="Respiratory")
        assert len(results) > 0
        assert all(r["category"] == "Respiratory" for r in results)

    def test_get_categories(self):
        categories = self.service.get_categories()
        assert "General" in categories
        assert "Respiratory" in categories
        assert "Neurological" in categories

    def test_get_by_category(self):
        results = self.service.get_by_category("Respiratory")
        assert len(results) > 0
        assert all(r["category"] == "Respiratory" for r in results)
