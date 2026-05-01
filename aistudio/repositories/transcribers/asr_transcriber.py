"""
Сервис asr speech to text
"""

from transformers import pipeline

asr = pipeline("automatic-speech-recognition")


class AsrTranscriber:
    def __init__(self, config: S3Config = None):
        """
        Конструктор
        """

    def transcribe(self, path_file: Path) -> str:
        """
        Перевести файл в текст
        """
        return ""