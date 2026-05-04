# AI Studio (Lumi backend)

FastAPI service for auth, admin, RAG document chat (S3 + FAISS), speech (Vosk / STT), and related APIs.

## Requirements

- Python **3.12+**
- [Poetry](https://python-poetry.org/) for dependencies
- MySQL (or your configured DB) per project settings
- **Ollama** (or remote LLM endpoint as configured in code) for RAG answers

## Setup

```bash
cd aiStudio
poetry install
```

Copy environment templates and fill secrets (database, S3, JWT, etc.):

- `.env.example` → `.env` (if present)

Run migrations as needed (`alembic`).

## Run the API

From **`aiStudio`** (repository root — same level as `pyproject.toml`):

```bash
poetry run uvicorn aistudio.main:app --host 127.0.0.1 --port 8000
```

Swagger: `http://127.0.0.1:8000/docs`

## Project folders you must have locally

### `samples/` (empty in git)

- **Purpose:** Writable directory for generated audio previews (e.g. TTS WAV files) served under `/samples`.
- **In git:** Only an empty placeholder (`.gitkeep`). Runtime files are ignored.
- The app creates this folder on startup if missing.

### `aimodels/` (models not in git)

- **Purpose:** Vosk speech models, optional bundled FFmpeg, and other large binaries.
- **In git:** Only `.gitkeep` and `aimodels/README.md` with layout instructions.
- **Required for Tajik Vosk STT:** unzip the model into:

  `aimodels/vosk-model-tg-0.22/`

  See `aimodels/README.md` for details.

## RAG (quick reference)

- Upload: `POST /api/v1/rag/upload-file/` or `/api/v1/rag/upload_file` (multipart `files`)
- Ask: `POST /api/v1/rag/query` with JSON body `question`, optional `retrieval_query`, `reply_language` (`en` | `ru` | `tg` | `auto`)

## Frontend

The React UI lives in a separate repo (**frontendlumi**). Typical dev: frontend on port **8001**, proxying API calls to this backend on **8000**.

## License

See repository root `LICENSE` if provided.
