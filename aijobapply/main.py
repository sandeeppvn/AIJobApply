import argparse
import imp
import os

cwd = os.getcwd()
os.environ["PYTHONPATH"] = cwd


import logging

from src.job_processor import JobProcessor
from src.utils import validate_arguments

logging.basicConfig(level=logging.INFO)


def run_application(args: dict) -> None:
    """
    Run the AI job application process.

    Parameters:
    -----------
    args: dict
        Dictionary of arguments to run the application with.

    Returns:    
    --------
    None

    """

    #Validate arguments
    try:
        logging.info("Validating arguments...")
        validated_args = validate_arguments(args)
        logging.info("Arguments validated.")
    except Exception as e:
        logging.exception(f"Error validating arguments: {e}")
        return

    try:
        logging.info("Creating job processor object...")
        # Create job processor object
        job_processor = JobProcessor(validated_args)

        logging.info("Processing jobs...")
        job_processor.process_jobs()
        logging.info("Jobs processed.")
    except Exception as e:
        logging.exception(f"Error processing jobs: {e}")
        return


def aijobapply_cli():
    """
    Command-line interface function for AI job application process.
    """
    parser = argparse.ArgumentParser(description="AI Job Application CLI")
    
    parser.add_argument("--USE_GMAIL", action="store_true", help="Use Gmail to send emails")
    parser.add_argument("--GMAIL_ADDRESS", type=str, default=None, help="Gmail address to send emails from")
    parser.add_argument("--GMAIL_PASSWORD", type=str, default=None, help="Password to gmail account")
    # parser.add_argument("--EMAIL_CONTENT", type=str, default=None, help="Email content")
    
    parser.add_argument("--USE_LINKEDIN", action="store_true", help="Use LinkedIn to send messages")
    parser.add_argument("--LINKEDIN_USERNAME", type=str, default=None, help="LinkedIn username")
    parser.add_argument("--LINKEDIN_PASSWORD", type=str, default=None, help="LinkedIn password")
    # parser.add_argument("--LINKEDIN_NOTE", type=str, default=None, help="LinkedIn note")
    parser.add_argument("--INTERACTIVE", action="store_true", default=False, help="Run in interactive mode/show browser")
    parser.add_argument("--CHROMEDRIVER_PATH", type=str, default=None, help="Path to the selenium driver")
    
    parser.add_argument( "--GOOGLE_API_CREDENTIALS_FILE", type=str, default=None, help="Path to the credentials file for google api")
    parser.add_argument("--GOOGLE_SHEET_NAME", type=str, default="AIJobApply", help="Name of the google sheet to read jobs from")
    
    # parser.add_argument("--LLM_API_URL", type=str, default="https://api.openai.com/v1/chat/completions", help="LLM API URL")
    parser.add_argument("--LLM_API_KEY", type=str, default=None, help="LLM api key")
    parser.add_argument("--LLM_MODEL", type=str, default=None, help="LLM model to use")

    parser.add_argument("--RESUME_PATH", type=str, default=None, help="Path to resume")
    parser.add_argument("--RESUME_PROFESSIONAL_SUMMARY", type=str, default=None, help="Professional summary for resume")
    parser.add_argument("--COVER_LETTER_PATH", type=str, default=None, help="Path to cover letter")
    parser.add_argument("--DESTINATION_FOLDER", type=str, default=None, help="Folder to save documents to")
    
    args = parser.parse_args()
    
    run_application(vars(args))


if __name__ == "__main__":
    aijobapply_cli()
