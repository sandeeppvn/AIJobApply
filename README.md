# AIJobApply

Automate your job application process using AI, Notion, and Email services.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
  - [Core Modules](#core-modules)
  - [Documents](#documents)
  - [Additional Directories](#additional-directories)
- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

## Overview

`AIJobApply` is designed to simplify and automate the job application process using cutting-edge technologies and services.

## Project Structure

### Core Modules

- **`main.py`**: Entry point for the program. Triggers the job application process.
- **`job_processor.py`**: Manages job processing, filtering, and updating.
- **`email_handler.py`**: Handles email functionalities.
- **`notion_handler.py`**: Interacts with Notion databases.
- **`openai_handler.py`**: Facilitates interactions with the OpenAI API.
- **`utils.py`**: Provides utility functions for reading templates and sending emails.

### Documents

Templates used for job applications:

- **Cover Letter**: `cover_letter_template.pdf`
- **Resume**: `resume_template.pdf`
- **Email**: `email_template.pdf`

### Additional Directories

- **`tests`**: Contains unit tests.
- **`legacy`**: Older versions or deprecated code.

## Dependencies

- **Requests**: HTTP requests.
- **Pandas**: Data manipulation.
- **Flask**: Web framework.
- **Selenium**: Web testing.
- **Chromedriver-Binary**: Selenium WebDriver.
- **OpenAI**: OpenAI API client.
- **PyPDF2**: PDF manipulation.
- **TQDM**: Progress bars.


## Getting Started

Follow these steps to install and use `AIJobApply`:

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your_username/AIJobApply.git
    ```
2. Navigate to the project directory:
    ```bash
    cd AIJobApply
    ```
3. Install the project as a package:
    ```bash
    pip install .
    ```

### Configuration


Certainly! I'll add steps to modify the template files within the "Configuration" section of the README.md.

markdown
Copy code
### Configuration

1. **Environment Variables**:
    - Rename the `.env.example` file (if it exists) to `.env`.
    - Open the `.env` file and modify the environment variables with your credentials and settings. For example:
        ```env
        NOTION_API_KEY=YOUR_NOTION_API_KEY
        OPENAI_API_KEY=YOUR_OPENAI_API_KEY
        GMAIL_ADDRESS=YOUR_GMAIL_ADDRESS
        GMAIL_PASSWORD=YOUR_GMAIL_PASSWORD
        ```
        (No spaces around the =, dont use quotes)
2. **Modify Templates**:
    - Navigate to the `documents` directory.
    - Modify the template files as per your requirements:
        - `cover_letter_template.pdf`: Update with your preferred cover letter format.
        - `resume_template.pdf`: Replace with your resume template.
        - `email_template.pdf`: Adjust the email format to your liking.

### Usage

Once installed and configured, you can run the AI job application process from the command line using:
    ```bash
    aijobapply
    ```

