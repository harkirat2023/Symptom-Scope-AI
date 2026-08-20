"""Repository for the Health Assistant agent: user health profiles and pending actions."""

from datetime import UTC, datetime, timedelta

from bson.objectid import ObjectId

from utils.database import get_database

_COLLECTION_PROFILES = None
_COLLECTION_PENDING = None


def _get_profiles_collection():
    global _COLLECTION_PROFILES
    if _COLLECTION_PROFILES is None:
        _COLLECTION_PROFILES = get_database()["user_health_profiles"]
    return _COLLECTION_PROFILES


def _get_pending_collection():
    global _COLLECTION_PENDING
    if _COLLECTION_PENDING is None:
        _COLLECTION_PENDING = get_database()["pending_actions"]
    return _COLLECTION_PENDING


class ProfileRepository:
    async def get(self, user_id: str) -> dict | None:
        return await _get_profiles_collection().find_one({"userId": user_id})

    async def upsert(self, user_id: str, data: dict) -> dict:
        now = datetime.now(UTC).isoformat()
        update = {k: v for k, v in data.items() if v is not None}
        update["updatedAt"] = now
        await _get_profiles_collection().update_one(
            {"userId": user_id},
            {"$set": update, "$setOnInsert": {"createdAt": now}},
            upsert=True,
        )
        return await self.get(user_id)


class PendingActionRepository:
    def _ttl_hours(self) -> int:
        return 24

    async def create(
        self,
        user_id: str,
        session_id: str,
        tool: str,
        args: dict,
        summary: str,
    ) -> dict:
        now = datetime.now(UTC)
        action = {
            "userId": user_id,
            "sessionId": session_id,
            "tool": tool,
            "args": args,
            "summary": summary,
            "status": "pending",
            "createdAt": now.isoformat(),
            "expiresAt": (now + timedelta(hours=self._ttl_hours())).isoformat(),
        }
        result = await _get_pending_collection().insert_one(action)
        action["_id"] = str(result.inserted_id)
        return action

    async def find_by_id(self, pending_action_id: str) -> dict | None:
        return await _get_pending_collection().find_one(
            {"_id": ObjectId(pending_action_id)}
        )

    async def mark_resolved(
        self,
        pending_action_id: str,
        status: str,
        result: dict | None = None,
        error: str | None = None,
    ) -> dict | None:
        now = datetime.now(UTC).isoformat()
        update: dict = {
            "status": status,
            "resolvedAt": now,
        }
        if result is not None:
            update["result"] = result
        if error is not None:
            update["error"] = error
        await _get_pending_collection().update_one(
            {"_id": ObjectId(pending_action_id)},
            {"$set": update},
        )
        return await self.find_by_id(pending_action_id)

    async def expire_stale(self, user_id: str) -> None:
        now = datetime.now(UTC).isoformat()
        await _get_pending_collection().update_many(
            {"userId": user_id, "status": "pending", "expiresAt": {"$lt": now}},
            {"$set": {"status": "expired"}},
        )