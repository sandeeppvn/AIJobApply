

import json
import os.path
from pathlib import Path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials


class GoogleAPIClass:
    def __init__(self, credentials_file_path: str, use_service_account: bool = True):
        """
        Initialize GoogleSheets object and establish connection with Google Sheets.
        """

        if not credentials_file_path.endswith(".json"):
            raise ValueError("Credentials file path must be a .json file.")
        
        credentials_file = Path(credentials_file_path)
        if not credentials_file.is_file():
            raise FileNotFoundError("Credentials file not found.")
        
        SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file']
        self.authenticate_service_account(credentials_file,SCOPES) if use_service_account else self.authenticate_user_account(credentials_file, SCOPES)

    def authenticate_service_account(self, credentials_file: Path, SCOPES: list):
        """
        Authenticate service account credentials for OAuth2
        """
        # Authenticate service account for Google Drive API
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scopes=SCOPES) # type: ignore
        self.google_drive_service = build('drive', 'v3', credentials=credentials)

        # Authenticate service account for GSpread API
        self.gspread_service = gspread.service_account(credentials_file)

    def authenticate_user_account(self, credentials_file: Path, SCOPES: list):
        """
        Authenticate user account credentials for OAuth2
        """
        # Authenticate user account for Google Drive API
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/google_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.google_drive_service = build('drive', 'v3', credentials=creds)

        with open(credentials_file) as f:
            creds = json.load(f)
        # Authenticate user account for GSpread API
        self.gspread_service, authorized_user = gspread.oauth_from_dict(creds)


    def get_gsheet(self, gsheet_name: str):
        """
        Get Google Sheet by name
        """
        # Get the spreadsheet by name
        gsheet = self.gspread_service.open(gsheet_name)

        return gsheet
    
    def create_folder(self, folder_name: str):
        """
        Create a folder in Google Drive
        """
        # Create a folder in Google Drive
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # Create the folder if it doesn't exist
        folder = self.google_drive_service.files().create(body=file_metadata, fields='id').execute()

        return folder.get('id')
    
    def upload_file(self, content: str, file_name: str, folder_id: str):
        """
        Create a temporary file and upload it to Google Drive
        """
        try:
            # Create a temporary file
            with open(file_name, 'w') as f:
                f.write(content)

            # Upload the file to Google Drive
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_name)
            file = self.google_drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        except errors.HttpError as e:
            print(f"Error uploading file to Google Drive: {e}")

        finally:
            if os.path.exists(file_name):
                # Delete the temporary file
                os.remove(file_name)


        