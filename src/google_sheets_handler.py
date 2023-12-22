from pathlib import Path
from typing import Optional

import gspread
import pandas as pd
from gspread.exceptions import SpreadsheetNotFound


class GoogleSheetsHandler:
    def __init__(self, credentials_file_path: str):
        """
        Initialize GoogleSheets object and establish connection with Google Sheets.
        Parameters
        ----------
        credentials_file_path : str
            Path to the credentials file for Google API.
        gsheet_name : str
            Name of the Google Sheet to read jobs from.
        """

        if not credentials_file_path.endswith(".json"):
            raise ValueError("Credentials file path must be a .json file.")
        
        credentials_file = Path(credentials_file_path)
        if not credentials_file.is_file():
            raise FileNotFoundError("Credentials file not found. Path provided: " + credentials_file_path)
        
        self.gc = gspread.service_account(filename=credentials_file)


    def get_gsheet(self, gsheet_name: str = "AIJobApply") -> gspread.Spreadsheet:
        """
        Get Google Sheet by name
        """
        try:
            return self.gc.open(gsheet_name)
        except SpreadsheetNotFound:
            raise ValueError(f"Google Sheet with name '{gsheet_name}' not found.")
        except Exception as e:
            raise ValueError(f"Error while getting Google Sheet: {str(e)}")
        
    def update_gsheet_from_dataframe(self, dataframe: pd.DataFrame, gsheet_name: str):
        """
        Update Google Sheet with the given dataframe
        Parameters
        ----------
        dataframe : pd.DataFrame
            Dataframe to update Google Sheet with.
        """
        try:
            gsheet = self.get_gsheet(gsheet_name)
            gsheet.sheet1.clear()
            gsheet.sheet1.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        except Exception as e:
            raise ValueError(f"Error while updating Google Sheet: {str(e)}")
        
        