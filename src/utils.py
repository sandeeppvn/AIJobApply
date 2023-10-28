import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Setting up logger
logger = logging.getLogger(__name__)

TEMPLATES = ["cover_letter_template", "resume_template", "email_template"]


def load_template_from_pdf(path: str, template_name: str) -> str:
    """Load content of a single template."""
    with open(f"{path}/{template_name}.pdf", "rb") as f:
        reader = PdfReader(f)
        return reader.pages[0].extract_text()


def load_templates(path: str = "templates") -> dict:
    """Load all templates from a directory."""
    templates = {}
    for template in TEMPLATES:
        try:
            templates[template] = load_template_from_pdf(path, template)
        except Exception as e:
            logger.exception(f"Error occurred while loading {template}: {e}")
    return templates


def send_email(
    email_content: str,
    recipient_email: str,
    sender_email: str,
    sender_password: str,
    subject: str,
) -> None:
    """Send an email using Gmail."""

    if not sender_email or not sender_password:
        logger.error("Gmail credentials not found")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(email_content, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            logger.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logger.exception(f"Error occurred while sending email: {e}")
