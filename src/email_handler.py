from src.utils import send_email


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
        send_email(content, recepient_email, self.sender_email, self.sender_password, subject)
