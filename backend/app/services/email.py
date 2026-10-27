import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

logger = logging.getLogger("EmailService")

class EmailService:
    @staticmethod
    def is_configured() -> bool:
        provider = os.getenv("EMAIL_PROVIDER", "").strip()
        host = os.getenv("EMAIL_HOST", "").strip()
        username = os.getenv("EMAIL_USERNAME", "").strip()
        return bool(provider or host or username)

    @staticmethod
    def get_status() -> Dict[str, Any]:
        configured = EmailService.is_configured()
        return {
            "configured": configured,
            "status": "READY" if configured else "EMAIL SERVICE NOT CONFIGURED",
            "provider": os.getenv("EMAIL_PROVIDER", "SMTP"),
            "admin_email": os.getenv("ADMIN_EMAIL", "admin@saarthi.ai")
        }

    @staticmethod
    def send_transactional_email(to_email: str, subject: str, body: str, event_type: str = "GENERAL") -> Dict[str, Any]:
        """
        Sends transactional email if configured via environment variables.
        If unconfigured, returns 'EMAIL SERVICE NOT CONFIGURED' status.
        """
        if not EmailService.is_configured():
            logger.info(f"Skipping email dispatch for event '{event_type}' to '{to_email}': Email service not configured.")
            return {
                "status": "EMAIL SERVICE NOT CONFIGURED",
                "sent": False,
                "event_type": event_type,
                "recipient": to_email,
                "reason": "EMAIL_PROVIDER or SMTP credentials not configured in environment."
            }

        host = os.getenv("EMAIL_HOST", "localhost")
        port = int(os.getenv("EMAIL_PORT", "587"))
        username = os.getenv("EMAIL_USERNAME", "")
        password = os.getenv("EMAIL_PASSWORD", "")
        from_email = os.getenv("EMAIL_FROM", username or "noreply@saarthi.ai")

        try:
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(host, port, timeout=10)
            server.starttls()
            if username and password:
                server.login(username, password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()

            logger.info(f"Successfully sent email ({event_type}) to {to_email}")
            return {
                "status": "SENT",
                "sent": True,
                "event_type": event_type,
                "recipient": to_email
            }
        except Exception as e:
            logger.error(f"Failed to send email ({event_type}) to {to_email}: {e}")
            return {
                "status": "FAILED",
                "sent": False,
                "event_type": event_type,
                "recipient": to_email,
                "error": str(e)
            }

    @staticmethod
    def notify_admin(subject: str, details: str, event_type: str = "ADMIN_NOTIFICATION") -> Dict[str, Any]:
        admin_email = os.getenv("ADMIN_EMAIL", "")
        if not admin_email:
            return {"status": "ADMIN EMAIL NOT CONFIGURED", "sent": False}
        return EmailService.send_transactional_email(admin_email, f"[Saarthi Admin] {subject}", details, event_type)
