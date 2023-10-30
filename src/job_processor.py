import logging
import os
from typing import Optional

import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.email_handler import EmailHandler
from src.google_sheets_handler import GoogleSheets
from src.openai_handler import Openai

# from src.notion_handler import Notion


logger = logging.getLogger(__name__)


class JobProcessor:
    def __init__(
        self,
        templates_path: str = "templates",
        gmail: Optional[str] = None,
        password: Optional[str] = None,
        # notion_secret_key: Optional[str] = None,
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

        # Exception handling
        if not self.gmail or not self.password or not self.credentials_file or not self.openapi_key or not self.model or self.templates_path is None:
            raise ValueError(
                "One or more of the required credentials is missing. Please check the .env file or the CLI arguments."
            )

        self.gc = GoogleSheets(self.credentials_file)
        self.openai = Openai(self.openapi_key, self.model)
        self.email_handler = EmailHandler(self.gmail, self.password)

    def process_jobs(self, gsheet_name: Optional[str] = None):
        """
        Main function to process jobs based on their status.
        Parameters:
        - gsheet_name (str): Name of the Google Sheet. If not specified, details from the .env file will be used.
        """

        self.jobs_df = self.get_all_jobs(gsheet_name)

        self.process_new_jobs()
        self.process_email_ready_jobs()
        self.process_email_approved_jobs()

        self.update_dataframe_to_gsheet(gsheet_name)

    def get_all_jobs(self, gsheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Get all jobs from the Google Sheet.
        Parameters:
        - gsheet_name (str): Name of the Google Sheet. If not specified, details from the .env file will be used.
        Returns:
        - DataFrame: Pandas DataFrame containing all the jobs.
        """
        if not gsheet_name:
            load_dotenv(find_dotenv())
            gsheet_name = os.getenv("GOOGLE_SHEET_NAME")
            if gsheet_name is None:
                raise ValueError(
                    "gsheet_name is not provided and GOOGLE_SHEET_NAME is not set in environment variables."
                )
            
        gsheet = self.gc.get_sheet(gsheet_name)
        return pd.DataFrame(gsheet.sheet1.get_all_records())

    def process_new_jobs(self):
        """
        Process jobs with "New Job" status.
       
        Description:
        - Filter jobs by "New Job" status.
        - If the job has an email, update the status to "Email Ready".
        - Else, if the job has contact details, use OpenAI to find the email.
        - If the email is found, update the status to "Email Ready".
        - Else, update the status to "Email required".
        """
        
        # Create a copy of the jobs_df DataFrame
        new_jobs_df = self.jobs_df.copy()
        
        # Filter out jobs with "New Job" status
        new_jobs_df = new_jobs_df[new_jobs_df['Status'] == 'New Job']

        # Identify jobs with emails and update their status
        has_email = new_jobs_df['Email'].notnull()
        new_jobs_df.loc[has_email, 'status'] = 'Email Ready'

        # For jobs without emails but with contact details
        has_contact_details = new_jobs_df['Contact Details'].notnull() & ~has_email

        found_emails = new_jobs_df.loc[has_contact_details, 'Contact Details'].apply(self.openai.find_email)
        new_jobs_df.loc[has_contact_details, 'Email'] = found_emails

        # Update the status of jobs accordingly
        new_jobs_df.loc[has_contact_details & found_emails.notnull(), 'Status'] = 'Email Ready'
        new_jobs_df.loc[has_contact_details & found_emails.isnull(), 'Status'] = 'Email Required'

        # If job has no email or contact details, update the status to "Email Required"
        new_jobs_df.loc[~has_email & ~has_contact_details, 'Status'] = 'Email Required'

        # Update the jobs_df DataFrame in-place
        self.jobs_df.update(new_jobs_df)

        """
        Process jobs with "Email Required" status.
       
        Description:
        - Filter jobs by "Email Required" status.
        - If the job has an email, update the status to "Email Ready".
        - Else, if the job has contact details, use OpenAI to find the email.
        - If the email is found, update the status to "Email Ready".
        - Else, update the status to "Email required".
        """
        
        # Create a copy of the jobs_df DataFrame
        email_required_jobs_df = self.jobs_df.copy()
        
        # Filter out jobs with "Email Required" status
        email_required_jobs_df = email_required_jobs_df[email_required_jobs_df['Status'] == 'Email Required']

        # Identify jobs with emails and update their status
        has_email = email_required_jobs_df['Email'].notnull()
        email_required_jobs_df.loc[has_email, 'status'] = 'Email Ready'

        # For jobs without emails but with contact details
        has_contact_details = email_required_jobs_df['Contact Details'].notnull() & ~has_email

        found_emails = email_required_jobs_df.loc[has_contact_details, 'Contact Details'].apply(self.openai.find_email)
        email_required_jobs_df.loc[has_contact_details, 'Email'] = found_emails

        # Update the status of jobs accordingly
        email_required_jobs_df.loc[has_contact_details & found_emails.notnull(), 'Status'] = 'Email Ready'
        email_required_jobs_df.loc[has_contact_details & found_emails.isnull(), 'Status'] = 'Email Required'

        # Update the jobs_df DataFrame in-place
        self.jobs_df.update(email_required_jobs_df)

    def process_email_ready_jobs(self):
        """
        Process jobs with "Email Ready" status.
       
        Description:
        - Filter jobs by "Email Ready" status.
        - Use OpenAI to generate email content, cover letter, resume, description and email subject line.
        - Update the status of jobs to "Email Approval Required".
        """
        
        # Create a copy of the jobs_df DataFrame
        email_ready_jobs_df = self.jobs_df.copy()
        
        # Filter out jobs with "Email Ready" status
        email_ready_jobs_df = email_ready_jobs_df[email_ready_jobs_df['Status'] == 'Email Ready']

        # Generate email content, cover letter, resume, description and email subject line using OpenAI.
        email_ready_jobs_df.apply(
            lambda row: self.openai.generate_custom_contents(
                raw_job_description=row['Description'],
                position=row['Position'],
                company_name=row['Company Name'],
                job_link=row['Link'],
                contact_details=row['Contact Details'],
            ), 
            axis=1,
        )

        # Update the status of jobs to "Email Approval Required"
        email_ready_jobs_df['Status'] = 'Email Approval Required'

        # Update the jobs_df DataFrame in-place
        self.jobs_df.update(email_ready_jobs_df)

    def process_email_approved_jobs(self):
        """
        Process jobs with "Email Approval Required" status.
       
        Description:
        - Filter jobs by "Email Approval Required" status.
        - Send email to the contact.
        - Update the status of jobs to "Email Sent".
        """
        
        # Create a copy of the jobs_df DataFrame
        email_approved_jobs_df = self.jobs_df.copy()
        
        # Filter out jobs with "Email Approval Required" status
        email_approved_jobs_df = email_approved_jobs_df[email_approved_jobs_df['Status'] == 'Email Approval Required']

        # For each job, send email to the contact
        for index, row in email_approved_jobs_df.iterrows():
            self.email_handler.send(
                content=row['Email Content'],
                recepient_email=row['Email'],
                subject=row['Email Subject Line'],
            )

        # Update the status of jobs to "Email Sent"
        email_approved_jobs_df['Status'] = 'Email Sent'

        # Update the jobs_df DataFrame in-place
        self.jobs_df.update(email_approved_jobs_df)

    def update_dataframe_to_gsheet(self, gsheet_name: Optional[str] = None):
        """
        Update the jobs_df DataFrame to the Google Sheet.
        Parameters:
        - gsheet_name (str): Name of the Google Sheet. If not specified, details from the .env file will be used.
        """
        if not gsheet_name:
            load_dotenv(find_dotenv())
            gsheet_name = os.getenv("GOOGLE_SHEET_NAME")
            if gsheet_name is None:
                raise ValueError(
                    "gsheet_name is not provided and GOOGLE_SHEET_NAME is not set in environment variables."
                )
        
        gsheet = self.gc.get_sheet(gsheet_name)
        gsheet.sheet1.update([self.jobs_df.columns.values.tolist()] + self.jobs_df.values.tolist())