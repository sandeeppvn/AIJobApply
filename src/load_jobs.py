import re

import requests
from bs4 import BeautifulSoup


def extract_job_id_from_text(text):
    # Regex pattern to match a LinkedIn job ID
    job_id_pattern = re.compile(r'https://www\.linkedin\.com/jobs/(view|search)/[a-zA-Z0-9/?=&]*currentJobId=(\d{10,})|https://www\.linkedin\.com/jobs/view/(\d{10,})')

    match = job_id_pattern.search(text)
    return match.group(2) or match.group(3) if match else None

def scrape_linkedin_job(job_id):
    url = f"https://www.linkedin.com/jobs/view/?currentJobId={job_id}"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract job title, job description, and company name
        # Note: These selectors are hypothetical and need to be adjusted based on the actual page structure
        job_title = soup.find('h1', {'class': 'job-title-class'}).get_text(strip=True)
        job_description = soup.find('section', {'class': 'job-description-class'}).get_text(strip=True)
        company_name = soup.find('a', {'class': 'company-name-class'}).get_text(strip=True)

        return job_title, job_description, company_name
    else:
        print(f"Failed to fetch the page: Status code {response.status_code}")
        return None
    
if __name__ == '__main__':
    # Example text containing a LinkedIn job ID
    example_text1 = "Check out this job at vent.io: https://www.linkedin.com/jobs/view/3789877020"
    example_text2 = "Check out this job at vent.io: https://www.linkedin.com/jobs/search/?currentJobId=3789877020"
    example_text3 = "Check out this job at vent.io: https://www.linkedin.com/jobs/view/3789877020/?alternateChannel=search&refId=vvF5OAiyf5EF%2FdnahXISAQ%3D%3D&trackingId=xdeHBup3TfqOsjG%2Bzjd3FA%3D%3D&trk=d_flagship3_notifications"
    example_text4 = "Check out this job at vent.io: https://www.linkedin.com/jobs/search/?currentJobId=3789877020&f_AL=true&geoId=92000000&keywords=software%20engineer&location=Worldwide"

    # Extract the job ID from the text
    for example_text in [example_text1, example_text2, example_text3, example_text4]:
        job_id = extract_job_id_from_text(example_text)
        if job_id:
            # Scrape the job details
            job_title, job_description, company_name = scrape_linkedin_job(job_id)
            print(f"Job Title: {job_title}")
            print(f"Job Description: {job_description}")
            print(f"Company Name: {company_name}")
            print()
        else:
            print("No LinkedIn job ID found in the text.")