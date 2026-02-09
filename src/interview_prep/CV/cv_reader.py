from llama_index.readers.file import PDFReader
from interview_prep.utils.text_tools import normalize_text
from config import config
from pathlib import Path
from interview_prep.schemas.cv_schema import Document


import pymupdf


cfg = config

class CVReader:
    """A class to read and parse CVs from PDF files."""

    def __init__(self):
        pass
        

    def read_cv(self, file_path: str) -> str:
        """Read and extract text from a CV PDF file.

        Args:
            file_path (str): The path to the CV PDF file.
        """
        #create structured data dictionary
        structured_data = {}
        structured_data["category"] = "CV"
        structured_data["source"] = file_path


        pdf_path = Path(file_path)
    
        #for caching purpose
        file_name = pdf_path.stem
        text_file = file_name + ".txt"
        print("file name : ", file_name)
        print("text file name : ", text_file)
        if not pdf_path.exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        doc = pymupdf.open(file_path)
        text = ""
        for page in doc:

            text += page.get_text()
            
            normalized_text = normalize_text(text)
            structured_data["raw_text"] = text
            structured_data["normalized_text"] = normalized_text
            print(structured_data["raw_text"])
        
        document = Document(**structured_data)
        
        print(document.normalized_text)
        return document

        
        


        



