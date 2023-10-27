from notion_handler import Notion

'''
Description: 
- This class gets all the jobs from the Notion database
'''
class GetJobsClass(Notion):
    def __init__(self):
        # super(Notion, self).__init__()
        super().__init__()

    def get_jobs(self) -> dict:
        '''
        Description: Get all jobs from the Notion database where the status is "Saved", "Email Ready" or "Email Approved"
        Input: None
        Output: A dictionary of jobs with company name, job link, and job role
        '''

        # Set the query
        filter = {
            "filter": {
                "or": [
                    {
                        "property": "Status",
                        "select": {
                            "equals": "Saved"
                        }
                    },
                    {
                        "property": "Status",
                        "select": {
                            "equals": "Email Ready"
                        }
                    },
                    {
                        "property": "Status",
                        "select": {
                            "equals": "Email Approved"
                        }
                    }
                ]
            }
        }




        # Use jobs_id from the Notion class
        response = self.get_pages(self.jobs_id, filter)

        return response
