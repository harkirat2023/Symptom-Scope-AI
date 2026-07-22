from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from utils.settings import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_database() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is not None:
        return _db
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=settings.mongodb_max_pool_size,
            minPoolSize=settings.mongodb_min_pool_size,
        )
    _db = _client["symptomscope"]
    return _db


async def ensure_indexes():
    db = get_database()
    predictions = db["predictions"]
    await predictions.create_index("userId")
    await predictions.create_index([("userId", 1), ("timestamp", -1)])
    await predictions.create_index("timestamp")

    chat_sessions = db["chat_sessions"]
    await chat_sessions.create_index("userId")
    await chat_sessions.create_index([("userId", 1), ("lastActivityAt", -1)])

    chat_messages = db["chat_messages"]
    await chat_messages.create_index("sessionId")
    await chat_messages.create_index([("sessionId", 1), ("createdAt", 1)])

    medicine_reminders = db["medicine_reminders"]
    await medicine_reminders.create_index("userId")
    await medicine_reminders.create_index([("userId", 1), ("status", 1)])
    await medicine_reminders.create_index("nextDueAt")

    reminder_logs = db["reminder_logs"]
    await reminder_logs.create_index("reminderId")
    await reminder_logs.create_index([("reminderId", 1), ("timestamp", -1)])

    health_risk_scores = db["health_risk_scores"]
    await health_risk_scores.create_index("userId")
    await health_risk_scores.create_index([("userId", 1), ("timestamp", -1)])

    user_health_profiles = db["user_health_profiles"]
    await user_health_profiles.create_index("userId", unique=True)

    from repositories.doctor_repository import ensure_indexes as doctor_indexes, seed_doctors
    from repositories.hospital_repository import ensure_indexes as hospital_indexes, seed_hospitals
    await doctor_indexes()
    await hospital_indexes()
    await seed_doctors()
    await seed_hospitals()


async def close_database():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
