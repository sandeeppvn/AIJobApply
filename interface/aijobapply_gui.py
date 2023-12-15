import json
import os
import platform
import subprocess
import tkinter as tk
from threading import Thread
from tkinter import filedialog, scrolledtext, ttk

from fpdf import FPDF

CACHE_FILE = "aijobapply_cache.json"
TEMPLATES_FOLDER = "templates"

def select_file(entry):
    path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, path)

def save_cache(data):
    with open(CACHE_FILE, "w") as file:
        json.dump(data, file)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    return {}

def create_pdf_from_text(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    if not os.path.exists(TEMPLATES_FOLDER):
        os.makedirs(TEMPLATES_FOLDER)
    pdf.output(os.path.join(TEMPLATES_FOLDER, filename))

def populate_fields_from_cache():
    cached_data = load_cache()
    openai_key_entry.insert(0, cached_data.get("OPENAI_API_KEY", ""))
    gmail_address_entry.insert(0, cached_data.get("GMAIL_ADDRESS", ""))
    gmail_password_entry.insert(0, cached_data.get("GMAIL_PASSWORD", ""))
    google_cred_file_entry.insert(0, cached_data.get("GOOGLE_API_CREDENTIALS_FILE", ""))
    google_sheet_name_entry.insert(0, cached_data.get("GOOGLE_SHEET_NAME", ""))
    chromedriver_path_entry.insert(0, cached_data.get("CHROMEDRIVER_PATH", ""))
    linkedin_username_entry.insert(0, cached_data.get("LINKEDIN_USERNAME", ""))
    linkedin_password_entry.insert(0, cached_data.get("LINKEDIN_PASSWORD", ""))
    # Templates path is absolute path of the TEMPLATE_FOLDER
    templates_path = os.path.abspath(TEMPLATES_FOLDER)
    resume_file_entry.insert(0, os.path.join(templates_path, "resume_template.pdf"))
    cover_letter_file_entry.insert(0, os.path.join(templates_path, "cover_letter_template.pdf"))
    email_content_text.insert("1.0", cached_data.get("email_content", ""))
    linkedin_note_text.insert("1.0", cached_data.get("linkedin_note", ""))


def run_aijobapply(output_text):
    data = {
        "TEMPLATES_PATH": os.path.abspath(TEMPLATES_FOLDER),
        "GMAIL_ADDRESS": gmail_address_entry.get(),
        "GMAIL_PASSWORD": gmail_password_entry.get(),
        "GOOGLE_API_CREDENTIALS_FILE": google_cred_file_entry.get(),
        "GOOGLE_SHEET_NAME": google_sheet_name_entry.get(),
        "OPENAI_URL": "https://api.openai.com/v1/",
        "OPENAI_API_KEY": openai_key_entry.get(),
        "OPENAI_MODEL": "gpt-4-0613",  # Replace with actual model name if different
        "CHROMEDRIVER_PATH": chromedriver_path_entry.get(),
        "LINKEDIN_USERNAME": linkedin_username_entry.get(),
        "LINKEDIN_PASSWORD": linkedin_password_entry.get(),
        "email_content": email_content_text.get("1.0", "end-1c"),
        "linkedin_note": linkedin_note_text.get("1.0", "end-1c")
    }

    save_cache(data)

    # Save PDFs
    create_pdf_from_text(data["email_content"], "email_template.pdf")
    create_pdf_from_text(data["linkedin_note"], "linkedin_note_template.pdf")

    # Construct and run the command
    command = [
        "aijobapply",
        "--OPENAI_API_KEY", data["OPENAI_API_KEY"],
        "--GMAIL_ADDRESS", data["GMAIL_ADDRESS"],
        "--GMAIL_PASSWORD", data["GMAIL_PASSWORD"],
        "--GOOGLE_API_CREDENTIALS_FILE", data["GOOGLE_API_CREDENTIALS_FILE"],
        "--GOOGLE_SHEET_NAME", data["GOOGLE_SHEET_NAME"],
        "--OPENAI_URL", data["OPENAI_URL"],
        "--OPENAI_MODEL", data["OPENAI_MODEL"],
        "--CHROMEDRIVER_PATH", data["CHROMEDRIVER_PATH"],
        "--LINKEDIN_USERNAME", data["LINKEDIN_USERNAME"],
        "--LINKEDIN_PASSWORD", data["LINKEDIN_PASSWORD"],
        "--TEMPLATES_PATH", data["TEMPLATES_PATH"]
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                               shell=True if platform.system() == "Windows" else False, 
                               text=True, bufsize=1)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            output_text.insert(tk.END, output)
            output_text.see(tk.END)

def submit():
    Thread(target=run_aijobapply, args=(output_text,)).start()

# Load cached data
cached_data = load_cache()

# GUI Setup
root = tk.Tk()
root.title("AIJobApply Configuration")
root.configure(background='#ECECEC')

style = ttk.Style()
style.configure("TLabel", background="#ECECEC", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10, "bold"))
style.configure("TEntry", font=("Arial", 10))

# Create input fields and labels
openai_key_label = ttk.Label(root, text="OpenAI API Key", style="TLabel")
openai_key_entry = ttk.Entry(root, width=30)
openai_key_entry.insert(0, cached_data.get("openai_api_key", ""))
gmail_address_label = ttk.Label(root, text="Gmail Address", style="TLabel")
gmail_address_entry = ttk.Entry(root, width=30)
gmail_address_entry.insert(0, cached_data.get("gmail_address", ""))
gmail_password_label = ttk.Label(root, text="Gmail Password", style="TLabel")
gmail_password_entry = ttk.Entry(root, show="*", width=30)
gmail_password_entry.insert(0, cached_data.get("gmail_password", ""))
google_cred_file_label = ttk.Label(root, text="Google Credentials File", style="TLabel")
google_cred_file_entry = ttk.Entry(root, width=30)
google_cred_file_entry.insert(0, cached_data.get("google_credentials_file", ""))
google_cred_button = ttk.Button(root, text="Select File", command=lambda: select_file(google_cred_file_entry))
google_sheet_name_label = ttk.Label(root, text="Google Sheet Name", style="TLabel")
google_sheet_name_entry = ttk.Entry(root, width=30)
google_sheet_name_entry.insert(0, cached_data.get("google_sheet_name", ""))
chromedriver_path_label = ttk.Label(root, text="Chromedriver Path", style="TLabel")
chromedriver_path_entry = ttk.Entry(root, width=30)
chromedriver_path_entry.insert(0, cached_data.get("chromedriver_path", ""))
chromedriver_button = ttk.Button(root, text="Select File", command=lambda: select_file(chromedriver_path_entry))
linkedin_username_label = ttk.Label(root, text="LinkedIn Username", style="TLabel")
linkedin_username_entry = ttk.Entry(root, width=30)
linkedin_username_entry.insert(0, cached_data.get("linkedin_username", ""))
linkedin_password_label = ttk.Label(root, text="LinkedIn Password", style="TLabel")
linkedin_password_entry = ttk.Entry(root, show="*", width=30)
linkedin_password_entry.insert(0, cached_data.get("linkedin_password", ""))

resume_file_label = ttk.Label(root, text="Resume File Path", style="TLabel")
resume_file_entry = ttk.Entry(root, width=30)
resume_file_entry.insert(0, cached_data.get("resume_file", ""))
resume_file_button = ttk.Button(root, text="Select File", command=lambda: select_file(resume_file_entry))

cover_letter_file_label = ttk.Label(root, text="Cover Letter File Path", style="TLabel")
cover_letter_file_entry = ttk.Entry(root, width=30)
cover_letter_file_entry.insert(0, cached_data.get("cover_letter_file", ""))
cover_letter_file_button = ttk.Button(root, text="Select File", command=lambda: select_file(cover_letter_file_entry))

email_content_label = ttk.Label(root, text="Email Content", style="TLabel")
email_content_text = scrolledtext.ScrolledText(root, height=4, width=30)
email_content_text.insert("1.0", cached_data.get("email_content", ""))

linkedin_note_label = ttk.Label(root, text="LinkedIn Note", style="TLabel")
linkedin_note_text = scrolledtext.ScrolledText(root, height=4, width=30)
linkedin_note_text.insert("1.0", cached_data.get("linkedin_note", ""))

populate_fields_from_cache()

# Create submit button
submit_button = ttk.Button(root, text="Submit", command=submit)

# Layout widgets
openai_key_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
openai_key_entry.grid(row=0, column=1, padx=5, pady=5)
gmail_address_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
gmail_address_entry.grid(row=1, column=1, padx=5, pady=5)
gmail_password_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
gmail_password_entry.grid(row=2, column=1, padx=5, pady=5)
google_cred_file_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
google_cred_file_entry.grid(row=3, column=1, padx=5, pady=5)
google_cred_button.grid(row=3, column=2, padx=5, pady=5)
google_sheet_name_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
google_sheet_name_entry.grid(row=4, column=1, padx=5, pady=5)
chromedriver_path_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
chromedriver_path_entry.grid(row=5, column=1, padx=5, pady=5)
chromedriver_button.grid(row=5, column=2, padx=5, pady=5)
linkedin_username_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)
linkedin_username_entry.grid(row=6, column=1, padx=5, pady=5)
linkedin_password_label.grid(row=7, column=0, sticky="w", padx=5, pady=5)
linkedin_password_entry.grid(row=7, column=1, padx=5, pady=5)
resume_file_label.grid(row=8, column=0, sticky="w", padx=5, pady=5)
resume_file_entry.grid(row=8, column=1, padx=5, pady=5)
resume_file_button.grid(row=8, column=2, padx=5, pady=5)
cover_letter_file_label.grid(row=9, column=0, sticky="w", padx=5, pady=5)
cover_letter_file_entry.grid(row=9, column=1, padx=5, pady=5)
cover_letter_file_button.grid(row=9, column=2, padx=5, pady=5)
email_content_label.grid(row=10, column=0, sticky="w", padx=5, pady=5)
email_content_text.grid(row=10, column=1, columnspan=2, padx=5, pady=5)
linkedin_note_label.grid(row=11, column=0, sticky="w", padx=5, pady=5)
linkedin_note_text.grid(row=11, column=1, columnspan=2, padx=5, pady=5)


# Create submit button
submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.grid(row=12, column=0, columnspan=3, padx=5, pady=5)

# Output Text Section
output_text = scrolledtext.ScrolledText(root, height=10)
output_text.grid(row=13, column=0, columnspan=3, padx=5, pady=5)


# Run the application
root.mainloop()
