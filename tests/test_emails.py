from unittest.mock import ANY, MagicMock, patch

import pytest

from src.email_handler import \
    EmailHandler  # Adjusted to import from your module


@pytest.fixture
def email_handler():
    return EmailHandler("test@example.com", "password")

def test_initialization(email_handler):
    assert email_handler.sender_email == "test@example.com"
    assert email_handler.sender_password == "password"

@patch("src.email_handler.smtplib.SMTP")
def test_send_email_success(mock_smtp, email_handler):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    email_handler.send("Test content", "recipient@example.com", "Test Subject")
    
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@example.com", "password")
    mock_server.sendmail.assert_called_once()
    # Add any other assertions you deem necessary


@patch("src.email_handler.smtplib.SMTP")
@patch("src.email_handler.logger")
def test_send_email_exception(mock_logger, mock_smtp, email_handler):
    mock_server = MagicMock()
    mock_server.sendmail.side_effect = Exception("Test exception")
    mock_smtp.return_value.__enter__.return_value = mock_server

    email_handler.send("Test content", "recipient@example.com", "Test Subject")

    mock_logger.exception.assert_called_once_with(ANY)