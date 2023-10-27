from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import re
from tqdm import tqdm
from openai_handler import Openai
from notion_handler import Notion
import json

'''
Description: 
- This class scrapes the job details from the job links.
- Use selenium to open the job link
- Use OpenAI to find the job description
- Use regex to find the email address
'''
class UpdateJobs(Openai, Notion):
    def __init__(self, templates: dict):
        Openai.__init__(self)
        Notion.__init__(self)

        # Initialize the selenium driver
        self.driver = webdriver.Chrome(service=Service('/packages/chromedriver.exe'))

        # Load the templates
        self.templates = templates
        

    def update_job_details(self, jobs_dict: dict):
        '''
        Description: This function takes in a jobs_dict and updates the job description and email address into the Notion database
        Input: jobs_dict (dict)
        Output: None
        '''
        for job in tqdm(jobs_dict):

            # Get the job details
            job_link = job['properties']['Job']['url']
            company_name = job['properties']['Company']['title'][0]['text']['content']
            job_role = job['properties']['Position']['select']['name']
            job_id = job['id']

            # Open the job link and get the page text
            self.driver.get(job_link)
            page_text = self.driver.find_element('tag name', 'body').text

            # From the page text, find the job description using OpenAI API
            job_description = self.find_job_description(page_text, job_role, company_name)

            # Generate a customized cover letter, resume and email
            customized_text = self.generate_customized_text(job_description, job_role, company_name)
            

            # Create a contact page for the email
            email = self.find_email(page_text)
            if email:
                # Obtain name from email, Split by @ and then split by space or number or underscore or dash or dot or other special characters and combine the words with space
                first = re.split(r'[@]', email)[0]
                name = ' '.join(re.split(r'[^a-zA-Z0-9_\-\.]', first))
                # Create a new contact record(page) with the email address and email content
                contact_properties = {
                    "Email": {"email": email},
                    "Content": {"rich_text": [{"text": {"content": customized_text['email']}}]},
                    "Company": {"rich_text": [{"text": {"content": company_name}}]},
                    "Name": {"title": [{"text": {"content": name}}]},
                    "Job": {"relation": [{"id": job_id}]}
                }
                self.create_pages(self.contacts_id, contact_properties)


            # Update the job record(page) with the job description and cover letter and resume summary, also mark the 
            job_properties = {
                "Description": {"rich_text": [{"text": {"content": job_description}}]},
                "CoverLetter": {"rich_text": [{"text": {"content": customized_text['cover_letter']}}]},
                "Resume": {"rich_text": [{"text": {"content": customized_text['resume']}}]},
                "processed": {"checkbox": True}
            }
            self.update_pages(job_id, job_properties)




    def generate_customized_text(self, job_description: str, job_role: str, company_name: str) -> dict:
        '''
        Description: This function takes in a job description, job role and company name and returns a customized cover letter, resume and email
        Input: job_description (str), job_role (str), company_name (str)
        Output: customized_text (dict), a dictionary of customized cover letter, resume and email
        '''
        cover_letter_template = self.templates['cover_letter_template']
        resume_template = self.templates['resume_template']
        email_template = self.templates['email_template']

        # Generate a customized cover letter, resume and email
        prompt = f"""
            You are applying for a {job_role} position at {company_name}. \
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
            Step 9: Create email content to send to the recruiter or hiring manager.

            Cover Letter: 
            ```{cover_letter_template}```

            Resume:
            ```{resume_template}```

            Job Description:
            ```{job_description}```

            Email:
            ```{email_template}```

            Output: A json with the keys: cover_letter, resume and email. 
            The values should within double quotes. The json should be inside curly braces.
            Use double quotes for the keys and values. For strings within the values, use single quotes.
        """
        
        response = self.query_prompt(prompt)

        # Parse the response as a json
        response = json.loads(response)

        return response

  
    
    def find_job_description(self, page_text: str, job_role: str, company_name: str) -> str:
        '''
        Description: This function takes in a page text, job role and company name and returns the job description using openai
        Input: page_text (str), job_role (str), company_name (str)
        Output: job_description (str)
        '''

        prompt = f"""
            Act as a job seeker and you are looking at a job posting for {job_role} at {company_name}. \
            Your goal is to understand the job description and find the key hard skills and soft skills. \
            Perform the following tasks: \
            Step 1: From the Page Text, which is delimited by triple backticks, find the job description \
            Step 2: From the job description, find \
                i) Hard skills: Technical skills, programming languages, Tools, etc. \
                ii) Soft skills: Communication, Teamwork, Problem solving, etc. \
            Step 3: Provide the job description and the key hard skills and soft skills in a well formatted manner \
            Pgae Text: ```{page_text}```
        """

        # Query the OpenAI API
        job_description = self.query_prompt(prompt)

        return job_description
    
    def find_email(self, page_text):
        '''
        Description: This function takes in a page text and returns the email address
        Input: page_text (str)
        Output: email (str)
        '''

        # the emails should be in the format of <characters>@<characters>.<characters>, the . must be present

        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', page_text)
        if email_match:
            email = email_match.group()
        else:
            # TODO: Scrape the email from LinkedIn
            email = None
        
        return email
    