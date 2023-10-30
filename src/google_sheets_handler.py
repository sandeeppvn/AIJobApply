

from pathlib import Path

import gspread


class GoogleSheets:
    def __init__(self, credentials_file_path: str):
        """
        Initialize GoogleSheets object and establish connection with Google Sheets.
        """

        if not credentials_file_path.endswith(".json"):
            raise ValueError("Credentials file path must be a .json file.")
        
        # Check if credentials file exists
        credentials_file = Path(credentials_file_path)
        if not credentials_file.is_file():
            raise FileNotFoundError("Credentials file not found.")
        
        # Provide the path to the credentials file to oauth
        self.gc = gspread.service_account(filename=credentials_file)

    def get_sheet(self, sheet_name: str):
        """
        Get Google Sheet object.
        """
        return self.gc.open(sheet_name)




