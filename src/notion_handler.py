import json
import logging
import time
from pprint import pprint
from urllib import response
from venv import create

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
    def __init__(self, notion_secret_key: str):
        """
        Initialize Notion object and load environment variables.
        """
        self.notion_url = self.api_key = "https://api.notion.com/v1/"
        self.headers = {**HEADERS, "Authorization": f"Bearer {notion_secret_key}"}

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

    def create_payload_for_query(self, **kwargs) -> dict:
        payload_dict = {
            "filter": {
                "property": kwargs["property_name"],
                kwargs["property_type"]: {kwargs["filter_operation"]: kwargs["property_value"]},
            }
        }

        return payload_dict

    def get_pages_by_filter(self, **kwargs) -> dict:
        """
        Query a Notion database based on a given filter.

        Args:
        - database_id (str): ID of the Notion database.
        - filter (dict): Filter criteria for querying.

        Returns:
        - dict: Result of the query.
        """
        payload = self.create_payload_for_query(**kwargs)
        endpoint = f"databases/{kwargs['database_id']}/query"
        response = self._send_request("POST", endpoint, payload)
        return response["results"]

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
        payload = self.create_payload_for_update(properties)
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

    def property_type_format(self, property_type: str, property_value: str) -> dict:
        """Helper function to create a property object."""
        if property_type == "rich_text":
            return {"rich_text": [{"text": {"content": property_value}}]}
        elif property_type == "title":
            return {"title": [{"text": {"content": property_value}}]}
        elif property_type == "select":
            return {"select": {"name": property_value}}
        elif property_type == "email":
            return {"email": property_value}
        else:
            raise ValueError(f"Invalid property type: {property_type}")

    def create_payload_for_update(self, properties: dict) -> dict:
        """
        Modify the payload for a Notion API request.

        Args:
        - properties (dict): Properties to be added to the payload.

        Returns:
        - dict: Modified payload.
        """
        selected_properties = {
            "Description": "rich_text",
            "Email": "rich_text",
            "Email Content": "rich_text",
            "Resume": "rich_text",
            "Cover Letter": "rich_text",
            "Contact Details": "rich_text",
            "Position": "select",
            "Company Name": "title",
            "Status": "select",
        }

        new_properties = {}
        for key, value in properties.items():
            if key in selected_properties:
                property_type = selected_properties[key]
                if value[property_type] and isinstance(value[property_type], dict) and value[property_type]["name"]:
                    new_properties[key] = self.property_type_format(property_type, value[property_type]["name"])
                elif (
                    value[property_type]
                    and isinstance(value[property_type], list)
                    and value[property_type][0]["text"]["content"]
                ):
                    new_properties[key] = self.property_type_format(
                        property_type, value[property_type][0]["text"]["content"]
                    )

        return {"properties": new_properties}
