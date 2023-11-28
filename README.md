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

## Project Structure

### Core Modules

- **`main.py`**: Entry point for the program. Triggers the job application process.
- **`job_processor.py`**: Manages job processing, filtering, and updating.
- **`email_handler.py`**: Handles email functionalities.
- **`google_api_handler.py`**: Interacts with Google APIs.
- **`openai_handler.py`**: Facilitates interactions with the OpenAI API.
- **`utils.py`**: Provides utility functions.

### Additional Directories

- **`tests`**: Contains unit tests.
- **`templates`**: Job application templates.

## Prerequisites

- Python 3.6 or higher.
- OpenAI GPT API access.
- Google API credentials.

## Adding a Job

A job can be added to the google sheet either manually or
you can use the RPI tool provided by Bardeen. This tool allows for a streamlined process of adding job listings through automation. For detailed instructions on how to use this tool, refer to the following Bardeen playbook: [LinkedIn Autobook](https://www.bardeen.ai/playbook/community/LinkedIn-5MfNwY4EcZLeK8GqTj).

## Google Sheets Setup

For setting up your job application data, AIJobApply utilizes Google Sheets. To get started quickly, you can use our pre-defined template. Access the Google Sheets template here: [AIJobApply Google Sheets Template](<https://docs.google.com/spreadsheets/d/1BQZXJg6gOo1LbHZPa-0wgOvPC1_yl8piH_L4TY5rL-Q/edit?usp=sharing>).

Ensure that you follow the structure of the template to avoid any issues with data processing in AIJobApply.

## Google API Credentials with OAuth 2.0

To interact with Google Sheets from the application, you'll need to set up OAuth 2.0 credentials, which allow the application to access your Google Sheets on your behalf:

1. **Google Cloud Console**: Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. **Create a New Project**: If you haven’t already, create a new project.
3. **Enable Google Sheets API**: In your project, navigate to 'APIs & Services' > 'Dashboard' and enable the Google Sheets API.
4. **Configure OAuth Consent Screen**:
   - Go to 'OAuth consent screen' and select an appropriate user type (usually 'External').
   - Fill in the necessary details like Application name, User support email, and Developer contact information.
   - Add the scopes for the Google Sheets API (e.g., `https://www.googleapis.com/auth/spreadsheets`).
5. **Create OAuth 2.0 Credentials**:
   - Go to 'Credentials' and click 'Create Credentials'.
   - Choose 'OAuth client ID'.
   - For the application type, select 'Desktop app' or another appropriate type.
   - Name your OAuth 2.0 client and click 'Create'.
6. **Download the Credentials**:
   - Once your OAuth client is created, click the download button to download the JSON file containing your client ID and client secret.
   - This file is used by your application to authenticate via OAuth 2.0.

7. **Using the Credentials in AIJobApply**:
   - Store your downloaded JSON file securely.
   - When you run the AIJobApply application for the first time, it will prompt you to authorize access to your Google Sheets. Follow the instructions to complete the OAuth flow.

Remember to never share your OAuth credentials publicly.

## OpenAI API Setup

To utilize the OpenAI GPT API for message generation, follow these steps to obtain an API key:

1. **OpenAI Account**: If you don't already have an OpenAI account, sign up at [OpenAI](https://openai.com/).
2. **API Access**: Once logged in, navigate to the API section.
3. **Create an API Key**: Follow the instructions to create a new API key.
4. **Secure the API Key**: Store your API key securely. It's recommended to use environment variables for accessing the API key in your application.


## Installation

Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```


Clone the repository:

```bash
git clone https://github.com/your-repository/AIJobApply.git
cd AIJobApply
```

Install the package:

```bash
pip install -e .
```

Add to PATH variable if necessary.

## Configuration

Set up environment variables for API keys and credentials in the .env file. 

Modify templates in the templates directory as per your requirements.

## Usage

After installation, the package provides a CLI. Run the application with:
```bash
aijobapply --templates_path "path/to/templates" --gsheet_name "Your Google Sheet Name"
```

Additional command line arguments are available. Use --help to see all options.
