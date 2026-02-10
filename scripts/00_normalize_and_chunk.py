"""File for reading, normalizing and chunking CVs and Job Descriptions."""
from interview_prep.CV.cv_reader import CVReader
from interview_prep.CV.chunker import CVChunker
from interview_prep.job_descripition.job_parser import JobDescriptionParser


if __name__ == "__main__":

    cv_reader = CVReader()
    cv_chunker = CVChunker()
    job_parser = JobDescriptionParser()

    





