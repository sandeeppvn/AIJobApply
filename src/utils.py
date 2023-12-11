import logging
import os

import pandas as pd
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
    templates = load_templates()
    for template_name, template_content in templates.items():
        with open(f"{job_folder}/{template_name}.docx", "w") as f:
            f.write(template_content)

    # # Create a pdf file for the cover letter
    # with open(f"{destination}/{job_folder}/cover_letter.pdf", "w") as f:
    #     f.write(job["Cover Letter"])
    
    # Create a pdf file for the resume
    pass
