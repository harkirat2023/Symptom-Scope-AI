import asyncio
import logging
from datetime import datetime, timezone
from services.email_service import EmailService

logger = logging.getLogger("symptomscope")


class ReminderScheduler:
    def __init__(self):
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Reminder scheduler started")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Reminder scheduler stopped")

    async def _poll_loop(self):
        while self._running:
            try:
                await self._check_due_reminders()
            except Exception as e:
                logger.error(f"Reminder check error: {e}")
            await asyncio.sleep(300)

    async def _check_due_reminders(self):
        from repositories.reminder_repository import ReminderRepository

        repo = ReminderRepository()
        email_service = EmailService()
        due = await repo.find_due_reminders()

        for reminder in due:
            try:
                reminder_id = str(reminder["_id"])
                user_id = reminder["userId"]

                if reminder.get("email_reminder"):
                    to_email = await self._resolve_user_email(user_id)
                    if to_email:
                        await email_service.send_reminder_email(
                            to_email,
                            reminder["medicine_name"],
                            reminder["dosage"],
                            reminder_id,
                            user_id,
                        )

                next_due = repo._compute_next_due(
                    reminder.get("start_time", "08:00")
                )
                from repositories.reminder_repository import _get_reminders_collection

                await _get_reminders_collection().update_one(
                    {"_id": reminder["_id"]},
                    {"$set": {"nextDueAt": next_due}},
                )

                logger.info(
                    f"Reminder triggered: {reminder['medicine_name']} for user {user_id}"
                )
            except Exception as e:
                logger.error(f"Error processing reminder {reminder.get('_id')}: {e}")

    async def _resolve_user_email(self, user_id: str) -> str | None:
        """Resolve the recipient email from the health profile (agent-captured)
        or, as a fallback, the legacy users collection."""
        from utils.database import get_database

        db = get_database()
        profile = await db["user_health_profiles"].find_one({"userId": user_id})
        if profile and profile.get("email"):
            return profile["email"]

        from bson.objectid import ObjectId

        try:
            user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
        except Exception:
            user_doc = None
        if user_doc and user_doc.get("email"):
            return user_doc["email"]

        user_doc = await db["users"].find_one({"userId": user_id})
        return user_doc.get("email") if user_doc else None


# Singleton scheduler instance
scheduler = ReminderScheduler()
