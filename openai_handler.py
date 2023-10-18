import os
import openai
from dotenv import load_dotenv, find_dotenv

class Openai:
    def __init__(self):
        # Load the .env file
        load_dotenv(find_dotenv())

        # Get the OpenAI API credentials from environment variables
        self.api_key = str(os.getenv('OPENAI_API_KEY'))
        self.model = str(os.getenv('OPENAI_MODEL'))

        # Set the OpenAI API key
        openai.api_key = self.api_key


    def query_prompt(self,prompt:str) -> str:
        '''
        Description: Query the OpenAI API
        Input: prompt (str)
        Output: A string of the results
        '''

        messages = [{'role': 'user', 'content': prompt}]
        response = openai.ChatCompletion.create(
            model = self.model,
            messages = messages,
            temperature = 0,
        )
        return response.choices[0].message["content"] # type: ignore
    
   


