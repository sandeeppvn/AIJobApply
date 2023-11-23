import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PyPDF2 import PdfReader

# Setting up logger
logger = logging.getLogger(__name__)

TEMPLATES = ["cover_letter_template", "resume_template", "email_template", "linkedin_note_template"]


def load_template_from_pdf(path: str, template_name: str) -> str:
    """Load content of a single template."""
    with open(f"{path}/{template_name}.pdf", "rb") as f:
        reader = PdfReader(f)
        return reader.pages[0].extract_text()


def load_templates(path: str = "templates") -> dict[str, str]:
    """Load all templates from a directory."""
    templates = {}
    for template in TEMPLATES:
        try:
            templates[template] = load_template_from_pdf(path, template)
        except Exception as e:
            logger.exception(f"Error occurred while loading {template}: {e}")
    return templates


def send_email(
    message_content: str,
    recipient_email: str,
    sender_email: str,
    sender_password: str,
    subject: str,
) -> None:
    """Send an email using Gmail."""

    if not sender_email or not sender_password:
        logger.error("Gmail credentials not found")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(message_content, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            # server.starttls()
            # server.login(sender_email, sender_password)
            # server.sendmail(sender_email, recipient_email, message.as_string())
            logger.info(f"Message sent to {recipient_email}")
    except Exception as e:
        logger.exception(f"Error occurred while sending email: {e}")


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