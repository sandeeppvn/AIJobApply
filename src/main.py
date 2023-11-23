import argparse
import os

cwd = os.getcwd()
os.environ["PYTHONPATH"] = cwd


from job_processor import JobProcessor


def aijobapply_cli():
    """
    Command-line interface function for AI job application process.
    CLI arguments:
        -h, --help: show help message and exit
        -t --templates_path: path to the template folder
        -g --gmail: gmail address to send emails from
        -p --password: password to gmail account
        -n --notion_secret_key: secret key to notion account
        -j --jobs_database_id: databse id of the jobs table in notion
        -o --openapi_key: openai api key
        -m --model: openai model to use
    """
    parser = argparse.ArgumentParser(description="AI Job Application CLI")
    parser.add_argument("-t", "--templates_path", type=str, default="templates")

    # If not specified, details from the .env file will be used
    parser.add_argument("-g", "--gmail", type=str, default=None)
    parser.add_argument("-p", "--password", type=str, default=None)
    parser.add_argument("-c", "--credentials_file", type=str, default=None)
    parser.add_argument("-j", "--gsheet_name", type=str, default=None)
    parser.add_argument("-o", "--openapi_key", type=str, default=None)
    parser.add_argument("-m", "--model", type=str, default=None)

    args = parser.parse_args()

    args.password = "PVNSandeep#0708"

    # Create job processor object
    job_processor = JobProcessor(
        args.templates_path, args.gmail, args.password, args.credentials_file, args.openapi_key, args.model
    )

    # Run job application process
    job_processor.process_jobs(args.gsheet_name)


if __name__ == "__main__":
    aijobapply_cli()
