import logging
import os
from typing import Optional

import pandas as pd
from tqdm import tqdm

from src.google_drive_handler import GoogleDriveHandler
from src.google_sheets_handler import GoogleSheetsHandler
from src.utils import create_job_folder, get_file_content

tqdm.pandas()
logger = logging.getLogger(__name__)
class JobProcessor:
    """
    JobProcessor class to process job applications.
    """
    def __init__(
        self,
        kwargs: dict,
    ):
        """
        Initialize JobProcessor class.
        """

        self.jobs_df = pd.DataFrame()
        for key, value in kwargs.items():
            setattr(self, key, value)
        logger.info("JobProcessor initialized.")
        self.gc = GoogleSheetsHandler(self.GOOGLE_API_CREDENTIALS_FILE)
        logger.info("Google Sheets Sevice Account connected.")

        # Extract the destination folder name from the path
        destination_folder_name = self.DESTINATION_FOLDER.split("/")[-1]

        self.google_drive_handler = GoogleDriveHandler(self.GOOGLE_API_CREDENTIALS_FILE, destination_folder_name)
        

    def process_jobs(self):
        """
        Main function to process jobs based on their status.
        """
        try:
            logger.info("Processing jobs...")
            self.jobs_df = self.get_all_jobs()

            logger.info("Finding jobs with missing contacts...")
            self.find_jobs_with_missing_contacts()

            logger.info("Generating custom contents for jobs...")
            self.generate_content_for_jobs()

            logger.info("Updating Google Sheet to reflect content generation status...")
            self.gc.update_gsheet_from_dataframe(self.jobs_df, self.GOOGLE_SHEET_NAME)

            logger.info("Processing Content Generated jobs...")
            self.process_content_generated_jobs()

            logger.info("Updating Google Sheet to reflect email and LinkedIn connection status...")
            self.gc.update_gsheet_from_dataframe(self.jobs_df, self.GOOGLE_SHEET_NAME)
            
            logger.info("Job processing complete.")

        except Exception as e:
            logger.error(f"Error while processing jobs: {str(e)}")
            raise e

    def get_all_jobs(self) -> pd.DataFrame:
        """
        Get all jobs from the Google Sheet.
        """
        gsheet = self.gc.get_gsheet(self.GOOGLE_SHEET_NAME)
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

    def find_jobs_with_missing_contacts(self):
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
        jobs_df.loc[~(has_email | has_linkedin_contact), 'Status'] = 'Contact Required'

        self.jobs_df.update(jobs_df)

    def generate_content_for_jobs(self):
        """
        For all jobs with custom content not generated, generate custom content and set status to "Content Generated"
        Wrapper: generate_custom_contents_wrapper
            Parameters:
            - job (Series): Pandas Series containing the details of a job.
            - LLM_handler (LLMConnectorClass): Instance of LLMConnectorClass.
        """

        # Fetch all jobs with either Message Content, Message Subject, LinkedIn Note, Resume, or Cover Letter missing
        jobs_to_generate_content = self.jobs_df.loc[
            (
                (self.jobs_df['Message Content'].str.strip() == "") |
                (self.jobs_df['Message Subject'].str.strip() == "") |
                (self.jobs_df['LinkedIn Note'].str.strip() == "") |
                (self.jobs_df['Resume'].str.strip() == "") |
                (self.jobs_df['Missing Keywords'].str.strip() == "") |
                (self.jobs_df['Cover Letter'].str.strip() == "")
            )
        ]

        if jobs_to_generate_content.empty:
            logger.info("No jobs with missing custom content found.")
            return
        
        logger.info(f"Found {len(jobs_to_generate_content)} jobs with missing custom content.")
        # Generate custom content for each job
        from src.LLM_handler import LLMConnectorClass
        llm_args = {
            'api_key': self.LLM_API_KEY,
            # 'LLM_api_url': self.LLM_API_URL,
            'model_name': self.LLM_MODEL,
        }
        prompt_args = {
            'resume_template': get_file_content(self.RESUME_PATH),
            'cover_letter_template': get_file_content(self.COVER_LETTER_PATH),
            'resume_professional_summary': self.RESUME_PROFESSIONAL_SUMMARY,
            # 'email_template': self.EMAIL_CONTENT if self.USE_GMAIL else "",
            # 'linkedin_note_template': self.LINKEDIN_NOTE if self.USE_LINKEDIN else "",
        }

        LLM_handler = LLMConnectorClass(llm_args, prompt_args, self.USE_GMAIL, self.USE_LINKEDIN)

        def generate_custom_contents_wrapper(job: pd.Series, LLM_handler: LLMConnectorClass) -> pd.Series:
            try:
                generated_contents = LLM_handler.generate_custom_content(job)
                
                for key, value in generated_contents.items():
                    job[key] = value
                job['Status'] = 'Content Generated'  # Set status if no error occurs
                logger.info(f"Custom contents generated for job at Company Name {job['Company Name']}")

                create_job_folder(
                    job=job,
                    resume_path=self.RESUME_PATH,
                    google_drive_handler=self.google_drive_handler,
                    destination=self.DESTINATION_FOLDER,
                )

            except Exception as e:
                logger.error(f"Failed to generate custom contents for job at Company Name {job['Company Name']}. Error: {str(e)}")
                job['Status'] = 'ERROR: Failed to generate custom contents'
            return job
        

        jobs_to_generate_content.progress_apply(lambda job: generate_custom_contents_wrapper(job, LLM_handler), axis=1) # type: ignore
        self.jobs_df.update(jobs_to_generate_content)

    def process_content_generated_jobs(self):
        """
        Process jobs with "Content Generated" status.
        For all jobs with "Content Generated" status, send emails and LinkedIn messages and set status to "Email Sent" or "LinkedIn Connection Sent"
        For all jobs with "Email Sent" or "LinkedIn Connection Sent" status, update the Google Sheet.
        """
        
        content_generated_jobs_df = self._get_jobs_with_status('Content Generated')
        if self.USE_GMAIL:
            email_jobs_df = content_generated_jobs_df[content_generated_jobs_df['Email'].str.strip() != ""].copy()
            if not email_jobs_df.empty:
                self.send_emails(email_jobs_df)
                self.jobs_df.update(email_jobs_df)

        if self.USE_LINKEDIN:
            linkedin_jobs_df = content_generated_jobs_df[content_generated_jobs_df['LinkedIn Contact'].str.strip() != ""].copy()
            if not linkedin_jobs_df.empty:
                self.send_linkedin_connections(linkedin_jobs_df)
                self.jobs_df.update(linkedin_jobs_df)

    def send_emails(self, jobs_df: pd.DataFrame):
        """
        Send emails for each job in the DataFrame and update the status.
        Wrapper: send_email_wrapper
            Parameters:
            - job (Series): Pandas Series containing the details of a job.
            - email_handler (EmailHandler): Instance of EmailHandler.
        """
        from src.email_handler import EmailHandler
        email_handler = EmailHandler(self.GMAIL_ADDRESS, self.GMAIL_PASSWORD)
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
        linkedin_handler = LinkedInConnectorClass(self.CHROMEDRIVER_PATH, self.INTERACTIVE)
        linkedin_handler.login(self.LINKEDIN_USERNAME, self.LINKEDIN_PASSWORD)

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