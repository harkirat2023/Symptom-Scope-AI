from datetime import datetime, timezone, timedelta
from utils.database import get_database

_COLLECTION_REMINDERS = None
_COLLECTION_LOGS = None


def _get_reminders_collection():
    global _COLLECTION_REMINDERS
    if _COLLECTION_REMINDERS is None:
        _COLLECTION_REMINDERS = get_database()["medicine_reminders"]
    return _COLLECTION_REMINDERS


def _get_logs_collection():
    global _COLLECTION_LOGS
    if _COLLECTION_LOGS is None:
        _COLLECTION_LOGS = get_database()["reminder_logs"]
    return _COLLECTION_LOGS


class ReminderRepository:
    async def create(self, user_id: str, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        next_due = self._compute_next_due(data.get("start_time", "08:00"))
        reminder = {
            **data,
            "userId": user_id,
            "status": "active",
            "nextDueAt": next_due,
            "createdAt": now,
            "updatedAt": now,
        }
        result = await _get_reminders_collection().insert_one(reminder)
        reminder["_id"] = str(result.inserted_id)
        return reminder

    async def find_by_user(
        self,
        user_id: str,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        query: dict = {"userId": user_id}
        if status:
            query["status"] = status
        cursor = (
            _get_reminders_collection()
            .find(query)
            .sort("nextDueAt", 1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def find_by_id(self, reminder_id: str) -> dict | None:
        from bson.objectid import ObjectId
        return await _get_reminders_collection().find_one(
            {"_id": ObjectId(reminder_id)}
        )

    async def update(self, reminder_id: str, data: dict) -> dict | None:
        from bson.objectid import ObjectId
        data["updatedAt"] = datetime.now(timezone.utc).isoformat()
        if "start_time" in data:
            data["nextDueAt"] = self._compute_next_due(data["start_time"])
        await _get_reminders_collection().update_one(
            {"_id": ObjectId(reminder_id)},
            {"$set": data},
        )
        return await self.find_by_id(reminder_id)

    async def delete(self, reminder_id: str) -> bool:
        from bson.objectid import ObjectId
        result = await _get_reminders_collection().delete_one(
            {"_id": ObjectId(reminder_id)}
        )
        return result.deleted_count > 0

    async def log_status(
        self, reminder_id: str, user_id: str, status: str, note: str | None = None
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        log_entry = {
            "reminderId": reminder_id,
            "userId": user_id,
            "status": status,
            "timestamp": now,
            "note": note,
        }
        result = await _get_logs_collection().insert_one(log_entry)
        log_entry["_id"] = str(result.inserted_id)

        next_due = self._compute_next_due_from_now()
        await _get_reminders_collection().update_one(
            {"_id": reminder_id},
            {"$set": {"nextDueAt": next_due, "updatedAt": now}},
        )
        return log_entry

    async def find_upcoming(
        self, user_id: str
    ) -> dict | None:
        now = datetime.now(timezone.utc).isoformat()
        cursor = (
            _get_reminders_collection()
            .find(
                {
                    "userId": user_id,
                    "status": "active",
                    "nextDueAt": {"$gte": now},
                }
            )
            .sort("nextDueAt", 1)
            .limit(1)
        )
        docs = await cursor.to_list(length=1)
        return docs[0] if docs else None

    async def find_due_reminders(self) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()
        cursor = (
            _get_reminders_collection()
            .find(
                {
                    "status": "active",
                    "nextDueAt": {"$lte": now},
                }
            )
            .limit(100)
        )
        return await cursor.to_list(length=100)

    @staticmethod
    def _compute_next_due(start_time: str) -> str:
        now = datetime.now(timezone.utc)
        parts = start_time.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if due <= now:
            due += timedelta(days=1)
        return due.isoformat()

    @staticmethod
    def _compute_next_due_from_now() -> str:
        return (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()
