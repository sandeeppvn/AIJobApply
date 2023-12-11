from unittest.mock import MagicMock, patch

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from src.linkedin_handler import LinkedInConnectorClass


# Mocking Selenium WebDriver and WebDriverWait
@pytest.fixture
def mock_webdriver():
    with patch('selenium.webdriver.Chrome') as mock_driver:
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance
        mock_wait = MagicMock()
        mock_driver_instance.wait = mock_wait
        yield mock_driver_instance, mock_wait

def test_linkedin_connector_initialization(mock_webdriver):
    driver, wait = mock_webdriver
    linkedin_connector = LinkedInConnectorClass("/path/to/driver", "username", "password")

    driver.get.assert_called_with('https://www.linkedin.com/login')
    # Add more assertions to check if username and password are entered, and the login button is clicked

def test_send_connection_request(mock_webdriver):
    driver, wait = mock_webdriver
    linkedin_connector = LinkedInConnectorClass("/path/to/driver", "username", "password")

    # Setup mock elements for connect button, note field, and send button
    connect_button = MagicMock()
    note_field = MagicMock()
    send_button = MagicMock()
    wait.until.side_effect = [connect_button, note_field, send_button]

    linkedin_connector.send_connection_request("https://www.linkedin.com/in/example", "Note")

    connect_button.click.assert_called_once()
    note_field.send_keys.assert_called_once_with("Note")
    send_button.click.assert_called_once()

def test_close_browser(mock_webdriver):
    driver, _ = mock_webdriver
    linkedin_connector = LinkedInConnectorClass("/path/to/driver", "username", "password")
    
    linkedin_connector.close_browser()
    driver.quit.assert_called_once()
