from botocore.exceptions import ClientError
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from urllib.parse import quote
import boto3
import os


router = APIRouter()

# Legacy known-working S3 setup
s3_client = boto3.client(
    "s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)







@router.get("/download_file")
async def download_file(filename: str = Query(..., description="Filename only")):
    """Must use the same bucket and prefix as ``rag_upload`` (``s3-uploader/``)."""
    bucket_name = "aistudio"
    object_name = f"s3-uploader/{filename}"

    try:
        file_buffer = BytesIO()
        s3_client.download_fileobj(bucket_name, object_name, file_buffer)
        file_buffer.seek(0)

        quoted_filename = quote(filename)

        return StreamingResponse(
            file_buffer,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"
            },
        )
    except ClientError as e:
        code = (e.response or {}).get("Error", {}).get("Code", "") or ""
        if code in ("404", "NoSuchKey", "NotFound") or "404" in str(e):
            raise HTTPException(status_code=404, detail="File not found in S3") from e
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}") from e










