from dotenv import load_dotenv
import os
import sys
import threading
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from pathlib import Path
from fastapi.concurrency import run_in_threadpool
load_dotenv(dotenv_path=Path("s3.env"))



class S3:
    def __init__(self, conf):
        self.region = conf.AWS_DEFAULT_REGION
        self.endpoint = conf.AWS_S3_ENDPOINT

        boto_config = Config(signature_version='s3v4')  # ВАЖНО для Yandex

        self.session = boto3.session.Session()

        self.s3_resource = self.session.resource(
            "s3",
            region_name=self.region,
            endpoint_url=self.endpoint,
            aws_access_key_id=conf.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=conf.AWS_SECRET_ACCESS_KEY,
            config=boto_config
        )

        self.s3_client = boto3.client(
            "s3",
            region_name=conf.AWS_DEFAULT_REGION,
            endpoint_url=conf.AWS_S3_ENDPOINT,
            aws_access_key_id=conf.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=conf.AWS_SECRET_ACCESS_KEY,
)






    async def download_file(self, bucket_name: str, file_name: Path | str, object_name: str, extra_args: dict = None):
        try:
            file_path = Path(file_name)  # ← безопасное приведение
            file_path.parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(bucket_name, object_name, str(file_path))
        except Exception as err:
            logging.error(err)
            return str(err)
        return {object_name: "Downloaded"}
    


    async def create_bucket(self, bucket_name: str):
        try:
            if self.region is None:
                self.s3_resource.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': self.region}
                self.s3_resource.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration=location
                )
        except ClientError as e:
            logging.error(e)
            return False
        return True


    async def list_objects(self, bucket_name, prefix: str = None): 
        operation_parameters = {"Bucket": bucket_name}
        if prefix:
            # Ensure correct prefix format for "folders"
            if not prefix.endswith("/"):
                prefix += "/"
            # Ensure correct prefix format for "folders"
            if not prefix.endswith("/"):
                prefix += "/"
            operation_parameters["Prefix"] = prefix

        paginator = self.s3_client.get_paginator('list_objects_v2')
        paginator = self.s3_client.get_paginator('list_objects_v2')

        try:
            page_iterator = paginator.paginate(**operation_parameters)
            return page_iterator
        except self.s3_client.exceptions.NoSuchKey:
            # Yandex quirk: treat it like empty list
            return []



class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

    