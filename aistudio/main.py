# from fastapi import FastAPI
# app = FastAPI()
# @app.get("/")
# async def main_route():
#   return {"message": "Hey, It is me"}
"""
main.py

Главная точка входа в приложение.
Инициализирует FastAPI-приложение и подключает маршруты (контроллеры).
"""
import json
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from aistudio.api.v1 import user_controller
from aistudio.api.v1 import ollama_controller
from aistudio.api.v1 import s3_main
from aistudio.api.v1 import subject_type_controller
from aistudio.api.v1 import subject_controller
from aistudio.api.v1 import role_controller
from aistudio.api.v1 import user_subject_controller

# Импорт моделей для инициализации
from aistudio.models.user import User
from aistudio.models.jwt_token import JWTToken
from aistudio.models.subject_type import SubjectType
from aistudio.models.subject import Subject
from aistudio.models.role import Role
from aistudio.models.user_subject import UserSubject
from aistudio.api.v1 import rag_api
from aistudio.api.v1 import rag_upload
from aistudio.api.v1.admin import admin_router

from fastapi import FastAPI, WebSocket, Response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from aistudio.api.v1 import (
    user_controller, ollama_controller, s3_main, subject_type_controller,
    subject_controller, role_controller, user_subject_controller, rag_api,
    rag_upload
)
from aistudio.api.v1.voice_controller import router as voice_router

app = FastAPI(
    title="AI Studio API",
    description=(
        "Backend for authentication, admin, and RAG file workflows. "
        "**RAG (upload / list / query)** lives under **`/api/v1/rag/`** — open the **RAG** group in Swagger, "
        "or visit **`GET /api/v1/rag/`** for a JSON index. API docs: **`/docs`** (this server, usually port **8000**)."
    ),
    version="1.0.0",
    # Keep docs lightweight; full expansion can freeze Swagger UI on larger specs.
    swagger_ui_parameters={"docExpansion": "list", "defaultModelsExpandDepth": -1},
    openapi_tags=[
        {
            "name": "RAG",
            "description": (
                "Document upload (S3 + vector store), file listing, and RAG query. "
                "Paths: `POST /api/v1/rag/upload_file`, `POST /api/v1/rag/upload-file/`, "
                "`GET /api/v1/rag/list_files`, `POST /api/v1/rag/query`."
            ),
        },
        {"name": "ollama", "description": "Local LLM management via Ollama CLI."},
        {"name": "Admin Panel", "description": "Admin APIs under `/api/v1/admin/...`."},
    ],
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Create samples directory if it doesn't exist
samples_dir = Path("samples")
samples_dir.mkdir(exist_ok=True)
app.mount("/samples", StaticFiles(directory="samples"), name="samples")

# Include routers
app.include_router(user_controller.router, prefix="/api/v1/users")
app.include_router(s3_main.router, prefix="/api/v1/s3")
app.include_router(ollama_controller.router)
# Register RAG file routes before the large rag_api router so they appear near the top of /openapi.json.
app.include_router(rag_upload.router, prefix="/api/v1/rag")
app.include_router(rag_api.router, prefix="/api/v1")
# RAG index: register on app for both slash variants (sub-router ``GET /`` can 404 with some clients).
@app.get("/api/v1/rag", tags=["RAG"], summary="RAG service index (no trailing slash)")
@app.get("/api/v1/rag/", tags=["RAG"], summary="RAG service index (trailing slash)")
def rag_index_public():
    return rag_upload.rag_index_json()

app.include_router(subject_type_controller.router, prefix="/api/v1/subject-types", tags=["Subject Types"])
app.include_router(subject_controller.router, prefix="/api/v1/subjects", tags=["Subjects"])
app.include_router(role_controller.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(user_subject_controller.router, prefix="/api/v1/user-subjects", tags=["User Subjects"])

# Подключение админ-панели
app.include_router(admin_router, prefix="/api/v1")
print("main.py loaded")
app.include_router(voice_router, prefix="/api/v1")  # TTS router

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "aiStudio API is running"}


@app.websocket('/speech/{speech_uuid}/ws')
async def speech_endpoint(websocket: WebSocket,
    speech_uuid: str):
    with open(f"tmp/speech/{speech_uuid}/data.json", 'r') as file:
        speech_data = json.load(file)
        await websocket.accept()
        texts = speech_data["text_data"]
        len_text = len(texts)
        index = 0

        while True:
            if index == len_text:
                break
            uuid_file = texts[index]["uuid"]
            text = texts[index]["text"]
            file_path = f"tmp/speech/{speech_uuid}/{uuid_file}.json"
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        #print(f"file {file.read()}")
                        speech_data = json.load(file)
                        speech_data['uuid'] = uuid_file
                        speech_data['text'] = text
                        await websocket.send_json(speech_data)
                        index += 1
                    os.remove(file_path)
            except Exception as e:
                print(f"Exception on read {e}")
        os.remove(f"tmp/speech/{speech_uuid}/data.json")
        os.rmdir(f"tmp/speech/{speech_uuid}")

