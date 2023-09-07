""" The script containing the entry point for the application. """
import asyncio
import os
from dotenv import load_dotenv
from confluence_extractor import ConfluenceExtractor, ConfluenceConfiguration
from document_uploader import DocumentUploader
import json

# Load environment variables from .env file
load_dotenv()

def main():
    """ The main entry point for the confluence_extractor application. """

    #Get specific environment variables
    brain = os.getenv('BRAIN')
    print(f"Brain: {brain}")

    # Note: The Quivr API key expires in 24 hours. You will need to update it.
    quivr_api_key = os.getenv('QUIVR_API_KEY')
    quivr_backend_url = os.getenv('QUIVR_BACKEND_URL')

    user_path = get_user_path()

    generate_metadata(user_path, brain)

    # Create a DocumentUploader object
    uploader = DocumentUploader(quivr_api_key, quivr_backend_url)
    uploader.process_directory(user_path)


def get_user_path():
    user_path = input("Geef het pad op (bijv. /Users/quintenmeijboom/Documents/Repos): ")
    return user_path


def generate_metadata(path, brain):
    metadata_file_path = os.path.join(path, "__metadata__.jsonl")
    with open(metadata_file_path, "w", encoding='utf-8') as metadata_file:
        for root, _, files in os.walk(path):
            for file_name in files:
                if file_name == "__metadata__.jsonl":
                    continue

                # Check of het bestand een .docx extensie heeft
                if file_name.endswith('.docx'):
                    file_path = os.path.join(root, file_name)
                    metadata = {
                        "file_path": file_path,
                        "auteur": "Quinten",
                        "brain_id": brain
                    }
                    metadata_line = json.dumps(metadata)
                    metadata_file.write(f"{metadata_line}\n")



if __name__ == '__main__':
    main()
