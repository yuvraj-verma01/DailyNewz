from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText


def send_email(
    html: str,
    subject: str,
    from_email: str,
    to_email: str,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 465,
) -> None:
    password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
    if not password:
        raise ValueError("GMAIL_APP_PASSWORD is not set")

    message = MIMEText(html, "html", "utf-8")
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(from_email, password)
            server.sendmail(from_email, [to_email], message.as_string())
    except smtplib.SMTPAuthenticationError as exc:
        raise ValueError(
            "Gmail authentication failed. Use an App Password for the Gmail "
            "account that matches from_email."
        ) from exc
