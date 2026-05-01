import os
from typing import List
import boto3
from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from tempfile import NamedTemporaryFile 


class S3DocumentLoader:
    def __init__(self, bucket_name: str, s3_client: boto3.client):
        self.bucket_name = bucket_name
        self.s3_client = s3_client

    def download_file(self, s3_key: str) -> str:
        with NamedTemporaryFile(delete=False) as tmp_file:
            self.s3_client.download_fileobj(self.bucket_name, s3_key, tmp_file)
            return tmp_file.name

    def load(self, s3_key: str) -> List[Document]:
        local_path = self.download_file(s3_key)

        try:
            ext = os.path.splitext(s3_key)[1].lower()  # <-- FIXED LINE

            if ext == ".pdf":
                loader = PyPDFLoader(local_path)
            elif ext == ".txt":
                loader = TextLoader(local_path, encoding="utf-8")
            elif ext == ".docx":
                loader = Docx2txtLoader(local_path)
            else:
                raise ValueError("Unsupported file type")

            docs = loader.load()
            return docs
        finally:
            os.remove(local_path)
