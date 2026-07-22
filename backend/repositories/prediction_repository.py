from datetime import datetime, timezone, timedelta
from schemas.prediction_schema import PredictionRecord
from utils.database import get_database

_COLLECTION = None

RANGE_DAYS = {"1m": 30, "3m": 90, "6m": 180, "1y": 365}


def _get_collection():
    global _COLLECTION
    if _COLLECTION is None:
        _COLLECTION = get_database()["predictions"]
    return _COLLECTION


class PredictionRepository:
    async def create(
        self,
        user_id: str,
        symptoms: list[str],
        prediction: str,
        confidence: float,
        severity: str,
        age: int | None = None,
        gender: str | None = None,
        existing_conditions: list[str] | None = None,
        symptom_duration: str | None = None,
        pain_level: int | None = None,
    ) -> PredictionRecord:
        record = {
            "userId": user_id,
            "symptoms": symptoms,
            "prediction": prediction,
            "confidence": confidence,
            "severity": severity,
            "age": age,
            "gender": gender,
            "existingConditions": existing_conditions or [],
            "symptomDuration": symptom_duration,
            "painLevel": pain_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        collection = _get_collection()
        result = await collection.insert_one(record)
        return PredictionRecord(
            _id=str(result.inserted_id),
            user_id=user_id,
            symptoms=symptoms,
            prediction=prediction,
            confidence=confidence,
            severity=severity,
            timestamp=record["timestamp"],
        )

    async def find_by_id(self, prediction_id: str) -> PredictionRecord | None:
        from bson.objectid import ObjectId
        collection = _get_collection()
        d = await collection.find_one({"_id": ObjectId(prediction_id)})
        if not d:
            return None
        return PredictionRecord(
            _id=str(d["_id"]),
            user_id=d["userId"],
            symptoms=d.get("symptoms", []),
            prediction=d.get("prediction", ""),
            confidence=d.get("confidence", 0.0),
            severity=d.get("severity", ""),
            timestamp=d.get("timestamp", ""),
        )

    async def find_by_user(
        self,
        user_id: str,
        time_range: str | None = None,
    ) -> list[PredictionRecord]:
        collection = _get_collection()
        query: dict = {"userId": user_id}
        if time_range and time_range in RANGE_DAYS:
            cutoff = datetime.now(timezone.utc) - timedelta(days=RANGE_DAYS[time_range])
            query["timestamp"] = {"$gte": cutoff.isoformat()}
        cursor = collection.find(
            query,
            projection={
                "_id": 1, "userId": 1, "symptoms": 1, "prediction": 1,
                "confidence": 1, "severity": 1, "timestamp": 1,
            },
        ).sort("timestamp", -1).limit(100)
        docs = await cursor.to_list(length=100)
        return [
            PredictionRecord(
                _id=str(d["_id"]),
                user_id=d["userId"],
                symptoms=d.get("symptoms", []),
                prediction=d.get("prediction", ""),
                confidence=d.get("confidence", 0.0),
                severity=d.get("severity", ""),
                timestamp=d.get("timestamp", ""),
            )
            for d in docs
        ]
