# aistudio/services/tts_client.py
import httpx

TTS_SERVICE_URL = "http://localhost:8010/tts"  # your microservice URL

async def tts_generate(text: str) -> bytes:
    async with httpx.AsyncClient() as client:
        # send the text as a query parameter
        response = await client.get(TTS_SERVICE_URL, params={"text": text})
        response.raise_for_status()
        return response.content  # raw WAV bytes
