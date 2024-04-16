import logging
import os
import re

import docx
import docxtpl
import pandas as pd

from src.handlers.google_drive_handler import GoogleDriveHandler

logger = logging.getLogger(__name__)

def create_job_folder(job:pd.Series, resume_path:str, google_drive_handler:GoogleDriveHandler, destination:str = "Job Applications"):
    """
    Create a folder for the job application process.
    Add relevant files to the folder.
    """
    # Create a folder for the job application
    # Name the folder as CompanyName_Position, no special characters or spaces. Add an underscore between company name and position
    company_name = re.sub(r"[^\w\s]", "", job["Company Name"])
    position = re.sub(r"\W+", "", job["Position"])
    job_name = f"{company_name}_{position}"
    job_folder = f"{destination}/{job_name}"
    if os.path.exists(job_folder):
        import shutil
        shutil.rmtree(job_folder)
    os.makedirs(job_folder, exist_ok=True)

    # Get the ID of the job folder (Creating the folder if it doesn't exist)
    job_folder_id = google_drive_handler.get_folder(job_name, google_drive_handler.job_root_folder_id)

    # Load the resume and replace jinja2 variables
    resume_variables = {
        "resume_professional_summary": job["Resume"],
    }
    resume = docxtpl.DocxTemplate(resume_path)
    resume.render(resume_variables)
    resume_file_path = os.path.join(job_folder, "Resume.docx")
    resume.save(resume_file_path)
    google_drive_handler.upload_file("Resume.docx", resume_file_path, job_folder_id)

    cover_letter_text = job["Cover Letter"]
    cover_letter_doc = docx.Document()
    cover_letter_doc.add_paragraph(cover_letter_text)
    cover_letter_file_path = os.path.join(job_folder, "Cover Letter.docx")
    cover_letter_doc.save(cover_letter_file_path)
    google_drive_handler.upload_file("Cover Letter.docx", cover_letter_file_path, job_folder_id)

    email = job["Message Subject"] + "\n\n" + job["Message Content"]
    email_file_path = os.path.join(job_folder, "Email.txt")
    with open(email_file_path, "w", encoding="utf-8") as file:
        file.write(email)
    google_drive_handler.upload_file("Email.txt", email_file_path, job_folder_id)

    linkedin_note = job["LinkedIn Note"]
    linkedin_note_file_path = os.path.join(job_folder, "LinkedIn Note.txt")
    with open(linkedin_note_file_path, "w", encoding="utf-8") as file:
        file.write(linkedin_note)
    google_drive_handler.upload_file("LinkedIn Note.txt", linkedin_note_file_path, job_folder_id)