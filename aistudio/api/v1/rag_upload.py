from fastapi import APIRouter, UploadFile, File, Query, BackgroundTasks, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from aistudio.langchain_loaders.s3_loader import S3DocumentLoader
from aistudio.langchain_loaders.rag_singleton import rag_service
from aistudio.api.v1.rag_api import run_rag_query
from typing import List, Sequence, Optional
from fastapi import HTTPException
from urllib.parse import quote
import boto3


class RagQueryBody(BaseModel):
    question: str = Field(..., description="Full user-facing prompt (may include chat context)")
    retrieval_query: Optional[str] = Field(
        None,
        description="Short text for vector search only; omit to use `question` for both",
    )
    reply_language: str = "auto"

router = APIRouter(tags=["RAG"])

# Legacy known-working S3 setup
s3 = boto3.client("s3", endpoint_url="https://storage.yandexcloud.net")
BUCKET_NAME = "aistudio"


def _ingest_s3_keys(keys: Sequence[str]) -> None:
    """Load keys from S3 and merge into the RAG index so earlier uploads in the session stay searchable."""
    rag_service.begin_ingest()
    try:
        loader = S3DocumentLoader(bucket_name=BUCKET_NAME, s3_client=s3)
        documents = []
        for key in keys:
            try:
                for doc in loader.load(key):
                    doc.metadata.setdefault("source_file", key.rsplit("/", 1)[-1])
                    documents.append(doc)
            except Exception as e:
                print(f"[RAG ingest failed] {key}: {e}")
        if documents:
            rag_service.add_documents(documents, replace=False)
    finally:
        rag_service.end_ingest()


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




async def _upload_files_impl(files: List[UploadFile], background_tasks: BackgroundTasks):
    results = []
    keys: List[str] = []
    try:
        for file in files:
            key = f"s3-uploader/{file.filename}"
            s3.upload_fileobj(file.file, BUCKET_NAME, key)
            keys.append(key)

            results.append(
                {"filename": file.filename, "status": "✅ Uploaded; indexing in background"}
            )

        if keys:
            background_tasks.add_task(_ingest_s3_keys, keys)

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
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    """Original path (kept for frontend compatibility)."""
    return await _upload_files_impl(files, background_tasks)


@router.post("/upload_file", summary="Upload files (multipart field: files)")
async def upload_file(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    """Snake_case alias — same behaviour as ``upload-file``."""
    return await _upload_files_impl(files, background_tasks)


@router.post("/query", summary="RAG query (JSON body preferred)")
async def query(
    question: Optional[str] = Query(None, description="Legacy: question as query param"),
    reply_language: Optional[str] = Query(
        None,
        description="Answer language (en/ru/tg/auto). Sent from UI; overrides JSON body when provided.",
    ),
    body: Optional[RagQueryBody] = Body(None),
):
    """Use JSON ``{question, retrieval_query?, reply_language?}`` so search text stays short while the LLM may see chat context."""
    if body is not None:
        rl = reply_language if reply_language is not None else body.reply_language
        return await run_rag_query(
            body.question,
            reply_language=rl,
            retrieval_query=body.retrieval_query,
        )
    if question is not None:
        rl_legacy = reply_language if reply_language is not None else "auto"
        return await run_rag_query(question, reply_language=rl_legacy, retrieval_query=None)
    raise HTTPException(
        status_code=422,
        detail="Send JSON body with `question`, or pass legacy query parameter `question`.",
    )


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

