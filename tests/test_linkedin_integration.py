# test_linkedin_integration.py

import profile

import pytest

from src.linkedin_handler import LinkedInConnectorClass


@pytest.fixture(scope="module")
def connector():
    """
    Pytest fixture to create an instance of LinkedInConnectorClass.
    The class automatically handles login during initialization.
    """
    driver_path = "chromedriver/chromedriver"
    test_username = "sandeeppvn2@gmail.com"  # Use a test account
    test_password = ".iB6EXxA.n"             # Use a test account
    connector = LinkedInConnectorClass(driver_path, test_username, test_password)
    
    yield connector
    connector.close_browser()

@pytest.mark.parametrize("profile_url, note", [
    (
        "https://www.linkedin.com/in/sandeeppvn/",
        "Test note"
    )
])
def test_send_connection_request_success(connector, profile_url, note):
    """
    Test if the send_connection_request method successfully navigates to a profile 
    and sends a connection request.
    """
    connector.send_connection_request(profile_url, note)
    # Add assertions to verify the request was sent
    # Note: Actual verification might be complex due to the nature of the operation
