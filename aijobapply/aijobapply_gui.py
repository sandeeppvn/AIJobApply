import json
import os
import tkinter as tk
from re import T
from threading import Thread
from tkinter import filedialog, messagebox, scrolledtext, ttk

import docx

from aijobapply.main import run_application

# Constants
CACHE_FILE = "aijobapply_cache.json"
TEMPLATES_FOLDER = "templates"

class AIJobApplyGUI:
    def __init__(self, root):
        self.root = root
        self.setup_style()
        self.create_widgets()
        self.load_cache()

    def setup_style(self):
        style = ttk.Style()
        style.configure("TLabel", background="#ECECEC", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TEntry", font=("Arial", 10))

    def create_widgets(self):
        self.entries = {}

        # Title
        title = ttk.Label(self.root, text="AIJobApply Configuration", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, sticky="ew", padx=5, pady=5, columnspan=2)

        # Configure sections_frame to expand with content
        sections_frame = ttk.Frame(self.root)
        sections_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        sections_frame.grid_columnconfigure(0, weight=1)
        sections_frame.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create Sections
        self.create_sections(sections_frame)

        # Submit button and Output text area
        self.create_submit_button()
        self.create_output_text_area()

    def create_sections(self, frame):
        # Section Definitions
        sections = {
            "Gmail": {
                "start_row": 0,
                "start_column": 0,
                "fields": {
                    "Gmail Address": ["GMAIL_ADDRESS", "text"],
                    "Gmail Password": ["GMAIL_PASSWORD", "password"],
                    "Email Content": ["EMAIL_CONTENT", "text_area"]
                },
                "use_checkbox": True
            },
            "LinkedIn": {
                "start_row": 0,
                "start_column": 1,
                "fields": {
                    "Chromedriver Path": ["CHROMEDRIVER_PATH", "select_file"],
                    "LinkedIn Username": ["LINKEDIN_USERNAME", "text"],
                    "LinkedIn Password": ["LINKEDIN_PASSWORD", "password"],
                    # "LinkedIn Note": ["LINKEDIN_NOTE", "text_area"]
                },
                "use_checkbox": True
            },
            "Credentials": {
                "start_row": 1,
                "start_column": 0,
                "fields": {
                    "Google API Credentials File": ["GOOGLE_API_CREDENTIALS_FILE", "select_file"],
                    "Google Sheet Name": ["GOOGLE_SHEET_NAME", "text"],
                    "LLM API Key": ["LLM_API_KEY", "text"],
                    "LLM Model": ["LLM_MODEL", "text"],
                    "LLM API URL": ["LLM_API_URL", "text"]
                },
                "use_checkbox": False
            },
            "Documents": {
                "start_row": 1,
                "start_column": 1,
                "fields": {
                    "Resume File": ["RESUME_PATH", "select_file"],
                    "Resume Summary": ["RESUME_PROFESSIONAL_SUMMARY", "text_area"],
                    "Cover Letter File": ["COVER_LETTER_PATH", "select_file"]
                },
                "use_checkbox": False
            }
        }

        # Create each section
        for title, config in sections.items():
            section = self.create_section(title, frame, config["start_row"], config["start_column"])
            self.create_section_fields(config["fields"], section, config["use_checkbox"])



    def create_section(self, title: str, parent: ttk.Frame, start_row: int, start_column: int):
        section = ttk.LabelFrame(parent, text=title)
        section.grid(row=start_row, column=start_column, sticky="nsew", padx=10, pady=5)
        section.grid_columnconfigure(1, weight=1)  # Make sure the entry fields expand
        return section
    
    def create_section_fields(self, fields: dict, frame: ttk.LabelFrame, use_checkbox: bool = False):
        """
        Creates the fields for the given section.
        Parameters:
            fields: A dictionary mapping field names to field types.
                - Field types can be one of the following:
                    - "text": A text entry field
                    - "password": A password entry field
                    - "text_area": A text area field
                    - "select_file": A text entry field with a button to select a file
            frame: The frame to place the fields in.
            use_checkbox: Whether or not to include a checkbox for the section. This is used to toggle the visibility of the section.
        """

        def toggle_section():
            """Toggles the visibility of the fields in the given section."""
            children = frame.winfo_children()[1:]  # Skip the first child, which is assumed to be the "Use LinkedIn" checkbox.

            if var.get():
                for child in children:
                    child.grid()
            else:
                for child in children:
                    child.grid_remove()

        if use_checkbox:
            var = tk.BooleanVar()
            var.set(True)
            checkbox = ttk.Checkbutton(frame, text=f"Use {frame['text']}", variable=var, command=toggle_section)
            checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.entries[f"USE_{frame['text'].upper()}"] = var  # Store the checkbox variable


        # Create the fieldsx
        row = 1 if use_checkbox else 0
        for label_text, field in fields.items():
            field_name, field_type = field
            label = ttk.Label(frame, text=label_text)
            label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            if field_type in ["text", "password", "select_file"]:
                entry = ttk.Entry(frame)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                if field_type == "password":
                    entry.config(show="*")
                if field_type == "select_file":
                    button = ttk.Button(frame, text="Select File", command=lambda entry=entry: self.select_file(entry))
                    button.grid(row=row, column=2, padx=5, pady=5, sticky="ew")
            elif field_type == "text_area":
                entry = scrolledtext.ScrolledText(frame, height=10)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                button = ttk.Button(frame, text="Select File", command=lambda e=entry: self.insert_file_content(e))
                button.grid(row=row, column=2, padx=5, pady=5)
            elif field_type == "checkbox":
                entry = ttk.Checkbutton(frame, text="Interactive Mode")
                entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")
                entry.state(["!alternate"])

            self.entries[field_name] = entry
            row += 1


    def insert_file_content(self, text_widget):
        """Inserts the content of a selected file into a text widget."""
        path = filedialog.askopenfilename()
        if path:
            try:
                # Ensure the file is .docx only
                if not path.endswith(".docx"):
                    messagebox.showerror("Invalid File", "Only .docx files are supported.")
                    return
                
                # Get the content of the file
                content = "\n".join([paragraph.text for paragraph in docx.Document(path).paragraphs])

                # Insert the content into the text widget
                text_widget.delete("1.0", "end-1c")
                text_widget.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file: {e}")            
                

    def create_submit_button(self):
        # Place the submit button below all sections
        self.submit_button = ttk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


    def create_output_text_area(self):
        # Place the output text area below the submit button
        self.output_text = scrolledtext.ScrolledText(self.root, height=10)
        self.output_text.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as file:
                cached_data = json.load(file)
                for field_name, widget in self.entries.items():
                    if isinstance(widget, tk.Entry):
                        widget.insert(0, cached_data.get(field_name, ""))
                    elif isinstance(widget, scrolledtext.ScrolledText):
                        widget.insert("1.0", cached_data.get(field_name, ""))
                    elif isinstance(widget, tk.Checkbutton):
                        widget.state(["!alternate"] if cached_data.get(field_name, False) else ["alternate"])

    @staticmethod
    def select_file(entry):
        path = filedialog.askopenfilename()
        if path:  # Only update the entry if a file was selected
            entry.delete(0, tk.END)
            entry.insert(0, path)


    def submit(self):
        Thread(target=self.run_aijobapply, args=(self.output_text,)).start()

    def run_aijobapply(self, output_text):
        data = {field: (entry.get() if isinstance(entry, tk.Entry) else entry.get("1.0", "end-1c")) 
                for field, entry in self.entries.items() if not isinstance(entry, tk.BooleanVar)}
        
        # Add checkbox states to data
        for field, entry in self.entries.items():
            if isinstance(entry, tk.BooleanVar):
                data[field] = entry.get()

        self.save_cache(data)

        # Construct and run the command
        gmail_commands = {
            "GMAIL_ADDRESS": data["GMAIL_ADDRESS"],
            "GMAIL_PASSWORD": data["GMAIL_PASSWORD"],
            # "EMAIL_CONTENT": data["EMAIL_CONTENT"],
        }
        linkedin_commands = {
            "CHROMEDRIVER_PATH": data["CHROMEDRIVER_PATH"],
            "LINKEDIN_USERNAME": data["LINKEDIN_USERNAME"],
            "LINKEDIN_PASSWORD": data["LINKEDIN_PASSWORD"],
            # "LINKEDIN_NOTE": data["LINKEDIN_NOTE"],
            "INTERACTIVE": data["INTERACTIVE"] if "INTERACTIVE" in data else "False",
        }
        main_commands = {
            "GOOGLE_API_CREDENTIALS_FILE": data["GOOGLE_API_CREDENTIALS_FILE"],
            "GOOGLE_SHEET_NAME": data["GOOGLE_SHEET_NAME"],
            "LLM_API_KEY": data["LLM_API_KEY"],
            "LLM_MODEL": data["LLM_MODEL"],
            "LLM_API_URL": data["LLM_API_URL"],
            "RESUME_PATH": data["RESUME_PATH"],
            "RESUME_PROFESSIONAL_SUMMARY": data["RESUME_PROFESSIONAL_SUMMARY"] if "RESUME_PROFESSIONAL_SUMMARY" in data else "",
            "COVER_LETTER_PATH": data["COVER_LETTER_PATH"],
        }

        if data.get("USE_GMAIL", False):
            main_commands.update(gmail_commands)
            main_commands["USE_GMAIL"] = True
            
        if data.get("USE_LINKEDIN", False):
            main_commands.update(linkedin_commands)
            main_commands["USE_LINKEDIN"] = True
            if data.get("INTERACTIVE", False):
                main_commands["INTERACTIVE"] = True

        run_application(main_commands)

    @staticmethod
    def save_cache(data):
        with open(CACHE_FILE, "w") as file:
            json.dump(data, file)

def main():
    root = tk.Tk()
    root.title("AIJobApply Configuration")
    root.configure(background='#ECECEC')

    # Set the window to open in full screen by default
    root.attributes('-fullscreen', True)

    app = AIJobApplyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
