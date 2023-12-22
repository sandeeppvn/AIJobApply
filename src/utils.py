import logging
import os

import docx
import pandas as pd
from dotenv import find_dotenv, load_dotenv
from PyPDF2 import PdfReader

# Setting up logger
logger = logging.getLogger(__name__)

TEMPLATES = ["cover_letter_template", "resume_template", "email_template", "linkedin_note_template"]

def get_file_content(path: str) -> str:
    """Get the content of a file."""
    try:
        # Ensure the file is .txt, .docx, or .pdf
        if not path.endswith((".txt", ".docx", ".pdf")):
            raise ValueError("Only .txt, .docx, and .pdf files are supported.")

        # Read the file content based on the file type
        if path.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
        elif path.endswith(".pdf"):
            with open(path, "rb") as file:
                pdf_reader = PdfReader(file)
                content = "\n".join([pdf_reader.pages[page].extract_text() for page in range(len(pdf_reader.pages))])
        elif path.endswith(".docx"):
            doc = docx.Document(path)
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            raise ValueError(f"Invalid file type: {path}")
        return content
    except Exception as e:
        logger.exception(f"Error reading file: {e}")
        return ""


def generate_function_description(name: str, description: str, *args: tuple[str, str]) -> list[dict]:
    """
    This function generates a function description for the OpenAPI specification.

    Args:
    - name (str): Name of the function.
    - description (str): Description of the function.
    - *args (tuple): Tuple of tuples containing the function arguments and their descriptions.

    Returns:
    - list[dict]: List of function descriptions in the OpenAPI specification format.
    """
    properties = {}
    required = []
    for arg_name, arg_description in args:
        properties[arg_name] = {"type": "string", "description": arg_description}
        required.append(arg_name)
    function_description = [
        {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties},
            "required": required,
        }
    ]

    return function_description


def load_prompt(prompt_name: str, prompt_args: dict) -> str:
    """
    Load prompt for a given prompt name.

    Args:
    - prompt_name (str): Name of the prompt txt file
    - prompt_args (dict): Dictionary of arguments to be passed to the prompt.

    Returns:
    - str: Prompt content in an f-string format.
    """
    if prompt_name == "generate_custom_contents":
        # Load the content from the file "generate_custom_contents.txt" and convert it to an f-string
        with open("prompts/generate_custom_contents.txt", "r") as f:
            prompt = f.read()
    else:
        raise ValueError(f"Invalid prompt name: {prompt_name}")

    return prompt.format(**prompt_args)


def create_rich_text_dict(content: str) -> dict:
    """
    Create a rich text dictionary for Notion API.

    Args:
    - content (str): Content of the rich text.

    Returns:
    - dict: Rich text dictionary.
    """
    return {
        "type": "text",
        "text": {"content": content},
    }


def create_job_folder(job:pd.Series, destination:str = "job_applications"):
    """
    Create a folder for the job application process.
    Add relevant files to the folder.
    """
    # Create a folder for the job application
    job_folder = f"{destination}/{job['Company Name']}_{job['Position']}"
    os.makedirs(job_folder, exist_ok=True)

    # Save the template files to the folder as docx files
    # TODO: Add logic to generate updated templates and save them to the folder
    templates = {
        "cover_letter": job["Cover Letter Template"],
        "resume": job["Resume Template"],
        "email": job["Email Template"],
        "linkedin_note": job["LinkedIn Note Template"],
    }
    for template_name, template_content in templates.items():
        with open(f"{job_folder}/{template_name}.docx", "w") as f:
            f.write(template_content)




def get_argument_value(arg_name, args):
    """
    Check if the argument is provided via CLI or as an environment variable.
    Raise an error if the argument is not found.
    """
    arg_value = getattr(args, arg_name, None) or os.getenv(arg_name)
    if arg_value is None:
        raise ValueError(f"Required argument '{arg_name}' not provided.")
    return arg_value

def validate_arguments(args) -> dict:
    """
    Validate the arguments passed to the CLI. 
    Check if all arguments are present and valid either from the CLI or as an environment variable.
    Create a dictionary of the arguments and their updated values.
    """
    load_dotenv(find_dotenv())
    validate_args = {}

    required_args = {
        # Gmail arguments
        "USE_GMAIL": "Use Gmail to send emails",

        # LinkedIn arguments
        "USE_LINKEDIN": "Use LinkedIn to send connection requests",

        # OpenAI arguments
        "OPENAI_API_KEY": "Openai api key",
        "OPENAI_MODEL": "Openai model to use",
        "OPENAI_URL": "Openai url",

        # Google Sheets arguments
        "GOOGLE_API_CREDENTIALS_FILE": "Path to the credentials file for google api",
        "GOOGLE_SHEET_NAME": "Name of the google sheet to read jobs from",

        # Document arguments
        "RESUME_PATH": "Path to resume",
        "COVER_LETTER_PATH": "Path to cover letter",
        
    }

    gmail_args = {
        "GMAIL_ADDRESS": "Gmail address to send emails from",
        "GMAIL_PASSWORD": "Password to gmail account",
        "EMAIL_CONTENT": "Email content",
    }

    linkedin_args = {
        "CHROMEDRIVER_PATH": "Path to the selenium driver",
        "LINKEDIN_USERNAME": "LinkedIn username",
        "LINKEDIN_PASSWORD": "LinkedIn password",
        "INTERACTIVE": "Run in interactive mode/show browser"
    }

    # Check if all required arguments are provided
    for arg_name, arg_description in required_args.items():
        if arg_name not in args.__dict__ and os.getenv(arg_name) is None:
            raise ValueError(f"Required argument '{arg_name}' not provided.")
        validate_args[arg_name] = get_argument_value(arg_name, args)
        
    # Check if all Gmail arguments are provided
    if args.USE_GMAIL:
        for arg_name, arg_description in gmail_args.items():
            if arg_name not in args.__dict__ and os.getenv(arg_name) is None:
                raise ValueError(f"Gmail argument '{arg_name}' not provided.")
            validate_args[arg_name] = get_argument_value(arg_name, args)
            
    # Check if all LinkedIn arguments are provided
    if args.USE_LINKEDIN:
        for arg_name, arg_description in linkedin_args.items():
            if arg_name not in args.__dict__ and os.getenv(arg_name) is None:
                raise ValueError(f"LinkedIn argument '{arg_name}' not provided.")
            validate_args[arg_name] = get_argument_value(arg_name, args)

    return validate_args
