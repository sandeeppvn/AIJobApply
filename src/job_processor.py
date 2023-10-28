import logging
import os
from operator import ge
from typing import Optional

from dotenv import find_dotenv, load_dotenv

from src.email_handler import EmailHandler
from src.notion_handler import Notion
from src.openai_handler import Openai

logger = logging.getLogger(__name__)


class JobProcessor:
    def __init__(
        self,
        templates_path: str = "templates",
        gmail: Optional[str] = None,
        password: Optional[str] = None,
        notion_secret_key: Optional[str] = None,
        openapi_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize a JobProcessor instance with required handlers and credentials.
        """

        # if not specified, details from the .env file will be used
        self.templates_path = templates_path

        load_dotenv(find_dotenv())
        # if not specified, details from the .env file will be used and assinged to self
        self.gmail = gmail or os.getenv("GMAIL_ADDRESS")
        self.password = password or os.getenv("GMAIL_PASSWORD")
        self.notion_secret_key = notion_secret_key or os.getenv("NOTION_SECRET_KEY")
        self.openapi_key = openapi_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL")

        # Exception handling
        if self.gmail is None:
            raise ValueError("gmail is not provided and GMAIL_ADDRESS is not set in environment variables.")
        if self.password is None:
            raise ValueError("password is not provided and GMAIL_PASSWORD is not set in environment variables.")
        if self.notion_secret_key is None:
            raise ValueError(
                "notion_secret_key is not provided and NOTION_SECRET_KEY is not set in environment variables."
            )
        if self.openapi_key is None:
            raise ValueError("openapi_key is not provided and OPENAI_API_KEY is not set in environment variables.")
        if self.model is None:
            raise ValueError("model is not provided and OPENAI_MODEL is not set in environment variables.")

        self.notion = Notion(self.notion_secret_key)
        self.openai = Openai(self.openapi_key, self.model)
        self.email_handler = EmailHandler(self.gmail, self.password)

    def filter_jobs_by_status(self, jobs, status):
        """
        Filter jobs by the given status.

        Args:
        - jobs (list): List of job dictionaries.
        - status (str): Status to filter by.

        Returns:
        - list: List of jobs filtered by the status.
        """
        return [job for job in jobs if job["properties"]["Status"]["select"]["name"] == status]

    def process_new_jobs(self, new_jobs):
        """
        Process jobs with "Saved" status.

        Args:
        - new_jobs (list): List of new job dictionaries.

        Returns:
        - list: Updated list of new job dictionaries.
        """
        processed_jobs = []
        for new_job in new_jobs:
            if new_job["properties"]["Email"]["rich_text"]:
                new_job["properties"]["Status"]["select"]["name"] = "Email Ready"
                processed_jobs.append(new_job)
            else:
                if new_job["properties"]["Contact Details"]["rich_text"]:
                    email = self.openai.find_email(new_job["properties"]["Contact Details"]["rich_text"])
                    if email:
                        new_job["properties"]["Email"]["email"] = email
                        new_job["properties"]["Status"]["select"]["name"] = "Email Ready"
                        processed_jobs.append(new_job)
                    else:
                        new_job["properties"]["Status"]["select"]["name"] = "Email required"
                        processed_jobs.append(new_job)
                else:
                    new_job["properties"]["Status"]["select"]["name"] = "Email required"
                    processed_jobs.append(new_job)
        return processed_jobs

    def process_email_ready_jobs(self, email_ready_jobs):
        """
        Process jobs with "Email Ready" status.

        Args:
        - email_ready_jobs (list): List of jobs ready for emails.

        Returns:
        - list: Updated list of email ready job dictionaries.
        """
        processed_jobs = []
        for email_ready_job in email_ready_jobs:
            if (
                not email_ready_job["properties"]["Email"]["rich_text"]
                and not email_ready_job["properties"]["Contact Details"]["rich_text"]
            ):
                email_ready_job["properties"]["Status"]["select"]["name"] = "Email required"
                processed_jobs.append(email_ready_job)
                continue

            if email_ready_job["properties"]["Contact Details"]["rich_text"]:
                contact_details = email_ready_job["properties"]["Contact Details"]["rich_text"][0]["text"]["content"]
            else:
                contact_details = ""
            generated_content = self.openai.generate_custom_contents(
                description=email_ready_job["properties"]["Description"]["rich_text"][0]["text"]["content"],
                position=email_ready_job["properties"]["Position"]["select"]["name"],
                company_name=email_ready_job["properties"]["Company Name"]["title"][0]["text"]["content"],
                job_link=email_ready_job["properties"]["Link"]["url"],
                contact_details=contact_details,
            )

            email_ready_job["properties"]["Email Content"]["rich_text"][0]["text"]["content"] = generated_content[
                "email"
            ]
            email_ready_job["properties"]["Cover Letter Content"]["rich_text"][0]["text"][
                "content"
            ] = generated_content["cover_letter"]
            email_ready_job["properties"]["Resume Content"]["rich_text"][0]["text"]["content"] = generated_content[
                "resume"
            ]
            email_ready_job["properties"]["Description"]["rich_text"][0]["text"]["content"] = generated_content[
                "description"
            ]
            email_ready_job["email_subject_line"] = generated_content["email_subject_line"]

            email_ready_job["properties"]["Status"]["select"]["name"] = "Email Approval Required"
            processed_jobs.append(email_ready_job)
        return processed_jobs

    def process_email_approved_jobs(self, email_approved_jobs):
        """
        Process jobs with "Email Approved" status.

        Args:
        - email_approved_jobs (list): List of approved jobs for email.

        Returns:
        - list: Updated list of email approved job dictionaries.
        """
        processed_jobs = []
        for email_approved_job in email_approved_jobs:
            email_content = email_approved_job["properties"]["Email Content"]["rich_text"][0]["text"]["content"]
            email = email_approved_job["properties"]["Email"]["rich_text"][0]["text"]["content"]
            subject_line = email_approved_job["email_subject_line"]
            self.email_handler.send(email_content, email, subject_line)

            email_approved_job["properties"]["Status"]["select"]["name"] = "Email Sent"
            processed_jobs.append(email_approved_job)
        return processed_jobs

    def process_jobs(self, j_id: Optional[str] = None):
        """
        Main function to process jobs based on their status.
        Parameters:
        - jobs_database_id (str): ID of the Notion database. If not specified, details from the .env file will be used.
        """
        load_dotenv(find_dotenv())
        jobs_database_id = j_id or os.getenv("NOTION_JOBS_DATABASE_ID")
        if jobs_database_id is None:
            raise ValueError(
                "jobs_database_id is not provided and NOTION_JOBS_DATABASE_ID is not set in environment variables."
            )

        # variables: name, type, value, operation
        all_jobs = self.notion.get_pages_by_filter(
            database_id=jobs_database_id,
            property_name="Email Sent",
            property_type="checkbox",
            property_value=False,
            filter_operation="equals",
        )

        new_jobs = self.filter_jobs_by_status(all_jobs, "Saved")
        email_ready_jobs = self.filter_jobs_by_status(all_jobs, "Email Ready")
        email_approved_jobs = self.filter_jobs_by_status(all_jobs, "Approval Required")

        processed_new_jobs = self.process_new_jobs(new_jobs)
        processed_email_ready_jobs = self.process_email_ready_jobs(email_ready_jobs)
        processed_email_approved_jobs = self.process_email_approved_jobs(email_approved_jobs)

        jobs_to_update = processed_new_jobs + processed_email_ready_jobs + processed_email_approved_jobs
        self.notion.update_jobs(jobs_to_update)
