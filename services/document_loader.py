# document_loader.py
from llama_index.core import SimpleDirectoryReader, Document
import json
import os


class DocumentLoader:
    def __init__(self):
        self.supported_formats = {'.txt', '.pdf', '.json'}

    def load_documents(self, directory_path):
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")

        try:
            reader = SimpleDirectoryReader(
                input_dir=directory_path,
                filename_as_id=True,
                exclude_hidden=True
            )

            documents = reader.load_data()
            print(f"Successfully loaded {len(documents)} documents")
            return documents

        except Exception as e:
            print(f"Error loading documents: {str(e)}")
            return []
