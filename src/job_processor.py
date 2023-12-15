import logging
import os
from typing import Optional

import pandas as pd
from tqdm import tqdm

from src.google_sheets_handler import GoogleSheetsHandler
from src.utils import create_job_folder

tqdm.pandas()
logger = logging.getLogger(__name__)
class JobProcessor:
    """
    JobProcessor class to process job applications.
    """
    def __init__(
        self,
        **kwargs,
    ):
        """
        Initialize JobProcessor class.
        Args:
        - templates_path (str): Path to the template folder.
        - gmail_address (str): Gmail address to send emails from.
        - gmail_password (str): Password to gmail account.
        - google_api_credentials_file (str): Path to the credentials file for google api.
        - google_sheet_name (str): Name of the google sheet to read jobs from.
        - openai_url (str): Openai url.
        - openai_api_key (str): Openai api key.
        - openai_model (str): Openai model to use.
        - chromedriver_path (str): Path to the selenium driver.
        - linkedin_username (str): LinkedIn username.
        - linkedin_password (str): LinkedIn password.
        - interactive (bool): Run in interactive mode/show browser.
        """

        self.jobs_df = pd.DataFrame()
        for key, value in kwargs.items():
            setattr(self, key, value)
        logger.info("JobProcessor initialized.")
        self.gc = GoogleSheetsHandler(self.google_api_credentials_file, self.google_sheet_name)
        logger.info("Google Sheets Sevice Account connected.")
        

    def process_jobs(self):
        """
        Main function to process jobs based on their status.
        """
        try:
            logger.info("Processing jobs...")
            self.jobs_df = self.get_all_jobs()

            logger.info("Processing new jobs...")
            self.process_new_jobs()

            logger.info("Processing Contact Ready jobs...")
            self.process_contact_ready_jobs()

            logger.info("Updating Google Sheet to reflect content generation status...")
            self.gc.update_gsheet_from_dataframe(self.jobs_df)

            logger.info("Processing Content Generated jobs...")
            self.process_content_generated_jobs()

            logger.info("Updating Google Sheet to reflect email and LinkedIn connection status...")
            self.gc.update_gsheet_from_dataframe(self.jobs_df)
            
            logger.info("Job processing complete.")

        except Exception as e:
            logger.error(f"Error while processing jobs: {str(e)}")
            raise e

    def get_all_jobs(self) -> pd.DataFrame:
        """
        Get all jobs from the Google Sheet.
        """
        gsheet = self.gc.get_gsheet(self.google_sheet_name)
        jobs = pd.DataFrame(gsheet.sheet1.get_all_records())
        logger.info(f"Found {len(jobs)} jobs in Google Sheet.")

        return jobs
    
    def _get_jobs_with_status(self, status: str) -> pd.DataFrame:
        """
        Get jobs with a specific status.
        """
        jobs_df = self.jobs_df[self.jobs_df['Status'] == status].copy()
        if jobs_df.empty:
            logger.info(f"No jobs with '{status}' status found.")
        else:
            logger.info(f"Found {len(jobs_df)} jobs with '{status}' status.")
        return jobs_df

    def process_new_jobs(self):
        """
        Process jobs with "New Job" and "Contact Required" status.
        For all new jobs, if email or LinkedIn contact is not provided, set status to "Contact Required"
        For all new jobs, if email or LinkedIn contact is provided, set status to "Contact Ready"
        """
        new_jobs_df = self._get_jobs_with_status('New Job')
        contact_required_jobs_df = self._get_jobs_with_status('Contact Required')

        jobs_df = pd.concat([new_jobs_df, contact_required_jobs_df])
        
        has_email = jobs_df['Email'].str.strip() != ""
        has_linkedin_contact = jobs_df['LinkedIn Contact'].str.strip() != ""
        jobs_df.loc[has_email | has_linkedin_contact, 'Status'] = 'Contact Ready'
        jobs_df.loc[~(has_email | has_linkedin_contact), 'Status'] = 'Contact Required'

        self.jobs_df.update(jobs_df)

    def process_contact_ready_jobs(self):
        """
        For all jobs with "Contact Ready" status, generate custom contents and set status to "Content Generated"
        Wrapper: generate_custom_contents_wrapper
            Parameters:
            - job (Series): Pandas Series containing the details of a job.
            - openai_handler (OpenAIConnectorClass): Instance of OpenAIConnectorClass.
        """

        jobs_df = self._get_jobs_with_status("Contact Ready")
        # If content is already generated (check for the data in colmns 'Message Content', 'Message Subject', 'LinkedIn Note', 'Updated Job Description', 'Resume Content', 'Cover Letter Content'), then just update the status to "Content Generated"
        content_generated_jobs_df = jobs_df[
            (jobs_df['Message Content'].str.strip() != "") &
            (jobs_df['Message Subject'].str.strip() != "") &
            (jobs_df['LinkedIn Note'].str.strip() != "") &
            (jobs_df['Resume'].str.strip() != "") &
            (jobs_df['Cover Letter'].str.strip() != "")
        ].copy()

        if not content_generated_jobs_df.empty:
            content_generated_jobs_df['Status'] = 'Content Generated'
            jobs_df.update(content_generated_jobs_df)
            self.jobs_df.update(jobs_df)
            jobs_df = jobs_df[jobs_df['Status'] != 'Content Generated']

        from src.openai_handler import OpenAIConnectorClass
        openai_handler = OpenAIConnectorClass(
            openapi_key=self.openai_api_key,
            openai_url=self.openai_url,
            openai_model=self.openai_model,
        )

        def generate_custom_contents_wrapper(job: pd.Series, openai_handler: OpenAIConnectorClass) -> pd.Series:
            try:
                generated_contents = openai_handler.generate_custom_contents(job)
                for key, value in generated_contents.items():
                    job[key] = value
                job['Status'] = 'Content Generated'  # Set status if no error occurs
                logger.info(f"Custom contents generated for job at Company Name {job['Company Name']}")

                create_job_folder(job) # type: ignore

            except Exception as e:
                logger.error(f"Failed to generate custom contents for job at Company Name {job['Company Name']}. Error: {str(e)}")
                job['Status'] = 'ERROR: Failed to generate custom contents'
            return job
        

        if not jobs_df.empty:
            jobs_df.progress_apply(lambda job: generate_custom_contents_wrapper(job, openai_handler), axis=1) # type: ignore
            self.jobs_df.update(jobs_df)

    def process_content_generated_jobs(self):
        """
        Process jobs with "Content Generated" status.
        For all jobs with "Content Generated" status, send emails and LinkedIn messages and set status to "Email Sent" or "LinkedIn Connection Sent"
        For all jobs with "Email Sent" or "LinkedIn Connection Sent" status, update the Google Sheet.
        """
        
        jobs_df = self._get_jobs_with_status("Content Generated")

        email_jobs_df = jobs_df[jobs_df['Email'].str.strip() != ""].copy()
        if not email_jobs_df.empty:
            self.send_emails(email_jobs_df)
            self.jobs_df.update(email_jobs_df)

        linkedin_jobs_df = jobs_df[jobs_df['LinkedIn Contact'].str.strip() != ""].copy()
        if not linkedin_jobs_df.empty:
            self.send_linkedin_connections(linkedin_jobs_df)

        

    def send_emails(self, jobs_df: pd.DataFrame):
        """
        Send emails for each job in the DataFrame and update the status.
        Wrapper: send_email_wrapper
            Parameters:
            - job (Series): Pandas Series containing the details of a job.
            - email_handler (EmailHandler): Instance of EmailHandler.
        """
        from src.email_handler import EmailHandler
        email_handler = EmailHandler(self.gmail_address, self.gmail_password)
        logger.info("Email Connection Established.")
        logger.info(f"Sending emails to {len(jobs_df)} contacts...")
        def send_email_wrapper(job: pd.Series, email_handler: EmailHandler) -> pd.Series:
                try:
                    email_handler.send(
                        content=job['Message Content'],
                        recepient_email=job['Email'],
                        subject=job['Message Subject'],
                    )
                    job['Status'] = 'Email Sent'
                    logger.info(f"Email sent to {job['Email']} for job at Company Name {job['Company Name']}")
                except Exception as e:
                    logger.warning(f"Failed to send email for job at Company Name {job['Company Name']}. Error: {str(e)}")
                    job['Status'] = 'Failed to send email'
                return job
                
        jobs_df.progress_apply(lambda job: send_email_wrapper(job, email_handler), axis=1) # type: ignore
        self.jobs_df.update(jobs_df)

    def send_linkedin_connections(self, jobs_df: pd.DataFrame):
        """
        Send LinkedIn connection requests for each job in the DataFrame.
        Wrapper: send_linkedin_connection_with_message
            Parameters:
            - job (Series): Pandas Series containing the details of a job.
            - linkedin_handler (LinkedInConnectorClass): Instance of LinkedInConnectorClass.
        """        
        
        from src.linkedin_handler import LinkedInConnectorClass
        logger.info("Logging into LinkedIn...")
        linkedin_handler = LinkedInConnectorClass(self.chromedriver_path, self.interactive)
        linkedin_handler.login(self.linkedin_username, self.linkedin_password)

        logger.info("LinkedIn Connection Established.")
        logger.info(f"Sending LinkedIn connection requests to {len(jobs_df)} contacts...")
        def send_linkedin_connection_with_message(job: pd.Series, linkedin_handler: LinkedInConnectorClass) -> pd.Series:
            try:
                linkedin_handler.send_connection_request(
                    profile_url=job['LinkedIn Contact'],
                    note=job['LinkedIn Note']
                )
                job['Status'] = 'LinkedIn Connection Sent'
                logger.info(f"LinkedIn connection request sent to {job['Name']} for job at Company Name {job['Company Name']}")
                
            except Exception as e:
                logger.warning(f"Failed to send LinkedIn connection request for job at Company Name {job['Company Name']}. Error: {str(e)}")
                job['Status'] = 'Failed to send LinkedIn connection request'

            return job

        jobs_df.progress_apply(lambda job: send_linkedin_connection_with_message(job, linkedin_handler), axis=1) # type: ignore
        self.jobs_df.update(jobs_df)

    def update_gsheet(self):
        """
        Update Google Sheet with the updated jobs DataFrame.
        """
        try:
            self.gc.update_gsheet_from_dataframe(self.jobs_df)
            logger.info("Google Sheet updated successfully.")
        except Exception as e:
            logger.error(f"Error while updating Google Sheet: {str(e)}")
            raise