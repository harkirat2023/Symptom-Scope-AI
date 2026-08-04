import smtplib
import secrets
import hashlib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.settings import settings
import logging
from fastapi import Request

logger = logging.getLogger("symptomscope")


class EmailService:
    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.secret_key = settings.secret_key

    def _create_signed_action_link(self, reminder_id: str, action: str, user_id: str, expires_in_hours: int = 24) -> str:
        timestamp = str(int(time.time()) + expires_in_hours * 3600)
        signature = hashlib.sha256(f"{reminder_id}:{action}:{user_id}:{timestamp}".encode()).hexdigest()
        token = secrets.token_urlsafe(16)
        return f"https://symptomscope.vercel.app/api/reminders/{reminder_id}/action?token={token}&action={action}&expires={timestamp}&signature={signature}"

    async def send_reminder_email(
        self, to_email: str, medicine_name: str, dosage: str, reminder_id: str, user_id: str
    ) -> bool:
        if not self.host or not self.user:
            logger.warning("SMTP not configured — skipping reminder email")
            return False

        try:
            yes_link = self._create_signed_action_link(reminder_id, "taken", user_id)
            no_link = self._create_signed_action_link(reminder_id, "missed", user_id)

            text = (
                f"Medicine Reminder\n\n"
                f"It's time to take your medication:\n"
                f"Medicine: {medicine_name}\n"
                f"Dosage: {dosage}\n\n"
                f"Please log your status:\n"
                f"YES: {yes_link}\n"
                f"NO: {no_link}\n\n"
                f"This is an automated reminder from SymptomScope AI."
            )

            html = (
                f"<html><body>"
                f"<h2>SymptomScope - Medicine Reminder</h2>"
                f"<p>It's time to take your medication:</p>"
                f"<p><strong>Medicine:</strong> {medicine_name}<br>"
                f"<strong>Dosage:</strong> {dosage}</p>"
                f"<p><strong>Please log your status:</strong></p>"
                f"<p><a href='{yes_link}' style='background-color: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;'>YES - Mark as Taken</a>"
                f"<a href='{no_link}' style='background-color: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>NO - Mark as Missed</a></p>"
                f"<hr><p style='color:#666;font-size:12px;'>"
                f"This is an automated reminder from SymptomScope AI.</p>"
                f"</body></html>"
            )

            msg = MIMEMultipart("alternative")
            msg["Subject"] = "SymptomScope - Medicine Reminder"
            msg["From"] = self.from_email
            msg["To"] = to_email

            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Reminder email sent to {to_email} for {medicine_name} with action links")
            return True

        except Exception as e:
            logger.error(f"Failed to send reminder email: {e}")
            return False

    async def process_reminder_action(self, request: Request, reminder_id: str, action: str, token: str) -> bool:
        try:
            query = dict(request.query_params)
            if not all(k in query for k in ["action", "expires", "signature"]):
                return False

            if query["action"] != action:
                return False

            expires = int(query["expires"])
            if expires < time.time():
                return False

            user_id = query.get("user_id")
            if not user_id:
                return False

            calculated_signature = hashlib.sha256(f"{reminder_id}:{action}:{user_id}:{expires}".encode()).hexdigest()
            if calculated_signature != query["signature"]:
                return False

            from repositories.reminder_repository import ReminderRepository
            repo = ReminderRepository()
            await repo.log_status(reminder_id, user_id, action, "Logged via email")

            return True
        except Exception as e:
            logger.error(f"Error processing reminder action: {e}")
            return False
