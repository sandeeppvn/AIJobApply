
import pytest
from src.email_handler import EmailHandler

# Mocking dependencies for the EmailHandler class
@pytest.fixture
def mock_utils(mocker):
    return mocker.patch('src.email_handler.utils', autospec=True)

@pytest.fixture
def email_handler(mock_utils):
    return EmailHandler()

def test_send(email_handler, mock_utils):
    # Mock data
    content = "Test Content"
    email = "test@example.com"
    subject = "Test Subject"
    
    # Call the method
    email_handler.send(content, email, subject)
    
    # Assert the expected behavior
    mock_utils.send_email.assert_called_once_with(content, email, subject)

# Add more tests for other methods of EmailHandler class if there are any...

