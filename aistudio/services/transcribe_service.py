"""
Сервис переводчик
"""
import traceback
from fastapi import UploadFile
from sqlalchemy.orm import Session
from aistudio.config.config import S3Config
from aistudio.services.tmp_file_service import TmpFileService
from aistudio.repositories.transcribers.yandex_transcriber import YandexTranscriber
from aistudio.repositories.transcribers.vosk_transcriber import VoskTranscriber
from aistudio.services.translate_service import TranslateService
from aistudio.repositories.transcription_log_repository import TranscriptionLogRepository
from aistudio.schemas.transcription_log_out import TranscriptionLogCreate


class TranscribeService:
    def __init__(self, config: S3Config, language: str='auto', db: Session = None):
        """
        Конструктор
        """
        # Tajik STT: use Vosk ``vosk-model-tg-*``. Yandex ``language=auto`` mis-detects tg as uz/ru.
        if language == 'tg':
            self.transcribers = [VoskTranscriber()]
        elif language == 'auto':
            self.transcribers = [VoskTranscriber(), YandexTranscriber(config)]
        elif language not in ["ru", "en"]:
            self.transcribers = [YandexTranscriber(config)]
        else:
            self.transcribers = [VoskTranscriber()]

        self.translate_service = TranslateService(config)
        self.language = language
        self.db = db
        self.transcription_log_repository = TranscriptionLogRepository(db) if db else None
        self.language = language
        self.db = db
        self.transcription_log_repository = TranscriptionLogRepository(db) if db else None

    def _log_transcription(
        self,
        file_uuid: str,
        text: str,
        lang: str,
        service: str,
        stage: int = 0,
        stage_name: str = None
    ) -> None:
        """
        Log transcription to database
        
        Args:
            file_uuid: UUID of the audio file
            text: Transcribed text
            lang: Language code (ru, tg)
            service: Service name (vosk, yandex)
            stage: Processing stage (0=original)
            stage_name: Optional stage name
        """
        if not self.transcription_log_repository:
            return
        
        try:
            log_data = TranscriptionLogCreate(
                file_uuid=file_uuid,
                text=text,
                lang=lang,
                service=service,
                stage=stage,
                stage_name=stage_name
            )
            self.transcription_log_repository.create(
                file_uuid=log_data.file_uuid,
                text=log_data.text,
                lang=log_data.lang,
                service=log_data.service,
                correct_text=log_data.correct_text,
                stage=log_data.stage,
                stage_name=log_data.stage_name
            )
        except Exception as log_error:
            print(f"Failed to log transcription: {log_error}")

    def transcribe(self, file: UploadFile) -> dict:
        """
        Перевести файл в текст

        """
        try:
            tmp = TmpFileService(file)
            file_uuid = tmp.get_file_uuid()
            text = ""
            service_used = ""
            
            for transcriber in self.transcribers:
                text = transcriber.transcribe(tmp.get_file_path())
                
                # Determine service name
                if isinstance(transcriber, YandexTranscriber):
                    service_used = "yandex"
                elif isinstance(transcriber, VoskTranscriber):
                    service_used = "vosk"
                
                # Determine language
                lang = "tg" if self.language not in ["ru", "en", "auto"] else "ru"
                if self.language == "auto":
                    # Try to detect language from text
                    lang = "tg" if service_used == "vosk" else "ru"
                
                # Log the transcription
                self._log_transcription(
                    file_uuid=file_uuid,
                    text=text,
                    lang=lang,
                    service=service_used,
                    stage=0,
                    stage_name="original"
                )
                
                return {"text": text}
                #if self.translate_service.is_languages(text, ["ru", "en"]):
                #    return {"text": text}
            return {"text": text}

        except Exception as e:
            return {"error": str(e) + ' ' + {traceback.format_exc()}}
