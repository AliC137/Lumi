"""
Сервис переводчик
"""
from aistudio.config.config import S3Config
from aistudio.repositories.translaters.yandex_translater import YandexTranslater
from aistudio.repositories.translaters.lingvanex_translater import LingvanexTranslater


class TranslateService:
    def __init__(self, config: S3Config, type: str = 'yandex'):
        """
        Конструктор
        """

        self.translater = YandexTranslater(config) if type == 'yandex' \
            else LingvanexTranslater(config)


    def _get_translater(self):
        """
        Получить переводчик
        """
        return self.translater

    def translate(self, text:str, language: str = 'ru', source_language: str ='tg') -> str:
        """
        Перевести текст
        Параметры:
          text:str - текст для перевода
          language: - str код языка для перевода
        Вощврат:
          Возвращает
            src 
               text - переведенный текст
        """
        return self._get_translater().translate(text, language, source_language)

    def detect_language(self, text:str)->str:
        """
        Определение языка
        Параметры:
          text:str - текст
        Возврат:
          код языка 
        """
        return self._get_translater().detect_language(text)

    def is_languages(self, text:str, languages:list[str])->bool:
        """
        Проверка на принадлежность текста списку языков
        Параметры:
           text - исходный текст
           languages - массив кодов языков к которым принадлежит текст
        Возврат:
          bool
             Истина, если текст принадлежит указанному списку языков
        """
        lang = self.detect_language(text)
        return lang in languages



