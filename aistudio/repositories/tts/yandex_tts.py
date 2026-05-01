"""
Текст в речь Anicenna
"""

import requests
import uuid
from aistudio.config.config import S3Config
from speechkit import configure_credentials, creds, model_repository
from speechkit.tts import AudioEncoding
from pathlib import Path

class YandexTTS:
    """
    Текст в речь Yandex
    """
    def __init__(self, config: S3Config = None, host: str = ''):
        """
        Конструктор
        """
        self._api_key = config.YA_SPEECH_ACCESS_KEY
        self.host = host

    def speech(self, text: str) -> dict:
        """
        Получить речь
        """
        configure_credentials(
           yandex_credentials=creds.YandexCredentials(
             api_key=self._api_key
           )
        )

        synthesis_model = model_repository.synthesis_model()
        synthesis_model.voice = 'anton'  # Example voice
        synthesis_model.rate = 1.0  # Normal speech rate

        result = synthesis_model.synthesize(text, raw_format=False)
        file_name = f"samples/{uuid.uuid4()}.wav"
        result.export(Path(file_name), 'wav')

        # Export the synthesized audio to a WAV file

#        result.export(file_name, format=AudioEncoding.WAV)

        samples= [f"{self.host}/{file_name}"]

        return {'samples': samples}

