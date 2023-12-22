import argparse
import os
from ast import parse

cwd = os.getcwd()
os.environ["PYTHONPATH"] = cwd


from src.job_processor import JobProcessor
from src.utils import validate_arguments


def run_application(args):
    """
    Run the AI job application process.

    Args:
        args: Command line arguments

    Returns:
        None

    """

    #Validate arguments
    validated_args = validate_arguments(args)

    # Create job processor object
    job_processor = JobProcessor(validated_args)
    job_processor.process_jobs()


def aijobapply_cli():
    """
    Command-line interface function for AI job application process.


    """
    parser = argparse.ArgumentParser(description="AI Job Application CLI")
    
    parser.add_argument("--USE_GMAIL", action="store_true", help="Use Gmail to send emails")
    parser.add_argument("--GMAIL_ADDRESS", type=str, default=None, help="Gmail address to send emails from")
    parser.add_argument("--GMAIL_PASSWORD", type=str, default=None, help="Password to gmail account")
    parser.add_argument("--EMAIL_CONTENT", type=str, default=None, help="Email content")
    
    parser.add_argument("--USE_LINKEDIN", action="store_true", default=True, help="Use LinkedIn to send connection requests")
    parser.add_argument("--LINKEDIN_USERNAME", type=str, default=None, help="LinkedIn username")
    parser.add_argument("--LINKEDIN_PASSWORD", type=str, default=None, help="LinkedIn password")
    parser.add_argument("--LINKEDIN_NOTE", type=str, default=None, help="LinkedIn note")
    parser.add_argument("--INTERACTIVE", action="store_true", default=False, help="Run in interactive mode/show browser")
    parser.add_argument("--CHROMEDRIVER_PATH", type=str, default=None, help="Path to the selenium driver")
    
    parser.add_argument( "--GOOGLE_API_CREDENTIALS_FILE", type=str, default=None, help="Path to the credentials file for google api")
    parser.add_argument("--GOOGLE_SHEET_NAME", type=str, default="AIJobApply", help="Name of the google sheet to read jobs from")
    
    parser.add_argument("--OPENAI_URL", type=str, default="https://api.openai.com/v1/", help="Openai url")
    parser.add_argument("--OPENAI_API_KEY", type=str, default=None, help="Openai api key")
    parser.add_argument("--OPENAI_MODEL", type=str, default=None, help="Openai model to use")

    parser.add_argument("--RESUME_PATH", type=str, default=None, help="Path to resume")
    parser.add_argument("--COVER_LETTER_PATH", type=str, default=None, help="Path to cover letter")
    
    args = parser.parse_args()
    run_application(args)


if __name__ == "__main__":
    aijobapply_cli()
