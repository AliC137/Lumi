from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pathlib import Path
from aistudio.repositories.fastapi_s3 import S3
from aistudio.config.config import S3Config
from botocore.exceptions import ClientError
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import boto3
from io import BytesIO
import os
from urllib.parse import quote
from fastapi.responses import StreamingResponse
from urllib.parse import quote




router = APIRouter()

s3_config = S3Config()

s3_client = S3(s3_config)

s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("AWS_S3_ENDPOINT"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)








@router.get("/download_file")
async def download_file(filename: str = Query(..., description="Filename only")):
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    object_name = f"s3-uploader/{filename}"

    try:
        file_buffer = BytesIO()
        s3_client.download_fileobj(bucket_name, object_name, file_buffer)
        file_buffer.seek(0)

        # Кодируем имя файла для заголовка
        quoted_filename = quote(filename)

        return StreamingResponse(
            file_buffer,
            media_type="application/octet-stream",
            headers={
                # для браузеров, которые понимают UTF-8
                "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"
            }
        )
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found in S3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")










