from src.utils import send_email


class EmailHandler:
    def send(self, content, email, subject):
        """
        Send an email with the given content and subject.

        Args:
        - content (str): Email content.
        - email (str): Recipient email address.
        - subject (str): Email subject line.
        """
        send_email(content, email, subject)
