import json
import logging

import openai

from src.utils import (generate_function_description, load_prompt,
                       load_templates)

logging.basicConfig(level=logging.INFO)

class Openai:
    def __init__(self, openapi_key: str, model: str):
        """
        Initialize Openai object and set API key.
        """

        openai.api_key = openapi_key
        self.model = model

    def query_prompt(self, prompt: str, function_description: list = [{}]) -> dict:
        """
        Query the OpenAI API with a given prompt.

        Args:
        - prompt (str): The prompt to be sent to the API.
        - function_description (list): List of dictionaries describing the functions to be used.

        Returns:
        - dict: Response from the API.
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            if function_description:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    functions=function_description,
                    function_call="auto",
                )
            else:
                response = openai.Completion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                )
            output = response.choices[0].message  # type: ignore
            if output.get("function_call"):
                function_name = output.function_call.name
                if function_name not in ["find_email_helper", "generate_custom_contents_helper"]:
                    raise ValueError(f"Function name {function_name} not found in the list of available functions.")
                function_call = eval(f"self.{function_name}")

                function_arguments = json.loads(output.function_call.arguments)
                output = function_call(**function_arguments)

                return output

            return output.content
        except Exception as e:
            logging.error(f"Error querying OpenAI API: {e}")
            return {}

    def find_email(self, contact_details: str) -> str:
        """
        Extract email address from contact details using OpenAI.

        Args:
        - contact_details (str): The provided contact details.

        Returns:
        - str: Extracted email address or addresses.
        """
        prompt = load_prompt("find_email", contact_details=contact_details)

        function_description = generate_function_description(
            "find_email_helper",
            "Find email address from contact details",
            ("email", "Email address"),
        )

        response = self.query_prompt(prompt, function_description)
        return response["email"]

    def find_email_helper(self, email: str) -> dict:
        """Parse the response from OpenAI API to match the required output format."""
        return {"email": email}

    def generate_custom_contents(self, **kwargs) -> dict:
        """
        Generate customized content for email, cover letter, and resume based on given inputs.

        **kwargs:
        - raw_job_description (str): Raw job description.
        - position (str): Position name.
        - company_name (str): Company name.
        - job_link (str): Link to the job posting.


        Returns:
        - dict: Customized contents for email, cover letter, resume, and updated job description.
        """
        templates = load_templates()
        merged_kwargs = {**templates, **kwargs}
        prompt = load_prompt(
            prompt_name="generate_custom_contents",
            **merged_kwargs,
        )

        try:
            function_description = generate_function_description(
                "generate_custom_contents_helper",
                "Generate custom contents",
                ("cover_letter", "Cover letter content"),
                ("resume", "Resume content"),
                ("email_content", "Email content"),
                ("updated_job_description", "Updated job description"),
                ("email_subject_line", "Email subject line"),
            )

            return self.query_prompt(prompt, function_description)

        except json.JSONDecodeError:
            logging.error("Error decoding JSON from OpenAI response.")
            return {}

    def generate_custom_contents_helper(
        self, cover_letter: str, resume: str, email_content: str, updated_job_description: str, email_subject_line: str
    ) -> dict:
        """Parse the response from OpenAI API to match the required output format."""
        return {
            "cover_letter": cover_letter,
            "resume": resume,
            "email_content": email_content,
            "description": updated_job_description,
            "email_subject_line": email_subject_line,
        }
