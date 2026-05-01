"""
Сервис яндек speech to text
"""
from aistudio.config.config import S3Config
from pathlib import Path
from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType


class YandexTranscriber:
    def __init__(self, config: S3Config):
        """
        Конструктор
        """
        self._api_key = config.YA_SPEECH_ACCESS_KEY

    def transcribe(self, path_file: Path)->str:
        """
        Перевести файл в текст
        """
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=self._api_key
            )
        )
        model = model_repository.recognition_model()

        model.model = 'general'
        model.language = 'auto'#'ru-RU'
        model.audio_processing_type = AudioProcessingType.Full

        result = model.transcribe_file(path_file)
        text_result = ""
        for c, res in enumerate(result):
            text_result += res.normalized_text
        return text_result
