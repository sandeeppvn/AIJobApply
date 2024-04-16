import logging

import docx

logger = logging.getLogger(__name__)
def get_file_content(path: str) -> str:
    """Get the content of a file."""
    try:
        # Ensure the file is .docx only
        if not path.endswith((".docx")):
            raise ValueError("Only .docx files are supported.")

        # Read the entire docx file as a string
        doc = docx.Document(path)
        content = "".join([paragraph.text for paragraph in doc.paragraphs])
        return content
    except Exception as e:
        logger.exception(f"Error reading file: {e}")
        return ""