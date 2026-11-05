import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app


def send_notification_email(student_id, message):
    """Email an unread notification when SMTP is configured and enabled."""
    settings = current_app.config
    required = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM")
    if not all(settings.get(key) for key in required):
        return False

    from .database import get_db

    student = get_db().execute(
        "SELECT name,email,email_notifications FROM users WHERE id=? AND role='student'",
        (student_id,),
    ).fetchone()
    if not student or not student["email_notifications"] or not student["email"]:
        return False

    email = EmailMessage()
    email["Subject"] = "New placement notification"
    email["From"] = settings["SMTP_FROM"]
    email["To"] = student["email"]
    email.set_content(
        f"Hello {student['name']},\n\n"
        f"You have a new unread notification in CampusBridge:\n\n{message}\n\n"
        "Sign in to the placement portal to view it."
    )

    try:
        port = settings["SMTP_PORT"]
        if port == 465:
            with smtplib.SMTP_SSL(
                settings["SMTP_HOST"], port, context=ssl.create_default_context(), timeout=10
            ) as server:
                server.login(settings["SMTP_USERNAME"], settings["SMTP_PASSWORD"])
                server.send_message(email)
        else:
            with smtplib.SMTP(settings["SMTP_HOST"], port, timeout=10) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(settings["SMTP_USERNAME"], settings["SMTP_PASSWORD"])
                server.send_message(email)
        return True
    except (OSError, smtplib.SMTPException):
        current_app.logger.exception("Could not send placement notification email")
        return False
