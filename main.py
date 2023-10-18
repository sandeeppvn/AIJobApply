from update_jobs import UpdateJobs
from get_jobs import NotionJobsClass
from PyPDF2 import PdfReader

def main():
    # Load the templates
    templates = load_templates()

    # Get all the new jobs from the Notion database
    notionJobs = NotionJobsClass()
    new_jobs = notionJobs.get_jobs()

    # Get the job details (job description and email) scrapping from the job link and update the records in the Notion database
    jobDetailsScraper = UpdateJobs(templates)
    jobDetailsScraper.update_job_details(new_jobs)


def load_templates(path = 'documents') -> dict:
    '''
    Description: This function loads the templates from the documents folder
    Input: Optional : path (str) to the directory containing the templates
    Output: A dictionary of templates, keys: cover_letter_template, resume_template, email_template
    '''
    templates = {}

    # Get the email, cover letter and resume template from documents folder
    reader = PdfReader(f'{path}/cover_letter_template.pdf')
    templates['cover_letter_template'] = reader.pages[0].extractText

    reader = PdfReader(f'{path}/resume_template.pdf')
    templates['resume_template'] = reader.pages[0].extractText

    reader = PdfReader(f'{path}/email_template.pdf')
    templates['email_template'] = reader.pages[0].extractText


    return templates

if __name__ == "__main__":
    main()
