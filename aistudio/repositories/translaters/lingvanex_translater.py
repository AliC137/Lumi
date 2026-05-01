"""
lingvanex переводчик
"""
import requests
from aistudio.config.config import S3Config
from textwrap3 import wrap
import time

class LingvanexTranslater:
    """
    Класс яндекс переводчика
    """
    def __init__(self, config: S3Config):
        """
        Конструктор принимает yandex config
        """
        self._url = "https://api-b2b.backenster.com/b1/api/v3/translate"
        self._api_key = config.LR_KEY_API
        self._headers =  self._make_headers()

    def _make_headers(self) -> dict:
        """
        Сделать header
        Возвращает строку header для аутентификации к сервису
        """
        return {
            "Authorization": f"Bearer {self._api_key}", # Adjust based on Lingvanex's specific authorization method
            "Content-Type": "application/json"
        }

    def _get_headers(self) -> dict:
        """
        Получить заголовок
        """
        return self._headers

    def _get_url(self) -> str:
        """
         Получить url сервиса
        """
        return self._url

    def _translate_data(self, text: str, language: str = 'ru', source_language: str ='tg') -> dict:
        """
        Сделать запрос к сервису переводчика
        """
        data = {
           "from": source_language,
           "to": language,
           "data": text
        }
        try:
            response = requests.post(self._get_url(), headers=self._get_headers(), json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise Exception(f"Ошибка переводчика: {err}")

    def detect_language(self, text: str) -> str:
        """
        Определить язык
        """
        data = {
           "q": text
        }
        try:
            response = requests.post("https://api-gl.lingvanex.com/language/translate/v2/detect", headers=self._get_headers(), json=data)
            response.raise_for_status()
            r = response.json()
            return r['data']['detections'][0][0]['language']
        except requests.exceptions.HTTPError as err:
            raise Exception(f"Ошибка переводчика: {err}")

        #{'data': {'detections': [[{'confidence': 1, 'language': 'tg', 'isReliable': False}]]}} 


    def translate_and_detect(self, text: str, language: str = 'ru', source_language: str ='tg') -> dict:
        """
        Перевести текст
        Параметры:
          text:str - текст для перевода
          language: - str код языка для перевода
        Вощврат:
          Возвращает
            dict 
               source_language - код языка
               text - переведенный текст
        """
        translation = self._translate_data(text,language,source_language)
        r = translation["result"]
        return {"source_language": source_language,
                "text": translation["result"]
               }

    def translate(self, text: str, language: str = 'ru', source_language: str ='tg') -> str:
        wtexts = wrap(text, 20000)
        translated = ""
        delay = 1/20
        index = 0
        for t in wtexts:
            time.sleep(delay)
            data = self.translate_and_detect(t, language, source_language)
            translated += " " + data['text'] if index > 0 else data['text']
            index += 1
        return translated
