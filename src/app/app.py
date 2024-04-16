from typing import Dict

import gradio as gr

from src.scrappers.linkedin_job_scrapper import scrape_linkedin_job


def process_job(linkedin_url: str) -> Dict:

    # Extract Job Content from the URL
    job_details = scrape_linkedin_job(linkedin_url)

    

    return job_details


interface = gr.Interface(fn=process_job,
                         inputs="text",
                         outputs="text",
                         title="LinkedIn Job Scraper",
                         description="Enter a LinkedIn job URL to get job details displayed in a table.")
interface.launch()

# Run the function with a sample LinkedIn URL
# scrape_linkedin_job("https://www.linkedin.com/jobs/search/?currentJobId=3890975969&keywords=machine%20learning&origin=SUGGESTION")