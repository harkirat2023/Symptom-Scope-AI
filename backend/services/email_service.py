import smtplib
import hashlib
import hmac
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.settings import settings
import logging

logger = logging.getLogger("symptomscope")


class EmailService:
    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.secret_key = settings.secret_key

    def configured(self) -> bool:
        return bool(self.host and self.user and self.password and self.from_email)

    def _base_url(self) -> str:
        return settings.public_base_url.rstrip("/") if getattr(settings, "public_base_url", None) else ""

    def _create_signed_action_link(self, reminder_id: str, action: str, user_id: str, expires_in_hours: int = 48) -> str:
        """Build a signed one-click link for reminder status logging.

        The signature is an HMAC over the payload so only the backend can mint
        valid links. No authentication token is required to open the link.
        """
        expires = str(int(time.time()) + expires_in_hours * 3600)
        payload = f"{reminder_id}:{action}:{user_id}:{expires}"
        signature = hmac.new(
            self.secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return (
            f"{self._base_url()}/api/v1/reminders/{reminder_id}/action"
            f"?action={action}&user={user_id}&expires={expires}&sig={signature}"
        )

    def verify_action_signature(self, reminder_id: str, action: str, user_id: str, expires: str, signature: str) -> bool:
        """Verify an action-link signature and expiry."""
        try:
            if not expires or int(expires) < int(time.time()):
                return False
            payload = f"{reminder_id}:{action}:{user_id}:{expires}"
            expected = hmac.new(
                self.secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, signature or "")
        except Exception:
            return False

    def _send(self, to_email: str, subject: str, text: str, html: str) -> bool:
        if not self.configured():
            logger.warning("SMTP not configured — skipping email to %s", to_email)
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            logger.info("Email sent to %s (subject=%s)", to_email, subject)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, e)
            return False

    async def send_reminder_email(
        self, to_email: str, medicine_name: str, dosage: str, reminder_id: str, user_id: str
    ) -> bool:
        if not self.configured():
            logger.warning("SMTP not configured — skipping reminder email")
            return False

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

        return self._send(to_email, "SymptomScope - Medicine Reminder", text, html)

    async def send_recovery_plan_email(
        self, to_email: str, disease: str, plan_id: str | None = None
    ) -> bool:
        """Notify the user that their personalized recovery plan is ready."""
        if not self.configured():
            logger.warning("SMTP not configured — skipping recovery plan email")
            return False

        text = (
            f"Your SymptomScope recovery plan is ready!\n\n"
            f"Based on your latest symptom check ({disease}), a personalized "
            f"recovery plan has been generated for you.\n\n"
            f"Open the app and go to the Recovery Plan page to view it. "
            f"Remember to set up your medication reminders and follow up with "
            f"a healthcare professional.\n\n"
            f"Stay safe,\nSymptomScope AI"
        )
        html = (
            f"<html><body>"
            f"<h2>Your recovery plan is ready</h2>"
            f"<p>Based on your latest symptom check (<strong>{disease}</strong>), "
            f"a personalized recovery plan has been generated for you.</p>"
            f"<p>Open the SymptomScope app and go to the <strong>Recovery Plan</strong> "
            f"page to view it. Don't forget to set up your medication reminders.</p>"
            f"<hr><p style='color:#666;font-size:12px;'>"
            f"Educational purposes only. Always consult a healthcare professional.</p>"
            f"</body></html>"
        )
        return self._send(to_email, "Your SymptomScope recovery plan is ready", text, html)
