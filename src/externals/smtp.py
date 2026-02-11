import logging
import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

from src.utils.helpers import get_html_template, render_html_template

logger = logging.getLogger("stdout")

load_dotenv()


class SMTPEmailHandler:
    def __init__(self):
        self.SMTP_EMAIL = os.getenv("SMTP_EMAIL")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.SMTP_HOST = os.getenv("SMTP_HOST")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT"))
        if not all(
            [self.SMTP_EMAIL, self.SMTP_PASSWORD, self.SMTP_HOST, self.SMTP_PORT]
        ):
            raise ValueError(
                "SMTP configuration is incomplete. Please check environment variables."
            )

    def send_email(self, to_email: str, subject: str, html_content: str):
        try:
            msg = MIMEText(html_content, "html")
            msg["Subject"] = subject
            msg["From"] = self.SMTP_EMAIL
            msg["To"] = to_email

            with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT) as server:
                server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        subject = "Verify Your Email Address"
        html_template = get_html_template(template_file_name="verification_email.html")
        if not html_template:
            print("Error: HTML template for verification email not found.")
            return False

        context = {"verification_link": verification_link}
        html_content = render_html_template(html_template, context)
        return self.send_email(to_email, subject, html_content)
