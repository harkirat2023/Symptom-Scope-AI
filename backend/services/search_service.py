import difflib
import re
from typing import Any


def compute_relevance(query: str, text: str) -> float:
    q = query.lower().strip()
    t = text.lower().strip()
    if not q or not t:
        return 0.0
    if q == t:
        return 1.0
    if t.startswith(q):
        return 0.9
    if q in t:
        return 0.7
    words_q = set(re.split(r"[\s_]+", q))
    words_t = set(re.split(r"[\s_]+", t))
    common = words_q & words_t
    if common:
        return 0.5 * len(common) / max(len(words_q), 1)
    ratio = difflib.SequenceMatcher(None, q, t).ratio()
    if ratio > 0.6:
        return ratio * 0.4
    return 0.0


def score_and_sort(
    items: list[dict[str, Any]],
    query: str | None,
    search_fields: list[str],
    sort_by: str | None = None,
    sort_order: str = "desc",
    top_k: int = 50,
) -> list[tuple[float, dict[str, Any]]]:
    scored: list[tuple[float, dict[str, Any]]] = []
    for item in items:
        if query:
            score = max(
                compute_relevance(query, str(item.get(f, "")))
                for f in search_fields
            )
        else:
            score = 0.5
        scored.append((score, item))
    if sort_by:
        reverse = sort_order != "asc"
        scored.sort(key=lambda x: (-x[0], x[1].get(sort_by, 0) if sort_by else 0))
        if reverse:
            scored.sort(key=lambda x: (-x[0], -x[1].get(sort_by, 0)))
    else:
        scored.sort(key=lambda x: -x[0])
    return scored[:top_k]


def filter_by_field(
    items: list[dict[str, Any]],
    field: str,
    value: str | None,
    exact: bool = False,
) -> list[dict[str, Any]]:
    if not value:
        return items
    v = value.lower().strip()
    if exact:
        return [i for i in items if str(i.get(field, "")).lower() == v]
    return [
        i
        for i in items
        if v in str(i.get(field, "")).lower()
    ]
