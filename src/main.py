import argparse
import os

cwd = os.getcwd()
os.environ["PYTHONPATH"] = cwd


from src.job_processor import JobProcessor
from src.utils import validate_argments


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
        -s --chromedriver_path: path to the selenium driver
        -lu --linkedin_username: linkedin username
        -lp --linkedin_password: linkedin password
        -i --interactive: run in interactive mode/show browser

    """
    parser = argparse.ArgumentParser(description="AI Job Application CLI")
    parser.add_argument("-t", "--TEMPLATES_PATH", type=str, default=None, help="Path to the template folder")
    parser.add_argument("-ga", "--GMAIL_ADDRESS", type=str, default=None, help="Gmail address to send emails from")
    parser.add_argument("-gp", "--GMAIL_PASSWORD", type=str, default=None, help="Password to gmail account")
    parser.add_argument("-c", "--GOOGLE_API_CREDENTIALS_FILE", type=str, default=None, help="Path to the credentials file for google api")
    parser.add_argument("-j", "--GOOGLE_SHEET_NAME", type=str, default="AIJobApply", help="Name of the google sheet to read jobs from")
    parser.add_argument("-u", "--OPENAI_URL", type=str, default="https://api.openai.com/v1/", help="Openai url")
    parser.add_argument("-o", "--OPENAI_API_KEY", type=str, default=None, help="Openai api key")
    parser.add_argument("-m", "--OPENAI_MODEL", type=str, default=None, help="Openai model to use")
    parser.add_argument("-s", "--CHROMEDRIVER_PATH", type=str, default=None, help="Path to the selenium driver")
    parser.add_argument("-lu", "--LINKEDIN_USERNAME", type=str, default=None, help="LinkedIn username")
    parser.add_argument("-lp", "--LINKEDIN_PASSWORD", type=str, default=None, help="LinkedIn password")
    parser.add_argument("-i", "--INTERACTIVE", action="store_true", default=False, help="Run in interactive mode/show browser")


    args = parser.parse_args()

    #Validate arguments
    validated_args = validate_argments(args)


    # Create job processor object
    job_processor = JobProcessor(
        templates_path=validated_args["TEMPLATES_PATH"],
        gmail_address=validated_args["GMAIL_ADDRESS"],
        gmail_password=validated_args["GMAIL_PASSWORD"],
        google_api_credentials_file=validated_args["GOOGLE_API_CREDENTIALS_FILE"],
        google_sheet_name=validated_args["GOOGLE_SHEET_NAME"],
        openai_url=validated_args["OPENAI_URL"],
        openai_api_key=validated_args["OPENAI_API_KEY"],
        openai_model=validated_args["OPENAI_MODEL"],
        chromedriver_path=validated_args["CHROMEDRIVER_PATH"],
        linkedin_username=validated_args["LINKEDIN_USERNAME"],
        linkedin_password=validated_args["LINKEDIN_PASSWORD"],
        interactive=validated_args["INTERACTIVE"]
    )
    job_processor.process_jobs()


if __name__ == "__main__":
    aijobapply_cli()
