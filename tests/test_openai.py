from unittest.mock import MagicMock, patch

import pytest

from src.openai_handler import OpenAIConnectorClass


@pytest.fixture
def openai_connector():
    return OpenAIConnectorClass('api_key', 'model')

@patch('src.openai_handler.openai.ChatCompletion.create')
@patch('src.openai_handler.openai.Completion.create')
def test_query_prompt(mock_completion_create, mock_chat_completion_create, openai_connector):
    # Mock response for the OpenAI API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = {"content": "test response"}

    mock_chat_completion_create.return_value = mock_response
    mock_completion_create.return_value = mock_response

    # Test with function description
    response = openai_connector.query_prompt("test prompt", [{"function_name": "test_function"}])
    assert response == "test response"
    mock_chat_completion_create.assert_called_once()

    # Test without function description
    response = openai_connector.query_prompt("test prompt")
    assert response == "test response"
    mock_completion_create.assert_called_once()

def test_generate_custom_contents(openai_connector):
    # Assuming load_templates and load_prompt return specific values, mock these functions
    with patch('src.utils.load_templates', return_value={"cover_letter": "cover_letter", "resume": "resume", "message_content": "message_content", "message_subject_line": "message_subject_line", "linkedin_note": "linkedin_note"}), \
         patch('src.utils..load_prompt', return_value="test prompt"):
        response = openai_connector.generate_custom_contents({"Description": "desc", "Position": "pos", "Company Name": "company", "Link": "link", "Name": "name"})
        # Add assertions based on expected behavior

def test_generate_custom_contents_helper(openai_connector):
    response = openai_connector.generate_custom_contents_helper("cover_letter", "resume", "message_content", "updated_job_description", "message_subject_line", "linkedin_note")
    expected_response = {
        "Cover Letter": "cover_letter",
        "Resume": "resume",
        "Message Content": "message_content",
        "Description": "updated_job_description",
        "Message Subject": "message_subject_line",
        "LinkedIn Note": "linkedin_note"
    }
    assert response == expected_response
