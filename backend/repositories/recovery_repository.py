from datetime import datetime, timezone
from utils.database import get_database
from bson.objectid import ObjectId


_COLLECTION = None


def _get_collection():
    global _COLLECTION
    if _COLLECTION is None:
        _COLLECTION = get_database()["recovery_plans"]
    return _COLLECTION


class RecoveryPlanRepository:
    async def create(
        self,
        user_id: str,
        prediction_id: str,
        disease: str,
        confidence: float,
        severity: str,
        symptoms: list[str],
        plan_data: dict,
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        plan = {
            "userId": user_id,
            "predictionId": prediction_id,
            "disease": disease,
            "confidence": confidence,
            "severity": severity,
            "symptoms": symptoms,
            "planData": plan_data,
            "isRegenerated": False,
            "regenerationCount": 0,
            "createdAt": now,
            "updatedAt": now,
        }
        result = await _get_collection().insert_one(plan)
        plan["_id"] = str(result.inserted_id)
        return plan

    async def find_by_id(self, plan_id: str) -> dict | None:
        return await _get_collection().find_one({"_id": ObjectId(plan_id)})

    async def find_by_prediction(self, prediction_id: str) -> dict | None:
        return await _get_collection().find_one({"predictionId": prediction_id})

    async def find_latest_by_user(self, user_id: str) -> dict | None:
        cursor = (
            _get_collection()
            .find({"userId": user_id})
            .sort("createdAt", -1)
            .limit(1)
        )
        return await cursor.to_list(length=1)

    async def find_by_user(self, user_id: str, limit: int = 20) -> list[dict]:
        cursor = (
            _get_collection()
            .find({"userId": user_id})
            .sort("createdAt", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def regenerate_plan(self, plan_id: str, plan_data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        result = await _get_collection().update_one(
            {"_id": ObjectId(plan_id)},
            {
                "$set": {
                    "planData": plan_data,
                    "isRegenerated": True,
                    "regenerationCount": {"$inc": 1},
                    "updatedAt": now,
                }
            },
        )
        if result.modified_count:
            return await self.find_by_id(plan_id)
        return None