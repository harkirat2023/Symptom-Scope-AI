import smtplib
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

    async def send_reminder_email(
        self, to_email: str, medicine_name: str, dosage: str
    ) -> bool:
        if not self.host or not self.user:
            logger.warning("SMTP not configured — skipping reminder email")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "SymptomScope - Medicine Reminder"
            msg["From"] = self.from_email
            msg["To"] = to_email

            text = (
                f"Medicine Reminder\n\n"
                f"It's time to take your medication:\n"
                f"Medicine: {medicine_name}\n"
                f"Dosage: {dosage}\n\n"
                f"Log your status in the SymptomScope app.\n\n"
                f"This is an automated reminder from SymptomScope AI."
            )

            html = (
                f"<html><body>"
                f"<h2>SymptomScope - Medicine Reminder</h2>"
                f"<p>It's time to take your medication:</p>"
                f"<p><strong>Medicine:</strong> {medicine_name}<br>"
                f"<strong>Dosage:</strong> {dosage}</p>"
                f"<p>Log your status in the <a href='https://symptomscope.vercel.app'>SymptomScope app</a>.</p>"
                f"<hr><p style='color:#666;font-size:12px;'>"
                f"This is an automated reminder from SymptomScope AI.</p>"
                f"</body></html>"
            )

            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Reminder email sent to {to_email} for {medicine_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send reminder email: {e}")
            return False
