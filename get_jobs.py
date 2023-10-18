from notion_handler import Notion

'''
Description: 
- This class gets all the jobs from the Notion database
'''
class NotionJobsClass(Notion):
    def __init__(self):
        # super(Notion, self).__init__()
        super().__init__()

    def get_jobs(self) -> dict:
        '''
        Description: Get all jobs from the Notion database where the checkbox "processed" is False
        Input: None
        Output: A dictionary of jobs with company name, job link, and job role
        '''

        # Set the query
        filter = {
            "filter": {
                "property": "processed",
                "checkbox": {
                    "equals": False
                }
            }
        }
        # Use jobs_id from the Notion class
        response = self.get_pages(self.jobs_id, filter)

        return response
