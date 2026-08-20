from datetime import UTC, datetime, timedelta

from utils.database import get_database

_COLLECTION_SCORES = None
_COLLECTION_PROFILES = None


def _get_scores_collection():
    global _COLLECTION_SCORES
    if _COLLECTION_SCORES is None:
        _COLLECTION_SCORES = get_database()["health_risk_scores"]
    return _COLLECTION_SCORES


def _get_profiles_collection():
    global _COLLECTION_PROFILES
    if _COLLECTION_PROFILES is None:
        _COLLECTION_PROFILES = get_database()["user_health_profiles"]
    return _COLLECTION_PROFILES


RANGE_DAYS = {"1m": 30, "3m": 90, "6m": 180, "1y": 365}


class RiskScoreRepository:
    async def save_score(
        self,
        user_id: str,
        score: float,
        category: str,
        breakdown: dict,
        prediction_id: str | None = None,
    ) -> dict:
        now = datetime.now(UTC).isoformat()
        doc = {
            "userId": user_id,
            "score": score,
            "category": category,
            "breakdown": breakdown,
            "predictionId": prediction_id,
            "timestamp": now,
        }
        result = await _get_scores_collection().insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    async def get_latest_score(self, user_id: str) -> dict | None:
        cursor = (
            _get_scores_collection()
            .find({"userId": user_id})
            .sort("timestamp", -1)
            .limit(1)
        )
        docs = await cursor.to_list(length=1)
        return docs[0] if docs else None

    async def get_score_history(
        self, user_id: str, time_range: str = "6m", limit: int = 50
    ) -> list[dict]:
        days = RANGE_DAYS.get(time_range, 180)
        cutoff = datetime.now(UTC) - timedelta(days=days)
        cursor = (
            _get_scores_collection()
            .find(
                {
                    "userId": user_id,
                    "timestamp": {"$gte": cutoff.isoformat()},
                }
            )
            .sort("timestamp", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def upsert_profile(
        self, user_id: str, data: dict
    ) -> dict:
        now = datetime.now(UTC).isoformat()
        data["updatedAt"] = now
        await _get_profiles_collection().update_one(
            {"userId": user_id},
            {"$set": data},
            upsert=True,
        )
        profile = await _get_profiles_collection().find_one(
            {"userId": user_id}
        )
        return profile

    async def get_profile(self, user_id: str) -> dict | None:
        return await _get_profiles_collection().find_one(
            {"userId": user_id}
        )

    async def get_all_scores_for_user(
        self, user_id: str, limit: int = 10
    ) -> list[dict]:
        cursor = (
            _get_scores_collection()
            .find({"userId": user_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)
