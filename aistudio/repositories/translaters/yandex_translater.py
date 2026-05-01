"""
Yandex переводчик
"""
import requests
from aistudio.config.config import S3Config
from textwrap3 import wrap
import time

class YandexTranslater:
    """
    Класс яндекс переводчика
    """
    def __init__(self, config: S3Config):
        """
        Конструктор принимает yandex config
        """
        self._url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        self._api_key = config.YA_SPEECH_ACCESS_KEY
        self._headers =  self._make_headers()

    def _make_headers(self) -> dict:
        """
        Сделать header
        Возвращает строку header для аутентификации к сервису
        """
        return {
            "Authorization": f"Api-Key {self._api_key}"
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
           "texts": [text],
           "targetLanguageCode": language,
           "sourceLanguageCode": None if source_language == '--' else source_language
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
        try:
            wtexts = wrap(text, 100)

            translation = self._translate_data(wtexts[0], source_language='--')
            if len(translation['translations']) > 0:
                return translation['translations'][0]['detectedLanguageCode']
            else:
                return '--'
        except Exception as e:
            return '--'

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
        if len(translation['translations']) > 0:
            translated_texts = []
            for translated in translation['translations']:
                translated_texts.append(translated['text'])
            translated_text = " ".join(translated_texts)
            s_l = translation['translations'][0]['detectedLanguageCode'] if 'detectedLanguageCode' in translation['translations'][0] else source_language
            return {"source_language": s_l,
                    "text": translated_text
                    }
        else:
            return {"source_language": "--", "text": text}

    def translate(self, text: str, language: str = 'ru', source_language: str ='tg') -> str:
        wtexts = wrap(text, 8000)
        translated = ""
        delay = 1/20
        index = 0
        for t in wtexts:
            time.sleep(delay)
            data = self.translate_and_detect(t, language, source_language)
            translated += " " + data['text'] if index > 0 else data['text']
            index += 1
        return translated
