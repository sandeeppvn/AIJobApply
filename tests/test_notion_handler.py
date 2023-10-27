
import pytest
from src.notion_handler import Notion

# Mocking dependencies for the Notion class
@pytest.fixture
def mock_requests(mocker):
    return mocker.patch('src.notion_handler.requests', autospec=True)

@pytest.fixture
def notion(mock_requests):
    return Notion()

def test_get_pages(notion, mock_requests):
    # Mock data
    database_id = "database123"
    filter = {"status": "Saved"}
    mock_response = {"results": [{"id": "1", "status": "Saved"}]}
    
    # Mock behavior
    mock_requests.post.return_value.json.return_value = mock_response
    
    # Call the method
    result = notion.get_pages(database_id, filter)
    
    # Assert the expected behavior
    assert len(result) == 1
    assert result[0]["id"] == "1"

# Add more tests for other methods of Notion class...

