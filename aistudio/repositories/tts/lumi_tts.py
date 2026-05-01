"""
Текст в речь Anicenna
"""
import uuid
import requests
from aistudio.config.config import S3Config

class LumiTTS:
    """
    Текст в речь Anicenna
    """
    def __init__(self, config: S3Config = None, host: str = ''):
        """
        Конструктор
        """
        self._url = "http://aiavicenna.tech:8500/api/v1/tts"
        self.host: str = host

    def _get_url(self):
        """
        Получить url сервиса
        """
        return self._url

    def speech(self, text: str) -> dict:
        """
        Получить речь
        """
        try:
            response = requests.post(self._get_url(), json={'text': text})
            response.raise_for_status()
            file_name = f"samples/{uuid.uuid4()}.wav"

            with open(file_name, "wb") as f:
                f.write(response.content)
            samples = [f"{self.host}/{file_name}"]

            return {'samples': samples}

            #return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"tts error: {str(e)}"}
