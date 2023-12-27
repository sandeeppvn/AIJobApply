import os
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class GoogleDriveHandler:
    def __init__(self, credentials_file_path: str, folder_name: str = "Job Applications"):
        self.credentials_file_path = credentials_file_path
        self.service = self.authenticate()
        self.job_root_folder_id = self.get_folder(folder_name)

    def authenticate(self):
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file_path, scopes=scopes)
        service = build('drive', 'v3', credentials=credentials)
        return service

    def upload_file(self, file_name: str, file_path: str, parent_id: str) -> None:

        # Add the file to the parent folder
        file_metadata = {'name': file_name, 'parents': [parent_id]}
        media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('File ID: %s' % file.get('id'))
        
    def get_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Get the ID of a folder, creating it if it doesn't exist."""
        # Formulate the query based on whether a parent ID is provided
        if parent_id:
            query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        else:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"

        # Execute the query
        response = self.service.files().list(q=query, spaces='drive', fields='files(id)').execute()

        # Check if the folder exists
        folders = response.get('files', [])
        if folders:
            # Return the ID of the existing folder
            return folders[0].get('id')
        else:
            # Create the folder if it doesn't exist and return its ID
            return self.create_folder(folder_name, parent_id)

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Create a new folder."""
        # Create the folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        file = self.service.files().create(body=file_metadata, fields='id').execute()

        # Return the ID of the created folder
        return file.get('id')

