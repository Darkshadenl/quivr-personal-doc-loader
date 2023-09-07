""" This module contains the DocumentUploader class. """
import os
import json
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt


class DocumentUploader:
    """ This class will upload documents to the backend. """

    def __init__(self, api_key, backend_url):
        self.api_key = api_key
        self.backend_url = backend_url

    def process_directory(self, content_dir):
        """ This method will process all files in the content directory. """
        metadata_file_path = os.path.join(content_dir, "__metadata__.jsonl")
        if os.path.isfile(metadata_file_path):
            with open(metadata_file_path, "r", encoding='utf-8') as metadata_file:
                for line in metadata_file:
                    json_object = json.loads(line)
                    file_path = json_object["file_path"]
                    try:
                        self.upload_file(file_path, json_object["brain_id"])
                    except Exception as err:  # pylint: disable=W0718
                        print(f"Failed to upload file {file_path}. Error: {err}")
        else:
            print("process dir exception")
            raise Exception("No __metadata__.jsonl file found in content directory.")  # pylint: disable=W0719

    @retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
    def upload_file(self, file_path, brain):
        """ This method will retry the upload 3 times if it fails."""

        filename = os.path.basename(file_path)
        print(filename)
        url = f"{self.backend_url}/upload"
        params = {'enable_summarization': 'false', 'brain_id': f'{brain}'}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json",
        }
        files = {
            'uploadFile': (filename, open(f'{file_path}', 'rb')),
        }

        try:
            response = requests.post(url, headers=headers, params=params, files=files, timeout=10)
            if response.status_code != 200:
                print(f"Server returned status {response.status_code}: {response.content.decode()}")
            response.raise_for_status()
        except requests.HTTPError as err:
            print(f"Failed to send file {filename}. Error: {err}")
            raise  # Re-raise the exception to trigger the retry
