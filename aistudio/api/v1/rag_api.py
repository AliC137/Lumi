import requests
import uuid
from fastapi import Query, UploadFile, APIRouter, FastAPI, Depends, HTTPException
from fastapi import Request, WebSocket
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from aistudio.langchain_loaders.rag_singleton import rag_service
from aistudio.langchain_loaders.rag_service import (
    normalize_reply_language,
    reply_language_instruction,
    strip_model_reasoning,
)
from aistudio.services.llms.llm_dialog_service import LLMDialogService
from aistudio.services.llms.library_service import LibraryService

from aistudio.services.transcribe_service import TranscribeService
from aistudio.services.tts_service import TTSService
from aistudio.services.docx2txt_service import Docx2TxtService

from aistudio.config.config import S3Config
from langchain_ollama import OllamaLLM
from aistudio.schemas.book_request import BookRequest
from aistudio.schemas.profile_request import ProfileRequest
from aistudio.schemas.tts_request import TTSRequest
from fastapi import BackgroundTasks
from aistudio.dependencies.database import get_db

router = APIRouter()
config = S3Config()
app = FastAPI()

llm = OllamaLLM(model="deepseek-r1")


async def run_rag_query(
    question_for_llm: str,
    reply_language: str = "auto",
    retrieval_query: str | None = None,
) -> dict:
    """Shared RAG + LLM fallback (retrieval uses retrieval_query when set — avoids noisy chat-prefix embeddings)."""
    rl = normalize_reply_language(reply_language)
    rq = (retrieval_query or "").strip() or None
    try:
        answer = rag_service.query(
            question_for_llm,
            reply_language=rl,
            retrieval_query=rq,
        )
        if answer and "No documents uploaded yet." not in answer:
            return {"answer": answer}
    except Exception as e:
        print(f"[RAG error] {e}")

    if rag_service.vectorstore is not None:
        blocked = {
            "ru": (
                "Не удалось составить ответ строго по загруженным фрагментам. "
                "Переформулируйте вопрос, укажите номер главы и ключевые слова из PDF, "
                "или дождитесь окончания индексации после загрузки."
            ),
            "tg": (
                "Ҷавоб аз матни боргирифташуда наёфт шуд. Саволро иваз кунед ё матни дақиқ аз PDF нависед."
            ),
            "en": (
                "Could not answer strictly from your uploaded excerpts. "
                "Rephrase the question, name the chapter and keywords from the PDF, "
                "or wait until indexing finishes after upload."
            ),
            "auto": (
                "Could not answer strictly from your uploaded excerpts. "
                "Rephrase the question, name the chapter and keywords from the PDF, "
                "or wait until indexing finishes after upload."
            ),
        }
        return {"answer": blocked.get(rl, blocked["auto"])}

    try:
        instr = reply_language_instruction(rl)
        prompt = (
            f"{instr}\n\n"
            "Answer directly with no reasoning preamble (no Hmm, no step-by-step planning).\n\n"
            f"Question:\n{question_for_llm}\n\nAnswer:"
        )
        raw = rag_service.get_llm().invoke(prompt)
        text = raw.content if hasattr(raw, "content") else str(raw)
        return {"answer": strip_model_reasoning(text)}
    except Exception as e:
        return {"error": f"LLM fallback failed: {str(e)}"}


@router.post("/stt/tajik/")
async def transcribe_tajik(file: UploadFile, db: Session = Depends(get_db)):
    transcribe_service = TranscribeService(config, 'tg', db=db)
    obj = transcribe_service.transcribe(file)
    if isinstance(obj, dict) and obj.get("error"):
        raise HTTPException(status_code=500, detail=str(obj["error"]))
    return obj


@router.post("/speech/trascribe")
async def transcribe_speech(file: UploadFile, db: Session = Depends(get_db)):
    transcribe_service = TranscribeService(config, db=db)
    obj = transcribe_service.transcribe(file)
    return obj


@router.post("/library/book/ask_old")
def ask_book_old(request: BookRequest):
    try:
        answer = rag_service.query(request.question)

        # Fallback to plain LLM if no docs
        if answer and "No documents uploaded yet." not in answer:
            return {"answer": answer}
    except Exception as e:
        print(f"[RAG error] {e}")

    # Fallback to plain Ollama
    try:
        fallback = llm.invoke(request.question)
        return {"answer": fallback}
    except Exception as e:
        return {"error": f"LLM fallback failed: {str(e)}"}

@router.post("/library/book/ask")
def ask_book(request: BookRequest):
    try:
        dialog = LLMDialogService(config, "library", request.book_id)
        return dialog.answer(request.question)
    except Exception as e:
        return {"error": str(e)}
@router.get("/library/books/load")
def load_books():
    try:
        library = LibraryService(config)
        return library.load_books()
    except Exception as e:
        return {"error": str(e)}

@router.post("/profile/dialog")
def profile_ask_ai(request: ProfileRequest):

    try:
        dialog = LLMDialogService(config,"profile", request.profile_id)
        return dialog.answer(request.question)
    except Exception as e:
        return {"error": str(e)}



#    try:
#        answer = rag_service.query(request.question)

        # Fallback to plain LLM if no docs
#        if answer and "No documents uploaded yet." not in answer:
#            return {"answer": answer}
#    except Exception as e:
#        print(f"[RAG error] {e}")

    # Fallback to plain Ollama
    try:
        fallback = llm.invoke(request.question)
        return {"answer": fallback}
    except Exception as e:
        return {"error": f"LLM fallback failed: {str(e)}"}

@router.post("/tts")
def get_tts(params: TTSRequest, request: Request, db: Session = Depends(get_db)):
    host = f'{request.url.scheme}://{request.url.netloc}'
    tts_service = TTSService(config, host, db)
    obj = tts_service.speech(params.text)
    return obj

@router.get("/docx2txt")
def get_tts(request: Request):
    docx2txt = Docx2TxtService()
    docx2txt.convert()
    return {'success':True}

@router.post("/tts/background")
async def get_tts_background(params: TTSRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    host = f'{request.url.scheme}://{request.url.netloc}'
    tts_service = TTSService(config, host, db)
    speech_data = tts_service.set_text(params.text)
    background_tasks.add_task(tts_service.background)
    return {"speech_data": speech_data
    }

@router.post("/tts/do")
async def get_tts_do(params: TTSRequest, request: Request, background_tasks: BackgroundTasks):
    host = f'{request.url.scheme}://{request.url.netloc}'
    tts_data = {"uuid":f"{uuid.uuid4()}"}
    return {"tts_data": tts_data}



