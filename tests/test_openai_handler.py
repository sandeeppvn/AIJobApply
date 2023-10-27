import pytest

from src.openai_handler import Openai


# Mocking dependencies for the Openai class
@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("src.openai_handler.openai", autospec=True)


@pytest.fixture
def openai_handler(mock_openai):
    return Openai()


def test_query_prompt(openai_handler, mock_openai):
    # Mock data
    prompt = "Test Prompt"
    mock_response = {"choices": [{"text": "Test Response"}]}

    # Mock behavior
    mock_openai.Completion.create.return_value = mock_response

    # Call the method
    result = openai_handler.query_prompt(prompt)

    # Assert the expected behavior
    assert result == "Test Response"


# Add more tests for other methods of Openai class...
