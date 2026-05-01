from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
from aistudio.langchain_loaders.s3_loader import S3DocumentLoader
from aistudio.langchain_loaders.rag_singleton import rag_service
from aistudio.api.v1.rag_api import run_rag_query
from typing import List
import boto3
import os
from fastapi import HTTPException
from urllib.parse import quote

router = APIRouter(tags=["RAG"])

# S3 configuration
s3 = boto3.client("s3", endpoint_url="https://storage.yandexcloud.net")
BUCKET_NAME = "aistudio"


def rag_index_json() -> dict:
    """JSON index for RAG (mounted on app as ``GET /api/v1/rag`` and ``GET /api/v1/rag/``)."""
    base = "/api/v1/rag"
    return {
        "service": "RAG",
        "note": "OpenAPI UI: GET /docs on this backend (not the React dev server unless proxied).",
        "endpoints": {
            "upload_file": {"method": "POST", "path": f"{base}/upload_file", "body": "multipart/form-data, field name: files"},
            "upload_file_legacy": {"method": "POST", "path": f"{base}/upload-file/", "body": "multipart/form-data, field name: files"},
            "list_files": {"method": "GET", "path": f"{base}/list_files"},
            "query": {"method": "POST", "path": f"{base}/query", "query": "question (required)"},
        },
    }




async def _upload_files_impl(files: List[UploadFile]):
    results = []
    try:
        loader = S3DocumentLoader(bucket_name=BUCKET_NAME, s3_client=s3)

        for file in files:
            key = f"s3-uploader/{file.filename}"
            s3.upload_fileobj(file.file, BUCKET_NAME, key)

            documents = loader.load(key)
            rag_service.add_documents(documents)

            results.append({"filename": file.filename, "status": "✅ Uploaded & processed"})

        return {"status": "success", "files": results}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "❌ Failed", "error": str(e), "files": results}
        )


@router.post(
    "/upload-file/",
    summary="Upload files (legacy path)",
    openapi_extra={"x-codegen-request-body-name": "files"},
)
async def upload_files(files: List[UploadFile] = File(...)):
    """Original path (kept for frontend compatibility)."""
    return await _upload_files_impl(files)


@router.post("/upload_file", summary="Upload files (multipart field: files)")
async def upload_file(files: List[UploadFile] = File(...)):
    """Snake_case alias — same behaviour as ``upload-file``."""
    return await _upload_files_impl(files)


@router.post("/query", summary="RAG query (query param: question)")
async def query(question: str = Query(..., description="Question for RAG / LLM fallback")):
    """RAG query under the same ``/api/v1/rag`` prefix as upload and list."""
    return await run_rag_query(question)


@router.get("/list_files", summary="List uploaded files in S3 prefix s3-uploader/")
def list_files():
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="s3-uploader/")
        contents = response.get("Contents", [])

        file_infos = []
        for obj in contents:
            key = obj["Key"]
            filename = key.split("/")[-1]
            q = quote(filename, safe="")
            file_infos.append({
                "filename": filename,
                "path": key,
                "download_url": f"/api/v1/s3/download_file?filename={q}",
            })

        return file_infos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

