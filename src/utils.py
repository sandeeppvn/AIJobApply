import logging
import os

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from PyPDF2 import PdfReader

# Setting up logger
logger = logging.getLogger(__name__)

TEMPLATES = ["cover_letter_template", "resume_template", "email_template", "linkedin_note_template"]

def load_templates(path: str = "templates") -> dict[str, str]:
    """Load all templates from a directory."""
    if os.getenv("TEMPLATES_PATH"):
        path = os.getenv("TEMPLATES_PATH")
    templates = {}
    for template in TEMPLATES:
        try:
            # If the template is a pdf file, load it using PyPDF2
            if os.path.isfile(f"{path}/{template}.pdf"):
                with open(f"{path}/{template}.pdf", "rb") as f:
                    reader = PdfReader(f)
                    templates[template] = reader.pages[0].extract_text()
            # If the template is a txt file, load it as a string
            elif os.path.isfile(f"{path}/{template}.txt"):
                with open(f"{path}/{template}.txt", "r") as f:
                    templates[template] = f.read()
            # if the templates is a docx file, load it as a string
            elif os.path.isfile(f"{path}/{template}.docx"):
                with open(f"{path}/{template}.docx", "r") as f:
                    templates[template] = f.read()
            else:
                logger.warning(f"Template {template} not found in the specified directory.")
        except Exception as e:
            logger.exception(f"Error occurred while loading {template}: {e}")
    return templates


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


def load_prompt(prompt_name: str, **kwargs) -> str:
    """
    Load prompt for a given prompt name.

    Args:
    - prompt_name (str): Name of the prompt txt file
    - **kwargs: Keyword arguments for the prompt.

    Returns:
    - str: Prompt content in an f-string format.
    """
    if prompt_name == "generate_custom_contents":
        # Load the content from the file "generate_custom_contents.txt" and convert it to an f-string
        with open("prompts/generate_custom_contents.txt", "r") as f:
            prompt = f.read()
    elif prompt_name == "find_email":
        # Load the content from the file "find_email.txt" and convert it to an f-string
        with open("prompts/find_email.txt", "r") as f:
            prompt = f.read()
    else:
        raise ValueError(f"Invalid prompt name: {prompt_name}")

    return prompt.format(**kwargs)


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
    templates = load_templates()
    for template_name, template_content in templates.items():
        with open(f"{job_folder}/{template_name}.docx", "w") as f:
            f.write(template_content)

def validate_argments(args) -> dict:
    """
    Validate the arguments passed to the CLI. 
    Check if all arguments are present and valid either from the CLI or as an environment variable.
    Create a dictionary of the arguments and their updated values.
    """
    
    # Define the required arguments
    required_args = {
        "TEMPLATES_PATH": "Path to the template folder",
        "GMAIL_ADDRESS": "Gmail address to send emails from",
        "GMAIL_PASSWORD": "Password to gmail account",
        "GOOGLE_API_CREDENTIALS_FILE": "Path to the credentials file for google api",
        "GOOGLE_SHEET_NAME": "Name of the google sheet to read jobs from",
        "OPENAI_URL": "Openai url",
        "OPENAI_API_KEY": "Openai api key",
        "OPENAI_MODEL": "Openai model to use",
        "CHROMEDRIVER_PATH": "Path to the selenium driver",
        "LINKEDIN_USERNAME": "LinkedIn username",
        "LINKEDIN_PASSWORD": "LinkedIn password",
        "INTERACTIVE": "Run in interactive mode/show browser"
    }

    # Create a dictionary to store the validated arguments
    validated_args = {}

    # If there is an environment file, load it to get the environment variables
    load_dotenv(find_dotenv())

    # Load the linkedin_note_template.pdf file and ensure the content is under 200 characters
    with open("templates/linkedin_note_template.pdf", "rb") as f:
        reader = PdfReader(f)
        linkedin_note_template = reader.pages[0].extract_text()
        if len(linkedin_note_template) > 200:
            raise ValueError("LinkedIn note template cannot be longer than 200 characters.")
    
    # Check if all required arguments are present
    for arg_name, arg_description in required_args.items():
        if getattr(args, arg_name) is None:
            if os.getenv(arg_name):
                validated_args[arg_name] = os.getenv(arg_name)
            else:
                raise ValueError(f"Argument {arg_name} not found. Please provide {arg_description} either as a CLI argument or as an environment variable.")
        else:
            validated_args[arg_name] = getattr(args, arg_name)
    return validated_args