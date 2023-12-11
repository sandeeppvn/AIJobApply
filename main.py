import argparse
import os

cwd = os.getcwd()
os.environ["PYTHONPATH"] = cwd


from src.job_processor import JobProcessor


def aijobapply_cli():
    """
    Command-line interface function for AI job application process.
    CLI arguments:
        -h, --help: show help message and exit
        -t --templates_path: path to the template folder
        -g --gmail: gmail address to send emails from
        -p --password: password to gmail account
        -j --jobs_database_id: databse id of the jobs table in notion
        -o --openapi_key: openai api key
        -m --model: openai model to use
    """
    parser = argparse.ArgumentParser(description="AI Job Application CLI")
    parser.add_argument("-t", "--templates_path", type=str, default=None, help="Path to the template folder")

    # If not specified, details from the .env file will be used
    parser.add_argument("-ga", "--gmail_address", type=str, default=None, help="Gmail address to send emails from")
    parser.add_argument("-gp", "--gmail_password", type=str, default=None, help="Password to gmail account")
    parser.add_argument("-c", "--credentials_file_path", type=str, default=None, help="Path to the credentials file for google api")
    parser.add_argument("-j", "--gsheet_name", type=str, default=None, help="Name of the google sheet to read jobs from")
    parser.add_argument("-o", "--openapi_key", type=str, default=None, help="Openai api key")
    parser.add_argument("-m", "--model", type=str, default=None, help="Openai model to use")
    parser.add_argument("-s", "--selenium_driver_path", type=str, default=None, help="Path to the selenium driver")
    parser.add_argument("-lu", "--linkedin_username", type=str, default=None, help="LinkedIn username")
    parser.add_argument("-lp", "--linkedin_password", type=str, default=None, help="LinkedIn password")

    args = parser.parse_args()

    # Create job processor object
    job_processor = JobProcessor(
        gmail_address=args.gmail_address, gmail_password=args.gmail_password, 
        credentials_file=args.credentials_file_path,
        openapi_key=args.openapi_key, model=args.model,
        selenium_driver_path=args.selenium_driver_path,
        linkedin_username=args.linkedin_username, linkedin_password=args.linkedin_password,
        google_sheet_name=args.gsheet_name
        
    )
    job_processor.process_jobs()


if __name__ == "__main__":
    aijobapply_cli()
