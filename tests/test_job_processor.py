import pytest

from src.email_handler import EmailHandler
from src.job_processor import JobProcessor
from src.notion_handler import Notion
from src.openai_handler import Openai


# Mocking dependencies for the JobProcessor class
@pytest.fixture
def mock_notion(mocker):
    return mocker.Mock(spec=Notion)


@pytest.fixture
def mock_openai(mocker):
    return mocker.Mock(spec=Openai)


@pytest.fixture
def mock_email_handler(mocker):
    return mocker.Mock(spec=EmailHandler)


@pytest.fixture
def job_processor(mock_notion, mock_openai, mock_email_handler, mocker):
    # Patch the instances created within the JobProcessor class to use our mocks
    mocker.patch.object(JobProcessor, "notion", mock_notion)
    mocker.patch.object(JobProcessor, "openai", mock_openai)
    mocker.patch.object(JobProcessor, "email_handler", mock_email_handler)

    return JobProcessor()


def test_filter_jobs_by_status(job_processor):
    # Mock data

    jobs = [{"status": "Saved"}, {"status": "Email Ready"}]
    status = "Saved"

    # Mock behavior
    job_processor.notion.get_pages.return_value = jobs

    # Call the method
    result = job_processor.filter_jobs_by_status(status)

    # Assert the expected behavior
    assert len(result) == 1
    assert result[0]["status"] == status


# Add more tests for other methods of JobProcessor class...
