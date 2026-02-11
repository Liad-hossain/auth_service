import os

import resend

from src.utils.helpers import get_html_template, render_html_template

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")


class ResendEmailHandler:
    def __init__(self, sender_email: str = ""):
        self.sender_email = sender_email or "liadhossain@gmail.com"
        resend.api_key = RESEND_API_KEY

    def send_email(
        self, to_email: str, subject: str, html_content: str
    ) -> resend.Email | None:
        try:
            params: resend.Emails.SendParams = {
                "from": self.sender_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            email: resend.Emails.SendResponse = resend.Emails.send(params)
            return email
        except Exception as e:
            print(f"Error sending email for {to_email}: {e}")
            return None

    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        subject = "Verify Your Email Address"
        html_template = get_html_template(template_file_name="verification_email.html")
        if not html_template:
            print("Error: HTML template for verification email not found.")
            return False

        context = {"verification_link": verification_link}
        html_content = render_html_template(html_template, context)
        email_response = self.send_email(to_email, subject, html_content)
        return email_response is not None
