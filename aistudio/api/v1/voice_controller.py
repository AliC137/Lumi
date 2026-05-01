from fastapi import APIRouter, Response
from aistudio.services.tts_client import tts_generate

router = APIRouter()

@router.get("/tts")
async def tts(text: str):
    audio_bytes = await tts_generate(text)
    return Response(content=audio_bytes, media_type="audio/wav")
