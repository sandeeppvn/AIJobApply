from unittest.mock import MagicMock, patch

import pytest

from src.email_handler import EmailHandler


@pytest.fixture
def email_credentials():
    return {
        "sender_email": "example@example.com",
        "sender_password": "password123"
    }

@pytest.fixture
def email_handler(email_credentials):
    return EmailHandler(email_credentials["sender_email"], email_credentials["sender_password"])

def test_email_handler_initialization(email_credentials):
    handler = EmailHandler(email_credentials["sender_email"], email_credentials["sender_password"])
    assert handler.sender_email == email_credentials["sender_email"]
    assert handler.sender_password == email_credentials["sender_password"]

@patch('src.email_handler.smtplib.SMTP')
def test_send_email_success(mock_smtp, email_handler):
    email_handler.send("Hello", "recipient@example.com")
    mock_smtp.assert_called_with("smtp.gmail.com", 587)
    mock_smtp.return_value.starttls.assert_called()
    mock_smtp.return_value.login.assert_called_with(email_handler.sender_email, email_handler.sender_password)
    mock_smtp.return_value.sendmail.assert_called()

@patch('src.email_handler.smtplib.SMTP')
def test_send_email_exception(mock_smtp, email_handler):
    mock_smtp.return_value.sendmail.side_effect = Exception("SMTP Error")
    with patch('src.email_handler.logger') as mock_logger:
        email_handler.send("Hello", "recipient@example.com")
        mock_logger.exception.assert_called_with("Error occurred while sending email: SMTP Error")
