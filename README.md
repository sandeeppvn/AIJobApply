# AIJobApply

Automate your job application process using AI, Google Sheets, and Email services.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Google Sheets Setup](#google-sheets-setup)
- [Adding a Job](#adding-a-job)
- [Google API Credentials with OAuth 2.0](#google-api-credentials-with-oauth-20)
- [OpenAI API Setup](#openai-api-setup)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## Overview

`AIJobApply` simplifies and automates the job application process using cutting-edge technologies like OpenAI's GPT, Google Sheets for job management, and automated email services.

## Features

- **Automated Message Generation**: Uses OpenAI's GPT API to customize application messages.
- **Google Sheets Integration**: Manages job details and status updates.
- **Email Integration**: Sends out emails with customized messages.
- **Command-Line Interface**: Easy-to-use CLI for managing the application process.

## Prerequisites

- Python 3.8 or higher.
- OpenAI GPT API access.
- Google App Password

## Adding a Job (Optional)

A job can be added to the google sheet either manually or
you can use the RPI tool provided by Bardeen. This tool allows for a streamlined process of adding job listings through automation. For detailed instructions on how to use this tool, refer to the following Bardeen playbook: [LinkedIn Autobook](https://www.bardeen.ai/playbook/community/LinkedIn-5MfNwY4EcZLeK8GqTj).

## Google Service Account Setup

To access the Google Sheets API, you need to create a service account and obtain the credentials file.

1. **Google Cloud Console**: If you don't already have a Google Cloud account, sign up at [Google Cloud Console](https://console.cloud.google.com/).
2. **Create a Project**: Create a new project in the Google Cloud Console.
3. **Enable the Google Sheets API**: Navigate to the [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com) page and enable the API for your project.
4. **Enable the Google Drive API**: Navigate to the [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com) page and enable the API for your project.
5. **Create a Service Account**: Navigate to the [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) page and create a new service account for your project.
6. **Download Credentials**: After creating the service account, download the JSON credentials file. This file contains the necessary information to authenticate your application with the Google Sheets API.
7. **Set Environment Variable**: Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to the location of the credentials file.    This environment variable is used by the Google Cloud client libraries to authenticate requests to the API.

    For Unix-like systems (Linux, macOS):
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
    ```

    For Windows: (Command Prompt or PowerShell), use the following command for all subsequent commands in the same terminal session:

    ```bat
    set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\credentials.json
    ```

## Google Sheets Setup

For setting up your job application data, AIJobApply utilizes Google Sheets. To get started quickly, you can use our pre-defined template. Access the Google Sheets template here: [AIJobApply Google Sheets Template](<https://docs.google.com/spreadsheets/d/1BQZXJg6gOo1LbHZPa-0wgOvPC1_yl8piH_L4TY5rL-Q/edit?usp=sharing>).

To make a copy of the template, click on `File` > `Make a copy`. This will create a copy of the template in your Google Drive. Name the copy as AIJobApply

You need to provide the sheet access to the service account created. To do this, click on `Share` and add the email address of the service account.
Open the credentials.json file and copy the client_email value and paste it in the `Add people and groups` section.
Ensure that the service account has `Editor` access to the sheet.


## OpenAI API Setup

To utilize the OpenAI GPT API for message generation, follow these steps to obtain an API key:

1. **OpenAI Account**: If you don't already have an OpenAI account, sign up at [OpenAI](https://openai.com/).
2. **API Access**: Once logged in, navigate to the API section.
3. **Create an API Key**: Follow the instructions to create a new API key.
4. **Secure the API Key**: Store your API key securely. It's recommended to use environment variables for accessing the API key in your application.
    
    ```bash
    export OPENAI_URL=https://api.openai.com/v1/
    export OPENAI_API_KEY=your_openai_api_key
    ```

## Gmail Setup

To send emails using the Gmail service.

- If you are not using 2FA, you can use your regular Gmail password. 

- If you are using 2FA, you need to set up an App Password. Follow these steps to generate an App Password:

1. **Google Account**: If you don't already have a Google account, sign up at [Google](https://accounts.google.com/signup).
2. **App Password**: Navigate to the [App Passwords](https://myaccount.google.com/apppasswords) section of your Google account.
3. **Generate Password**: Select `Mail` and `Other` from the dropdown menus. Enter a name for the application and click `Generate`.
4. **Secure the Password**: Store your App Password securely. It's recommended to use environment variables for accessing the App Password in your application.
    
        ```bash
        export GMAIL_ADDRESS=your_gmail_address
        export GMAIL_PASSWORD=your_gmail_application_password
        ```

## LinkedIn Setup

To send LinkedIn connection requests and messages, you need to provide your LinkedIn credentials.

```bash
export LINKEDIN_USERNAME=your_linkedin_username
export LINKEDIN_PASSWORD=your_linkedin_password
```

## Templates Setup

Create a folder named 'templates'. Inside this folder, add the following templates:

1. **cover_letter_template.pdf**: A PDF file containing your cover letter template. This will be used as a base for generating customized cover letters.
2. **resume_template.pdf**: A PDF file containing your resume template. This will be used as a base for generating customized resumes.
3. **email_template.pdf**: A PDF file containing your email template. This will be used as a base for generating customized emails and LinkedIn messages.
4. **linkedin_note_template.pdf**: A PDF file containing your LinkedIn note template. This will be used as a base for generating customized LinkedIn notes when sending connection requests.

Set the environment variable `TEMPLATES_PATH` to the path of the templates folder.

```bash
export TEMPLATES_PATH=path_to_your_templates_folder
```

### Security Warning

⚠️ **Important**: Be cautious with sensitive information such as API keys, usernames, and passwords. Avoid storing them in scripts or files that might be shared or committed to version control. It's always safer to use more secure methods for managing sensitive environment variables, such as a secure vault service or encrypted files.

## Installation

(Optional but Recommended) Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

### Install from PyPI
```bash
pip install aijobapply
```

### Install from Source
```bash
git clone https://github.com/sandeeppvn/AIJobApply.git
cd AIJobApply
pip install -e .
export PYTHONPATH=$(pwd)
```

## Usage
After installation, the application can be run using the `aijobapply` command.
If the environment variables are set correctly, you can run the application using the following command:
```bash
aijobapply
```

Alternatively, if you want to run the application without setting environment variables, you can pass the required credentials as command line arguments:
```bash
aijobapply --openai-api-key your_openai_api_key --gmail_address your_gmail_address --gmail-password your_gmail_application_password --linkedin_username your_linkedin_username --linkedin_password your_linkedin_password --templates_path path_to_your_templates_folder --google_credentials path_to_your_google_credentials_file --gsheet_name your_google_sheet_name --selenium_driver_path path_to_your_selenium_driver --model your_openai_model_name
```

Additional command line arguments are available. Use --help to see all options and their descriptions:
```bash
aijobapply --help
```

## Selenium Driver Setup

To automate the LinkedIn connection request and message sending process, you need to download the appropriate Selenium driver for your browser. The Selenium driver is used by the Selenium Python library to automate the browser actions.
Currently, the following Selenium drivers are supported:
- Chrome: [ChromeDriver](https://chromedriver.chromium.org/downloads)

Download the appropriate driver for your browser and set the environment variable `SELENIUM_DRIVER_PATH` to the path of the driver executable.

```bash