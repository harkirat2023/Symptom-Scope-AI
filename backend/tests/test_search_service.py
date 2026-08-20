from services.search_service import compute_relevance, filter_by_field, score_and_sort


class TestComputeRelevance:
    def test_exact_match(self):
        assert compute_relevance("fever", "fever") == 1.0

    def test_starts_with(self):
        assert compute_relevance("fev", "fever") == 0.9

    def test_contains(self):
        assert compute_relevance("ever", "fever") == 0.7

    def test_empty_query_returns_zero(self):
        assert compute_relevance("", "fever") == 0.0

    def test_empty_text_returns_zero(self):
        assert compute_relevance("fever", "") == 0.0

    def test_partial_word_match(self):
        score = compute_relevance("Cardio", "Cardiologist")
        assert score > 0

    def test_no_match_returns_zero(self):
        assert compute_relevance("xyzabc", "fever") == 0.0


class TestScoreAndSort:
    def test_empty_items(self):
        assert score_and_sort([], "test", ["name"]) == []

    def test_scores_items_by_query(self):
        items = [{"name": "fever"}, {"name": "headache"}]
        scored = score_and_sort(items, "fever", ["name"])
        assert len(scored) == 2
        assert scored[0][0] >= scored[1][0]

    def test_no_query_returns_default_score(self):
        items = [{"name": "test"}]
        scored = score_and_sort(items, None, ["name"])
        assert scored[0][0] == 0.5


class TestFilterByField:
    def test_exact_match(self):
        items = [{"city": "Ludhiana"}, {"city": "Amritsar"}]
        result = filter_by_field(items, "city", "Ludhiana", exact=True)
        assert len(result) == 1
        assert result[0]["city"] == "Ludhiana"

    def test_partial_match(self):
        items = [{"city": "Ludhiana"}, {"city": "Amritsar"}]
        result = filter_by_field(items, "city", "ludh")
        assert len(result) == 1

    def test_no_value_returns_all(self):
        items = [{"city": "Ludhiana"}]
        result = filter_by_field(items, "city", None)
        assert len(result) == 1

    def test_no_match_returns_empty(self):
        items = [{"city": "Ludhiana"}]
        result = filter_by_field(items, "city", "Mumbai")
        assert len(result) == 0
