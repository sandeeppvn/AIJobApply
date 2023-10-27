from src.job_processor import JobProcessor


def aijobapply_cli():
    """
    Command-line interface function for AI job application process.
    """
    processor = JobProcessor()
    processor.process_jobs()
