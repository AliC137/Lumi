# aimodels

Put **local ML binaries and weights** here (not committed to git). Run the API from the **`aiStudio`** project root so paths resolve correctly.

## Required for Tajik STT (Vosk)

1. Download a compatible **Vosk** model for Tajik (or the variant your deployment uses).
2. Extract it so this folder exists:

   `aimodels/vosk-model-tg-0.22/`

   The loader expects exactly that path (`aistudio.repositories.transcribers.vosk_transcriber`).

## Optional: FFmpeg

If you bundle FFmpeg for audio tooling, place it under `aimodels/` (see `aistudio/utils/ffmpeg_path.py`). Typical layout:

`aimodels/ffmpeg-…/bin/ffmpeg.exe` (Windows) or `ffmpeg` (Unix).

## Optional: other models

Add Hugging Face caches, Ollama weights, etc. locally under this directory as needed; keep large files out of version control.
