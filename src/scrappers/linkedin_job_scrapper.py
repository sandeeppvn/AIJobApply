import os
import re
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()


def scrape_linkedin_job(linkedin_url: str) -> Dict:
    """
    Scrape LinkedIn job details from a given LinkedIn job URL.

    Parameters:
    -----------
    linkedin_url: str
        LinkedIn job URL to scrape job details from.

    Returns:
    --------
    Dict
        Dictionary containing job details.
    """

    job_id = re.search(r"/jobs/view/(\d+)", linkedin_url)

    if job_id:
        job_id = job_id.group(1)
    else:
        job_id = re.search(r"currentJobId=(\d+)", linkedin_url)
        if job_id:
            job_id = job_id.group(1)
        else:
            return {"Error": "Invalid LinkedIn job URL"}

    url = os.getenv("LINKEDIN_SCRAPPER_API_KEY")
    api_key = os.getenv("LINKEDIN_SCRAPPER_API_KEY")
    params = {
        "api_key": api_key,
        "job_id": job_id
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"Error": f"Request failed with status code: {response.status_code}"}

    job = response.json()[0]
    job_details = {
        "Position": job["job_position"],
        "Company Name": job["company_name"],
        "Description": job["job_description"],
        "Linkedin Contact": "",
        "Contact Name": job["recruiter_details"][0]["recruiter_name"] if job["recruiter_details"] else ""
    }

    return job_details