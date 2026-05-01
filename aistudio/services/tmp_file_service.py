"""
Сервис переводчик
"""
import os
import uuid
from pathlib import Path
import shutil
from fastapi import UploadFile


class TmpFileService:
    def __init__(self, file: UploadFile):
        """
        Конструктор
        """
        self.file = file
        self.file_uuid = str(uuid.uuid4())
        self.file_path = f'tmp/{self.file_uuid}.wav'
        self.path_file = Path(self.file_path)
        self._save()

    def __del__(self):
        """
        Деструктор
        """
        self._remove()

    def _save(self) -> None:
        """
        Сохранить файл во временной папке
        """
        try:
            with self.path_file.open("wb") as buffer:
                shutil.copyfileobj(self.file.file, buffer)
        finally:
            self.file.file.close()

    def _remove(self) -> None:
        """
        Удалить файл
        """
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def get_file_path(self) -> Path:
        """
        Получить путь к файлу
        """
        return self.path_file

    def get_file_uuid(self) -> str:
        """
        Получить UUID файла
        """
        return self.file_uuid
