import logging

from src.email_handler import EmailHandler
from src.notion_handler import Notion
from src.openai_handler import Openai

logger = logging.getLogger(__name__)


class JobProcessor:
    def __init__(self):
        """
        Initialize a JobProcessor instance with required handlers.
        """
        self.notion = Notion()
        self.openai = Openai()
        self.email_handler = EmailHandler()

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
            if new_job["properties"]["Email"]["email"]:
                new_job["properties"]["Status"]["select"]["name"] = "Email Ready"
                processed_jobs.append(new_job)
            else:
                if new_job["properties"]["Contact Details"]["text"]:
                    email = self.openai.find_email(new_job["properties"]["Contact Details"]["text"])
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
            generated_content = self.openai.generate_custom_contents(
                description=email_ready_job["properties"]["Description"]["text"][0]["text"]["content"],
                position=email_ready_job["properties"]["Position"]["select"]["name"],
                company_name=email_ready_job["properties"]["Company Name"]["title"][0]["text"]["content"],
                job_link=email_ready_job["properties"]["Link"]["url"],
                contact_details=email_ready_job["properties"]["Contact Details"]["text"],
            )

            email_ready_job["properties"]["Email Content"]["rich_text"] = generated_content["email"]
            email_ready_job["properties"]["Cover Letter Content"]["rich_text"] = generated_content["cover_letter"]
            email_ready_job["properties"]["Resume Content"]["rich_text"] = generated_content["resume"]
            email_ready_job["properties"]["Description"]["text"][0]["text"]["content"] = generated_content[
                "description"
            ]
            email_ready_job["properties"]["Email Subject Line"]["title"][0]["text"]["content"] = generated_content[
                "email_subject_line"
            ]

            email_ready_job["properties"]["Status"]["select"]["name"] = "Approval Required"
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
            email = email_approved_job["properties"]["Email"]["email"]
            subject_line = email_approved_job["properties"]["Email Subject Line"]["title"][0]["text"]["content"]

            self.email_handler.send(email_content, email, subject_line)

            email_approved_job["properties"]["Status"]["select"]["name"] = "Email Sent"
            processed_jobs.append(email_approved_job)
        return processed_jobs

    def process_jobs(self):
        """
        Main function to process jobs based on their status.
        """
        filter = {"Status": ["Saved", "Email Ready", "Email Approved"]}
        all_jobs = self.notion.get_pages(self.notion.jobs_id, filter)
        new_jobs = self.filter_jobs_by_status(all_jobs, "Saved")
        email_ready_jobs = self.filter_jobs_by_status(all_jobs, "Email Ready")
        email_approved_jobs = self.filter_jobs_by_status(all_jobs, "Email Approved")

        new_jobs = self.process_new_jobs(new_jobs)
        email_ready_jobs = self.process_email_ready_jobs(email_ready_jobs)
        email_approved_jobs = self.process_email_approved_jobs(email_approved_jobs)

        jobs_to_update = new_jobs + email_ready_jobs + email_approved_jobs
        self.notion.update_jobs(jobs_to_update)
