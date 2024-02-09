import logging
import time

import pandas as pd
from tqdm import tqdm

from src.google_drive_handler import GoogleDriveHandler
from src.google_sheets_handler import GoogleSheetsHandler
from src.linkedin_handler import LinkedInConnectorClass
from src.LLM_handler import LLMConnectorClass
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

        if self.USE_LINKEDIN:
            logger.info("Logging into LinkedIn...")
            self.linkedin_handler = LinkedInConnectorClass(self.CHROMEDRIVER_PATH, self.INTERACTIVE)
            self.linkedin_handler.login(self.LINKEDIN_USERNAME, self.LINKEDIN_PASSWORD)
        

    def process_jobs(self):
        """
        Main function to process jobs based on their status.
        """
        try:
            logger.info("Processing jobs...")
            self.jobs_df = self.get_all_jobs()

            # logger.info("Scrape linkedin job from linkedin url...")
            # self.scrape_linkedin_job()

            logger.info("Generating custom contents for jobs...")
            self.generate_content_for_jobs()

            logger.info("Updating Google Sheet to reflect content generation status...")
            self.gc.update_gsheet_from_dataframe(self.jobs_df, self.GOOGLE_SHEET_NAME)

            logger.info("Processing Content Generated jobs...")
            self.send_messages_for_content_generated_jobs()

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

        # filter job with Applied field containing False
        # jobs = jobs[jobs['Applied'].str.contains('False', case=False)].copy()


        return jobs
    
    def scrape_linkedin_job(self):
        """
        Scrape linkedin job from linkedin url
        """
        def scrape_linkedin_job_wrapper(job: pd.Series, linkedin_handler: LinkedInConnectorClass) -> pd.Series:
            try:
                scrapped_job_content = linkedin_handler.scrape_job(job['link'])
                for key, value in scrapped_job_content.items():
                    job[key] = value
                job['Status'] = 'New Job'
                logger.info(f"Scrape linkedin job from linkedin url for job at Company Name {job['Company Name']}")
            except Exception as e:
                logger.error(f"Failed to scrape linkedin job from linkedin url for job at Company Name {job['Company Name']}. Error: {str(e)}")
                job['Status'] = 'ERROR: Failed to scrape linkedin job from linkedin url'
            return job

        jobs_to_scrape_linkedin_job = self.jobs_df[self.jobs_df['Scrape'] == 'True'].copy()

        if jobs_to_scrape_linkedin_job.empty:
            logger.info("No jobs with Scrape status found for scrape linkedin job from linkedin url.")
            return
        
        logger.info(f"Found {len(jobs_to_scrape_linkedin_job)} jobs with Scrape status for scrape linkedin job from linkedin url.")
        jobs_to_scrape_linkedin_job.progress_apply(lambda job: scrape_linkedin_job_wrapper(job, self.linkedin_handler), axis=1)

    def generate_content_for_jobs(self):
        """
        For all jobs with custom content not generated, generate custom content and set status to "Content Generated"
        Wrapper: generate_custom_contents_wrapper
            Parameters:
            - job (Series): Pandas Series containing the details of a job.
            - LLM_handler (LLMConnectorClass): Instance of LLMConnectorClass.
        """

        # Fetch all jobs with status "New Job"
        jobs_to_generate_content = self.jobs_df[self.jobs_df['Status'] == 'New Job'].copy()
        if jobs_to_generate_content.empty:
            logger.info("No jobs with 'New Job' status found for content generation.")
            return
        
        logger.info(f"Found {len(jobs_to_generate_content)} jobs with 'New Job' status for content generation.")
        # Generate custom content for each job
        
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
                # job['Content Generated'] = 'True'
                job['Status'] = 'Content Generated'
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

    def update_missing_contacts(self):
        """
        Update missing contacts
        - For all jobs with "Content Generated" status, check if email or LinkedIn contact is not provided and set status to "Missing Contact"
        - For all jobs with "Missing Contact" status, check if email or LinkedIn contact is provided and set status to "Content Generated"
        """
        
        jobs_with_contact_required_status = self.jobs_df[
            (self.jobs_df['Status'] == 'Missing Contact') &
            (
                (self.jobs_df['Email'].str.strip() != "") | 
                (self.jobs_df['LinkedIn Contact'].str.strip() != "")
            )
        ].copy()
        if not jobs_with_contact_required_status.empty:
            jobs_with_contact_required_status['Status'] = 'Content Generated'
            logger.info(f"Found {len(jobs_with_contact_required_status)} jobs with 'Missing Contact' status for update missing contacts.")
            self.jobs_df.update(jobs_with_contact_required_status)


        jobs_with_content_generated_status = self.jobs_df[
            (self.jobs_df['Status'] == 'Content Generated') &
            (
                (self.jobs_df['Email'].str.strip() == "") & 
                (self.jobs_df['LinkedIn Contact'].str.strip() == "")
            )
        ].copy()
        if not jobs_with_content_generated_status.empty:
            jobs_with_content_generated_status['Status'] = 'Missing Contact'
            logger.info(f"Found {len(jobs_with_content_generated_status)} jobs with 'Content Generated' status for update missing contacts.")
            self.jobs_df.update(jobs_with_content_generated_status)

    def update_message_content_with_name(self, jobs_df: pd.DataFrame):
        """
        Update message content with name for each job in the DataFrame.
        - In the message content, replace [Contact Name] with the name of the contact.
        - In the message subject, replace [Contact Name] with the name of the contact.
        If the name is not provided, fetch it from LinkedIn profile if available.
        """
        def update_message_content_with_name_wrapper(job: pd.Series, linkedin_handler: LinkedInConnectorClass) -> pd.Series:
            try:
                if job['Contact Name'] == "":
                    linkedin_handler.driver.get(job['LinkedIn Contact'])
                    job['Contact Name'] = linkedin_handler.get_name_from_url(job['LinkedIn Contact'])
                job['Message Content'] = job['Message Content'].replace("[Contact Name]", job['Contact Name'])
                job['Message Subject'] = job['Message Subject'].replace("[Contact Name]", job['Contact Name'])
                logger.info(f"Update message content with name for job at Company Name {job['Company Name']}")
            except Exception as e:
                logger.error(f"Failed to update message content with name for job at Company Name {job['Company Name']}. Error: {str(e)}")
            return job

        jobs_df.progress_apply(lambda job: update_message_content_with_name_wrapper(job, self.linkedin_handler), axis=1)

        self.jobs_df.update(jobs_df)
        
        
        
    def send_messages_for_content_generated_jobs(self):
        """
        Process jobs with "Content Generated" status:
        For all jobs with "Content Generated", send emails and LinkedIn messages and set status to "Message Sent"
        """

        self.update_missing_contacts()

        jobs_with_content_generated_status = self.jobs_df[self.jobs_df['Status'] == 'Content Generated'].copy()
        if jobs_with_content_generated_status.empty:
            logger.info("No jobs with 'Content Generated' status found for sending messages.")
            return
        
        logger.info(f"Found {len(jobs_with_content_generated_status)} jobs with 'Content Generated' status for sending messages.")
        if self.USE_GMAIL:
            gmail_jobs_df = jobs_with_content_generated_status[jobs_with_content_generated_status['Email'].str.strip() != ""].copy()
            if not gmail_jobs_df.empty:
                self.send_emails(gmail_jobs_df)
                self.jobs_df.update(gmail_jobs_df)

        if self.USE_LINKEDIN:
            linkedin_jobs_df = jobs_with_content_generated_status[jobs_with_content_generated_status['LinkedIn Contact'].str.strip() != ""].copy()
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
                    # Set the name in the message content
                    job['Message Content'] = job['Message Content'].replace("[Contact Name]", job['Contact Name'])
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

        linkedin_note = "Hi [Contact Name], I am keen on an open {position} role at {company_name}. I'd appreciate the opportunity to connect and explore how my expertise aligns with this role."

        logger.info("LinkedIn Connection Established.")
        logger.info(f"Sending LinkedIn connection requests to {len(jobs_df)} contacts...")
        def send_linkedin_connection_with_message(job: pd.Series, linkedin_handler: LinkedInConnectorClass) -> pd.Series:
            try:
                name = linkedin_handler.send_connection_request(
                    profile_url=job['LinkedIn Contact'],
                    note=linkedin_note.format(
                        position = job['Position'],
                        company_name =  job['Company Name'],
                    )
                )
                    
                job['Status'] = 'LinkedIn Connection Sent'
                logger.info(f"LinkedIn connection request sent to {job['Contact Name']} for job at Company Name {job['Company Name']}")
                time.sleep(5)
                
            except Exception as e:
                logger.warning(f"Failed to send LinkedIn connection request for job at Company Name {job['Company Name']}. Error: {str(e)}")
                job['Status'] = 'Failed to send LinkedIn connection request'

            return job

        jobs_df.progress_apply(lambda job: send_linkedin_connection_with_message(job, self.linkedin_handler), axis=1) # type: ignore
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