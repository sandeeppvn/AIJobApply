import os
import requests
from dotenv import load_dotenv, find_dotenv

class Notion:
    def __init__(self):
        # Load the .env file
        load_dotenv(find_dotenv())

        # Get the Notion API credentials from environment variables
        self.notion_url = str(os.getenv('NOTION_URL'))
        self.secret_key = str(os.getenv('NOTION_SECRET_KEY'))
        self.contacts_id = str(os.getenv('NOTION_CONTACTS_ID'))
        self.jobs_id = str(os.getenv('NOTION_JOBS_ID'))

        # Set the headers
        self.headers = {
            'Authorization': 'Bearer ' + self.secret_key,
            'Content-Type': 'application/json',
            'Notion-Version': '2021-05-13'
        }

    def get_pages(self, database_id:str, filter:dict) -> dict:
        '''
        Description: Query a Notion database
        Input: database_id (str), filter (dict)
        Output: A dictionary of the results
        '''

        # Set the database url
        database_url = self.notion_url + 'databases/' + database_id + '/query'

        # Send the request
        response = requests.request("POST", database_url, headers=self.headers, json=filter)

        # Get the response as json
        response = response.json()

        # Get the results
        results = response['results']

        return results
    
    def create_pages(self, database_id:str, properties:dict) -> dict:
        '''
        Description: Create one or more records in a Notion database
        Input: database_id (str), properties (dict)
        Output: A dictionary of the results
        '''

        # Set the database url
        database_url = self.notion_url + 'pages/'

        # Set the data
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }

        # Send the request
        response = requests.request("POST", database_url, headers=self.headers, json=payload)

        # Get the response as json
        response = response.json()

        return response
    
    def update_pages(self, record_id:str, properties:dict, parent=None) -> dict:
        '''
        Description: Update a record in a Notion database
        Input: database_id (str), record_id (str), properties (dict)
        Output: A dictionary of the results
        '''

        # Set the url
        url = self.notion_url + "pages/" + record_id

        payload = {
            "properties": properties
        }
        
        if parent:
            payload["parent"] = parent

        # Send the request
        response = requests.request("PATCH", url, headers=self.headers, json=payload)

        # Get the response as json
        response = response.json()

        return response
