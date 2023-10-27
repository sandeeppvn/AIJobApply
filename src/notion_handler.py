import logging
import os
import time

import requests
from dotenv import find_dotenv, load_dotenv

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13",  # Consider updating this from configuration if frequently changed
}


class NotionAPIError(Exception):
    """Exception raised for errors in the Notion API calls."""

    def __init__(self, message="Error occurred while interacting with the Notion API"):
        super().__init__(message)


class Notion:
    def __init__(self):
        """
        Initialize Notion object and load environment variables.
        """
        load_dotenv(find_dotenv())
        self.notion_url = self.api_key = str(os.getenv("NOTION_URL"))
        self.headers = {**HEADERS, "Authorization": f"Bearer {os.getenv('NOTION_SECRET_KEY')}"}
        self.contacts_id = str(os.getenv("NOTION_CONTACTS_ID"))
        self.jobs_id = str(os.getenv("NOTION_JOBS_ID"))

    def create_payload(self, filter: dict) -> dict:
        """
        Construct a payload for the Notion API based on a given filter.

        Args:
        - filter (dict): Filter criteria for querying the Notion database.

        Returns:
        - dict: Constructed payload.
        """

        def construct_filter(key, value):
            """Helper function to construct the filter."""
            if isinstance(value, list):
                return {key: {"or": [construct_filter(key, item) for item in value]}}
            elif isinstance(value, dict):
                return {key: {"and": [construct_filter(sub_key, sub_value) for sub_key, sub_value in value.items()]}}
            else:
                return {key: {"equals": value}}

        if not isinstance(filter, dict):
            raise ValueError("The filter must be a dictionary.")

        filters = [construct_filter(key, value) for key, value in filter.items()]
        return {"filter": {"and": filters}} if len(filters) > 1 else {"filter": filters[0]}

    def _send_request(self, method, endpoint, json_data):
        """
        Send requests to the Notion API and handle responses.

        Args:
        - method (str): HTTP method for the request.
        - endpoint (str): API endpoint to be accessed.
        - json_data (dict): Payload for the request.

        Returns:
        - dict: Parsed JSON data from the API response.

        Raises:
        - NotionAPIError: If the API returns an error.
        """
        url = self.notion_url + endpoint
        response = requests.request(method, url, headers=self.headers, json=json_data)
        response_data = response.json()

        if response.status_code != 200:
            logger.error(f"Error with Notion API: {response_data.get('message')}")
            raise NotionAPIError(response_data.get("message"))

        return response_data

    def get_pages(self, database_id: str, filter: dict) -> dict:
        """
        Query a Notion database based on a given filter.

        Args:
        - database_id (str): ID of the Notion database.
        - filter (dict): Filter criteria for querying.

        Returns:
        - dict: Result of the query.
        """
        payload = self.create_payload(filter)
        endpoint = f"databases/{database_id}/query"
        return self._send_request("POST", endpoint, payload)

    def create_pages(self, database_id: str, properties: dict) -> dict:
        """
        Create records in a Notion database.

        Args:
        - database_id (str): ID of the Notion database.
        - properties (dict): Properties for the new record.

        Returns:
        - dict: Created record data.
        """
        payload = {"parent": {"database_id": database_id}, "properties": properties}
        return self._send_request("POST", "pages/", payload)

    def update_page(self, record_id: str, properties: dict, parent=None) -> dict:
        """
        Update a page in a Notion database.

        Args:
        - record_id (str): ID of the record to update.
        - properties (dict): Updated properties for the record.
        - parent (dict, optional): Updated parent information, if applicable.

        Returns:
        - dict: Updated record data.
        """
        payload = {"properties": properties}
        if parent:
            payload["parent"] = parent
        endpoint = f"pages/{record_id}"
        return self._send_request("PATCH", endpoint, payload)

    def update_jobs(self, jobs_to_update: list) -> None:
        """
        Update jobs in the Notion database, handling rate limiting.

        Args:
        - jobs_to_update (list): List of jobs with properties to update.
        """
        for job in jobs_to_update:
            self.update_page(record_id=job["id"], properties=job["properties"])
            # TODO: Replace with a better rate-limiting strategy like exponential backoff
            time.sleep(0.5)
