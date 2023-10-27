import json
import logging
import os

import openai
from dotenv import find_dotenv, load_dotenv

from src.utils import load_templates

logging.basicConfig(level=logging.INFO)


class Openai:
    def __init__(self):
        """
        Initialize Openai object by loading environment variables and setting API key.
        """
        load_dotenv(find_dotenv())
        self.api_key = str(os.getenv("OPENAI_API_KEY"))
        self.model = str(os.getenv("OPENAI_MODEL"))
        openai.api_key = self.api_key

    def query_prompt(self, prompt: str) -> str:
        """
        Query the OpenAI API with a given prompt.

        Args:
        - prompt (str): The prompt to be sent to the API.

        Returns:
        - str: Response from the API.
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0,
            )

            return response.choices[0].message["content"]  # type: ignore
        except Exception as e:
            logging.error(f"Error querying OpenAI API: {e}")
            return ""

    def find_email(self, contact_details: str) -> str:
        """
        Extract email address from contact details using OpenAI.

        Args:
        - contact_details (str): The provided contact details.

        Returns:
        - str: Extracted email address or addresses.
        """
        prompt = f"""
        Contact details for a job posting delimited by triple backticks.
        Your goal is to find the email address from the contact details if it is present.
        Do not provide an email address if it is not present.
        The email address should be an exact match in the contact details.
        If only one email address is present, provide it.
        If no email address is present, provide an empty string.
        If multiple email addresses are present, provide them in a comma separated manner.
        Contact details: ```{contact_details}```
        """
        return self.query_prompt(prompt)

    def get_job_description(self, description: str, position: str, company_name: str) -> str:
        """
        Extract key hard skills, soft skills, and formatted job description from given inputs using OpenAI.

        Args:
        - description (str): The job description.
        - position (str): The job position.
        - company_name (str): The company name.

        Returns:
        - str: Formatted job description with key skills.
        """
        prompt = f"""
            Act as a job seeker and you are looking at a job posting for {position} at {company_name}. \
            Your goal is to understand the job description and find the key hard skills and soft skills. \
            Perform the following tasks: \
            Step 1: From the Job Description, which is delimited by triple backticks, find the job description \
            Step 2: From the job description, find \
                i) Hard skills: Technical skills, programming languages, Tools, etc. \
                ii) Soft skills: Communication, Teamwork, Problem solving, etc. \
            Step 3: Provide the job description and the key hard skills and soft skills in a well formatted manner \
            Job Description: ```{description}```

            Output: a string of the job description
        """
        return self.query_prompt(prompt)

    def generate_custom_contents(
        self, description: str, position: str, company_name: str, job_link: str, contact_details: str
    ) -> dict:
        """
        Generate customized content for email, cover letter, and resume based on given inputs.

        Args:
        - description (str): The job description.
        - position (str): The job position.
        - company_name (str): The company name.
        - job_link (str): The job link.
        - contact_details (str): Contact details.

        Returns:
        - dict: Customized contents for email, cover letter, resume, and updated job description.
        """
        templates = load_templates()
        prompt = f"""
            You are applying for a {position} position at {company_name}. \
            Your goal is to generate a customized cover letter, resume and email. \
            The output should be in a json format with the keys: cover_letter, resume and email. \
            All the documents should be in a well formatted manner. \
            Act as a professional writer.
            Step 1: Read the cover Letter <Cover Letter>
            Step 2: Read the Job description <Job Description>
            Step 3: Read the Resume <Resume>
            Step 4: Read the Email <Email>
            Step 5: Understand the job requirements, hard skills and soft skills. Ensure to capture the vision and mission of the company and the job role.
            Step 6: Modify the cover letter to match the Job Description. Don't overdo it, ensure the consistency remains. Try to retain as much information as possible from the resume and cover letter.
            Step 7: Provide the content in a text format consistent with the original cover letter, maintaining the same structure, paragraph objectives and number of words or total length of text. 
                The final paragraphs should be defined by:
                1. Para 1: Interest in the company, job and matching with the values and mission. Why I am interested in the role. Something specific that matches my work and the job.
                2. Para 2: My introduction and confidence that I can add value to the team.
                3. Para 3: My skillset and achievements emphasizing on the matching and requirements of the job posting.
                4. Para 4: Conclusion and excitement to apply/join the team.
            Step 8: Modify only the summary section of the resume to match the Job Description. Keep the length of the summary the same.
            Step 9: Identify the first name from the contact details: {contact_details}
            Step 10: Create email content to send to the recruiter or hiring manager. Add the job link: {job_link} as the last line of the email as reference.
            Step 11: Generate an appropriate subject line for the email. I am a job seeker who found a relevant role and is looking some advise, referral or networking

            Cover Letter: 
            ```{templates["cover_letter_template"]}```

            Resume:
            ```{templates["resume_template"]}```

            Job Description:
            ```{description}```

            Email:
            ```{templates["email_template"]}```

            Output: A json with the keys: cover_letter, resume and email, description, email_subject_line
            The output should be json parsable in python.
        """
        try:
            response = json.loads(self.query_prompt(prompt))
            response["description"] = description
            return response
        except json.JSONDecodeError:
            logging.error("Error decoding JSON from OpenAI response.")
            return {}
