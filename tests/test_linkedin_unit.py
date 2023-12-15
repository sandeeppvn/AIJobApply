from unittest.mock import Mock, patch

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.linkedin_handler import LinkedInConnectorClass


class TestLinkedInConnectorUnit:
    @pytest.fixture(scope="class")
    def mock_connector(self):
        with patch('selenium.webdriver.Chrome') as MockWebDriver:
            mock_driver = Mock()

            # Mock WebDriver
            mock_driver.maximize_window = Mock()
            mock_driver.get = Mock()
            mock_driver.quit = Mock()
            mock_driver.find_element = Mock()

            mock_elements = {
                'username': Mock(),
                'password': Mock(),
                "//button[@type='submit']": Mock(),
                "//button[contains(text(), 'Connect')]": Mock(),
                "//button[@aria-label='Add a note']": Mock(),
                "//button[@aria-label='Send now']": Mock(),
                'custom-message': Mock()
            }

            # Add send_keys method to the mock elements for text entry
            for element in mock_elements.values():
                element.send_keys = Mock()

            # Mock find_element
            def find_element_effect(by, locator):
                if locator in mock_elements:
                    return mock_elements[locator]
                else:
                    raise NoSuchElementException
                
            mock_driver.find_element.side_effect = find_element_effect

            # Mock WebDriverWait
            mock_wait = Mock()
            def mock_until(condition):
                if 'presence_of_element_located' in str(condition):
                    # Return a single mock element for presence_of_element_located
                    return next(iter(mock_elements.values()))
                else:
                    # Return a list of mock elements for other conditions
                    return list(mock_elements.values())
            mock_wait.until.side_effect = mock_until



            mock_driver.wait = mock_wait

            MockWebDriver.return_value = mock_driver

            with patch('src.linkedin_handler.LinkedInConnectorClass.__init__', return_value=None):
                connector = LinkedInConnectorClass("path/to/chromedriver")
                connector.driver = mock_driver
                connector.wait = mock_wait
                yield connector

    @pytest.mark.parametrize("username, password", [
        ("test_username", "test_password"),
        ("another_user", "another_pass")
    ])
    def test_login(self, mock_connector, username, password):
        mock_connector.login(username, password)

        # Assert that the necessary elements are interacted with
        mock_connector.driver.find_element.assert_called_with(By.ID, 'username')
        mock_connector.driver.find_element.assert_called_with(By.ID, 'password')
        mock_connector.driver.find_element.assert_called_with(By.XPATH, "//button[@type='submit']")

    @pytest.mark.parametrize("profile_url, note", [
        ("https://www.linkedin.com/in/example1", "Hi, this is a test connection request."),
        ("https://www.linkedin.com/in/example-name-1234", "Hello, let's connect on LinkedIn.")
    ])
    def test_send_connection_request(self, mock_connector, profile_url, note):
        mock_connector.send_connection_request(profile_url, note)

        # Assert that the profile page is navigated to
        mock_connector.driver.get.assert_called_with(profile_url)

        # Assert interactions with elements for sending a connection request
        mock_connector.driver.find_element.assert_any_call(By.XPATH, "//button[contains(text(), 'Connect')]")
        mock_connector.driver.find_element.assert_any_call(By.XPATH, "//button[@aria-label='Add a note']")
        mock_connector.driver.find_element.assert_any_call(By.ID, 'custom-message')
        mock_connector.driver.find_element.assert_any_call(By.XPATH, "//button[@aria-label='Send now']")

