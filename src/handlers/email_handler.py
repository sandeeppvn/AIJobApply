import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Setting up logger
logger = logging.getLogger(__name__)

class EmailHandler:
    def __init__(self, sender_email: str, sender_password: str):
        """
        Initialize EmailHandler object with Email credentials.
        """
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send(
        self,
        content: str,
        recepient_email: str,
        subject: str = "Request for Job Networking Opportunity",
    ):
        """
        Send an email with the given content and subject.

        Args:
        - content (str): Message Content.
        - email (str): Recipient email address.
        - subject (str): Message subject line.
        """
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recepient_email
        message["Subject"] = subject
        message.attach(MIMEText(content, "plain"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recepient_email, message.as_string())
                logger.info(f"Message sent to {recepient_email}")
        except Exception as e:
            logger.exception(f"Error occurred while sending email: {e}")