from datetime import datetime, timezone
from utils.database import get_database

_COLLECTION_SESSIONS = None
_COLLECTION_MESSAGES = None


def _get_sessions_collection():
    global _COLLECTION_SESSIONS
    if _COLLECTION_SESSIONS is None:
        _COLLECTION_SESSIONS = get_database()["chat_sessions"]
    return _COLLECTION_SESSIONS


def _get_messages_collection():
    global _COLLECTION_MESSAGES
    if _COLLECTION_MESSAGES is None:
        _COLLECTION_MESSAGES = get_database()["chat_messages"]
    return _COLLECTION_MESSAGES


class ChatRepository:
    async def create_session(
        self, user_id: str, prediction_context: dict | None = None
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        session = {
            "userId": user_id,
            "startedAt": now,
            "lastActivityAt": now,
            "isActive": True,
            "predictionContext": prediction_context,
        }
        result = await _get_sessions_collection().insert_one(session)
        session["_id"] = str(result.inserted_id)
        return session

    async def get_user_sessions(
        self, user_id: str, limit: int = 20
    ) -> list[dict]:
        cursor = (
            _get_sessions_collection()
            .find({"userId": user_id})
            .sort("lastActivityAt", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_session(self, session_id: str) -> dict | None:
        from bson.objectid import ObjectId
        return await _get_sessions_collection().find_one(
            {"_id": ObjectId(session_id)}
        )

    async def deactivate_session(self, session_id: str):
        from bson.objectid import ObjectId
        await _get_sessions_collection().update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"isActive": False}}
        )

    async def add_message(
        self, session_id: str, role: str, content: str
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        message = {
            "sessionId": session_id,
            "role": role,
            "content": content,
            "createdAt": now,
        }
        result = await _get_messages_collection().insert_one(message)
        message["_id"] = str(result.inserted_id)

        await _get_sessions_collection().update_one(
            {"_id": session_id},
            {"$set": {"lastActivityAt": now}}
        )
        return message

    async def get_session_messages(
        self, session_id: str, limit: int = 50
    ) -> list[dict]:
        from bson.objectid import ObjectId

        cursor = (
            _get_messages_collection()
            .find({"sessionId": session_id})
            .sort("createdAt", 1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def deactivate_stale_sessions(self, user_id: str, timeout_minutes: int = 30):
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        cutoff_iso = cutoff.isoformat()
        await _get_sessions_collection().update_many(
            {"userId": user_id, "isActive": True, "lastActivityAt": {"$lt": cutoff_iso}},
            {"$set": {"isActive": False}}
        )
