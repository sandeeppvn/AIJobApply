import logging
import os
from typing import Optional

import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.email_handler import EmailHandler
from src.google_api_handler import GoogleAPIClass
from src.openai_handler import Openai

logger = logging.getLogger(__name__)


class JobProcessor:
    def __init__(
        self,
        templates_path: str = "templates",
        gmail: Optional[str] = None,
        password: Optional[str] = None,
        credentials_file: Optional[str] = None,
        openapi_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize a JobProcessor instance with required handlers and credentials.
        """
        load_dotenv(find_dotenv())
        self.jobs_df = pd.DataFrame()
        self.templates_path = templates_path
        self.gmail = gmail or os.getenv("GMAIL_ADDRESS")
        self.password = password or os.getenv("GMAIL_PASSWORD")
        self.credentials_file = credentials_file or os.getenv("GOOGLE_API_CREDENTIALS_FILE")
        self.openapi_key = openapi_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL")

        self._validate_credentials()

        self.google_api_handler = GoogleAPIClass(self.credentials_file) # type: ignore
        self.openai = Openai(self.openapi_key, self.model) # type: ignore
        self.email_handler = EmailHandler(self.gmail, self.password) # type: ignore

    def _validate_credentials(self):
        """
        Validate required credentials.
        """
        if not all([self.gmail, self.password, self.credentials_file, self.openapi_key, self.model, self.templates_path]):
            raise ValueError(
                "One or more of the required credentials is missing. Please check the .env file or the CLI arguments."
            )

    def _get_gsheet_name(self, gsheet_name: Optional[str]) -> str:
        """
        Get the Google Sheet name from the parameter or environment variables.
        """
        if not gsheet_name:
            load_dotenv(find_dotenv())
            gsheet_name = os.getenv("GOOGLE_SHEET_NAME")
            if not gsheet_name:
                raise ValueError(
                    "gsheet_name is not provided and GOOGLE_SHEET_NAME is not set in environment variables."
                )
        return gsheet_name

    def process_jobs(self, gsheet_name: Optional[str] = None):
        """
        Main function to process jobs based on their status.
        """
        try:
            logger.info("Processing jobs...")
            self.jobs_df = self.get_all_jobs(gsheet_name)
            logger.info(f"Found {len(self.jobs_df)} total jobs to process")

            logger.info("Processing new jobs...")
            self.process_new_jobs()

            logger.info("Processing email ready jobs...")
            self.process_email_ready_jobs()

            logger.info("Processing email approved jobs...")
            self.process_email_approved_jobs()

            logger.info("Updating Google Sheet...")
            self.update_dataframe_to_gsheet(gsheet_name)

            logger.info("Creating drive files...")
            self.create_drive_files()

            logger.info("Job processing complete.")
        except Exception as e:
            logger.error(f"Error while processing jobs: {str(e)}")
            raise

    def get_all_jobs(self, gsheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Get all jobs from the Google Sheet.
        """
        gsheet_name = self._get_gsheet_name(gsheet_name)
        gsheet = self.google_api_handler.get_gsheet(gsheet_name)
        return pd.DataFrame(gsheet.sheet1.get_all_records())

    def process_new_jobs(self):
        """
        Process jobs with "New Job" or "Email Required" status.
        """
        for status in ['New Job', 'Email Required']:
            self._process_jobs_with_status(status)

    def _process_jobs_with_status(self, status: str):
        """
        Process jobs with a given status.
        """
        # Create a copy of the jobs_df DataFrame
        jobs_df = self.jobs_df[self.jobs_df['Status'] == status].copy()
        if jobs_df.empty:
            return

        has_email = has_email = jobs_df['Email'].str.strip() != ""
        jobs_df.loc[has_email, 'Status'] = 'Email Ready'

        has_contact_details = (jobs_df['Contact Details'].str.strip() != "") & ~has_email
        found_emails = jobs_df.loc[has_contact_details, 'Contact Details'].apply(self.openai.find_email)
        jobs_df.loc[has_contact_details, 'Email'] = found_emails

        jobs_df.loc[has_contact_details & (found_emails.str.strip() != ""), 'Status'] = 'Email Ready'
        jobs_df.loc[has_contact_details & (found_emails.str.strip() == ""), 'Status'] = 'Email Required'
        jobs_df.loc[~has_email & ~has_contact_details, 'Status'] = 'Email Required'

        self.jobs_df.update(jobs_df)

    def process_email_ready_jobs(self):
        """
        Process jobs with "Email Ready" status.
        """
        jobs_df = self.jobs_df[self.jobs_df['Status'] == 'Email Ready'].copy()
        if jobs_df.empty:
            return

        jobs_df.apply(self.openai.generate_custom_contents, axis=1)
        jobs_df['Status'] = 'Email Approval Required'
        self.jobs_df.update(jobs_df)

    def process_email_approved_jobs(self):
        """
        Process jobs with "Email Approval Required" status.
        """
        jobs_df = self.jobs_df[self.jobs_df['Status'] == 'Email Approval Required'].copy()
        if jobs_df.empty:
            return

        successful_indices = []
        for index, row in jobs_df.iterrows():
            try:
                self.email_handler.send(
                    content=row['Email Content'],
                    recepient_email=row['Email'],
                    subject=row['Email Subject Line'],
                )
                successful_indices.append(index)
            except Exception as e:
                logger.warning(f"Failed to send email for job at index {index}. Error: {str(e)}")

        jobs_df.loc[successful_indices, 'Status'] = 'Email Sent'
        self.jobs_df.update(jobs_df)

    def update_dataframe_to_gsheet(self, gsheet_name: Optional[str] = None):
        """
        Update the jobs_df DataFrame to the Google Sheet.
        """
        gsheet_name = self._get_gsheet_name(gsheet_name)
        if self.jobs_df.empty:
            return

        gsheet = self.google_api_handler.get_gsheet(gsheet_name)
        try:
            gsheet.sheet1.update([self.jobs_df.columns.values.tolist()] + self.jobs_df.values.tolist())
        except Exception as e:
            logger.error(f"Failed to update Google Sheet. Error: {str(e)}")

    def create_drive_files(self):
        """
        For each job, create a folder in Google Drive and upload the resume and cover letter and email content.
        """
        jobs_df = self.jobs_df[
            (self.jobs_df['Email Content'] != '') & 
            (self.jobs_df['Resume'] != '') &
            (self.jobs_df['Cover Letter'] != '')
        ].copy()

        if jobs_df.empty:
            return

        # For each job, create a folder in Google Drive and upload the resume and cover letter and email content
        jobs_df.apply(self.create_drive_files_for_job, axis=1)

    def create_drive_files_for_job(self, row) -> pd.Series:
        """
        Create a folder in Google Drive and upload the resume and cover letter and email content for a job.
        Parameters:
        - row (Series): Pandas Series containing the details of a job.
        Returns:
        - Series: Pandas Series containing the details of the job.
        """
        folder_name = row['Company Name'] + " - " + row['Position']
        folder_id = self.google_api_handler.create_folder(folder_name)

        self.google_api_handler.upload_file(row['Resume'], folder_id, "resume.docx")
        self.google_api_handler.upload_file(row['Cover Letter'], folder_id, "cover_letter.docx")
        self.google_api_handler.upload_file(row['Email Content'], folder_id, "email.docx")

        return row