import json
import logging

import openai

from src.utils import (generate_function_description, load_prompt,
                       load_templates)

logging.basicConfig(level=logging.INFO)

class OpenAIConnectorClass:
    def __init__(self, openapi_key: str, openai_url: str, openai_model: str):
        """
        Initialize Openai object and set API key.

        Args:
        - openapi_key (str): OpenAI API key.
        - openai_url (str): OpenAI API URL.
        - model (str): OpenAI model to use.
        """

        openai.api_key = openapi_key
        openai.api_base = openai_url
        self.model = openai_model


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
                if function_name != "generate_custom_contents_helper":
                    raise ValueError(f"Function name {function_name} not found in the list of available functions.")
                function_call = eval(f"self.{function_name}")

                function_arguments = json.loads(output.function_call.arguments)
                output = function_call(**function_arguments)

                return output

            return output["content"]
        except Exception as e:
            logging.error(f"Error querying OpenAI API: {e}")
            return {}

    def generate_custom_contents(self, job) -> dict:
        """
        Generate customized content for email, cover letter, and resume based on given inputs.
        - job: The pandas Series containing the job information.
        **kwargs:
        - raw_job_description (str): Raw job description.
        - position (str): Position name.
        - company_name (str): Company name.
        - job_link (str): Link to the job posting.


        Returns:
        - dict: Customized contents for email, cover letter, resume, updated job description, message subject line and linkedin note
        """

        kwargs = {
            "raw_job_description": job["Description"],
            "position": job["Position"],
            "company_name": job["Company Name"],
            "job_link": job["Link"],
            "name": job["Name"],
        }
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
                ("cover_letter", "Cover Letter Content"),
                ("resume", "Resume Content"),
                ("message_content", "Message Content"),
                ("updated_job_description", "Updated Job description"),
                ("message_subject_line", "Message Subject line"),
                ("linkedin_note", "LinkedIn Note")
            )
            response = self.query_prompt(prompt, function_description)
            # Check LinkedIn Note length and regenerate if necessary
            linkedin_note = response.get("LinkedIn Note")
            linkedin_prompt = "The LinkedIn note is too long. Please provide a shorter note. (200 characters or less)"
            while linkedin_note and len(linkedin_note) > 300:
                response = openai.Completion.create(
                    model=self.model,
                    prompt=linkedin_prompt,
                    temperature=0,
                )
                linkedin_note = response.choices[0].text.strip()

        except json.JSONDecodeError:
            logging.error("Error decoding JSON from OpenAI response.")
            return {}

    def generate_custom_contents_helper(
        self, 
        cover_letter: str, 
        resume: str, 
        message_content: str, 
        updated_job_description: str, 
        message_subject_line: str,
        linkedin_note: str
    ) -> dict:
        """Parse the response from OpenAI API to match the required output format."""
        return {
            "Cover Letter": cover_letter,
            "Resume": resume,
            "Message Content": message_content,
            "Description": updated_job_description,
            "Message Subject": message_subject_line,
            "LinkedIn Note": linkedin_note
        }
