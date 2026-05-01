"""
Сервис переводчик
"""
import os
import httpx
import uuid
import json
import re
from sqlalchemy.orm import Session
from aistudio.config.config import S3Config
from aistudio.repositories.tts.yandex_tts import YandexTTS
from aistudio.repositories.tts.lumi_tts import LumiTTS
from aistudio.services.translate_service import TranslateService
from aistudio.repositories.tts_log_repository import TTSLogRepository
from aistudio.schemas.tts_log_out import TTSLogCreate

class TTSService:
    def __init__(self, config: S3Config, host:str, db: Session = None):
        """
        Конструктор
        """
        self._tts_ru = YandexTTS(config, host=host)
        self._tts_tg = LumiTTS(config, host=host)

        self.translate_service = TranslateService(config)
        self.texts = []
        self._speech_uuid = None
        self.db = db
        self.tts_log_repository = TTSLogRepository(db) if db else None

    def _log_tts_conversion(
        self, 
        text: str, 
        uuid_file: str, 
        index: int, 
        lang: str, 
        service: str,
        stage: int = 0,
        stage_name: str = None
    ) -> None:
        """
        Log TTS conversion to database
        
        Args:
            text: Text that was converted
            uuid_file: UUID of the generated audio file
            index: Fragment index
            lang: Language code (ru, tg)
            service: Service name (yandex, lumi)
            stage: Processing stage (0=original)
            stage_name: Optional stage name
        """
        if not self.tts_log_repository:
            return
        
        try:
            log_data = TTSLogCreate(
                speech_uid=self._speech_uuid or str(uuid.uuid4()),
                uuid_file=uuid_file,
                text=text,
                index=index,
                lang=lang,
                service=service,
                stage=stage,
                stage_name=stage_name
            )
            self.tts_log_repository.create(log_data)
        except Exception as log_error:
            print(f"Failed to log TTS conversion: {log_error}")


    def clear_text(self, text: str) -> str:
        # Convert common markdown formatting to plain text for TTS.
        cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        cleaned = re.sub(r"[*_~`#>-]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def pop_text(self) -> dict|None:
        if len(self.texts) > 0:
            return self.texts.pop(0)
        return None

    def set_text(self, text: str) -> dict:
        text = self.clear_text(text)
        self._speech_uuid = str(uuid.uuid4())
        os.makedirs(f"tmp/speech", exist_ok=True)
        os.makedirs(f"tmp/speech/{self._speech_uuid}", exist_ok=True)
        #for s in re.split(r'(?<=[.,:!?…]) ', text):
        for s in re.split(r'(?<=[.!?…]) ', text):
            self.texts.append({"text": s, "uuid": str(uuid.uuid4())})
        #self.texts.append({"text": text, "uuid": str(uuid.uuid4())})
        print(f"chunck text {self.texts}")
        #words = self.clear_text(text).split()
        #chunk_size = 3
        #for i in range(0, len(words), chunk_size):
        #    self.texts.append({"text": " ".join(words[i:i + chunk_size]), "uuid": str(uuid.uuid4())})
        data = { "text_data": self.texts,
                 "speech_uuid": self._speech_uuid}

        with open(f"tmp/speech/{self._speech_uuid}/data.json", "w") as json_file:
             json.dump(data, json_file, indent=4)

        return data

    def is_in_dictionary(self, text: str)->bool:
        return "салом" in text.lower()

    def is_tg(self, text:str) -> bool:
        """
        Переключатель языка
        """
        print(f"text {text}")
        if self.is_in_dictionary(text):
            return True

        return self.translate_service.is_languages(text, ["tg"])

    def speech(self, text: str) -> dict:
        """
        Речь по тексту
        Параметры:
          text:str - текст
        Возврат:
            dict 
               samples: list[str] - Список wav файлов
        """
        try:
           text = self.clear_text(text)
           is_tg = self.is_tg(text)
           if is_tg:
               result = self._tts_tg.speech(text)
               service = "lumi"
               lang = "tg"
           else:
               result = self._tts_ru.speech(text)
               service = "yandex"
               lang = "ru"
           
           # Log TTS conversion
           if result.get('samples'):
               uuid_file = result['samples'][0].split('/')[-1].replace('.wav', '') if result['samples'] else None
               self._log_tts_conversion(
                   text=text,
                   uuid_file=uuid_file,
                   index=0,
                   lang=lang,
                   service=service,
                   stage=0,
                   stage_name="original"
               )
           
           return result
        except Exception as e:
            return {"error": str(e)}


    async def speech_sreaming(self, language: str):
        """
        Речь по тексту
        Параметры:
          text:str - текст
        Возврат:
            dict
               samples: list[str] - Список wav файлов
        """
#        if self.response is not None:
#            for chunk in self.response.iter_content(chunk_size=8192):
#                yield chunk
        index = 0
        while True:
            text = self.pop_text()
            if not text:
                break
            text_content = text["text"]
            uuid_file = text["uuid"]
            text_content = self.clear_text(text_content)
            
            if language == 'tg':
                data = self._tts_tg.speech(text_content)
                service = "lumi"
            else:
                data = self._tts_ru.speech(text_content)
                service = "yandex"

            # Log TTS conversion
            if data.get('samples'):
                self._log_tts_conversion(
                    text=text_content,
                    uuid_file=uuid_file,
                    index=index,
                    lang=language,
                    service=service,
                    stage=0,
                    stage_name="original"
                )

            async with httpx.AsyncClient() as client:
                async with client.stream("GET", data['samples'][0]) as response:
                    response.raise_for_status()  # Raise an exception for bad status codes
                    async for chunk in response.aiter_bytes():
                        yield chunk
            
            index += 1

    def background(self) -> None:
        is_tg = None
        index = 0
        while True:
            text_data = self.pop_text()
            if not text_data:
                break
            text = text_data["text"]
            uuid_file = text_data["uuid"]
            text = self.clear_text(text)
            
            if is_tg is None:
                is_tg = self.is_tg(text)
            
            if is_tg:
                data = self._tts_tg.speech(text)
                service = "lumi"
                lang = "tg"
            else:
                data = self._tts_ru.speech(text)
                service = "yandex"
                lang = "ru"
            
            # Log TTS conversion
            if data.get('samples'):
                self._log_tts_conversion(
                    text=text,
                    uuid_file=uuid_file,
                    index=index,
                    lang=lang,
                    service=service,
                    stage=0,
                    stage_name="original"
                )
            
            file_path = f"tmp/speech/{self._speech_uuid}/{uuid_file}.json"
            with open(file_path, "w") as json_file:
               json.dump(data, json_file, indent=4)
            
            index += 1