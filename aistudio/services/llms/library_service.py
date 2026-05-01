"""
Класс диалога с LLM
"""
import os
import json
import requests
from PyPDF2 import PdfReader
import io
import pymupdf
from PIL import Image
import pytesseract
from aistudio.langchain_loaders.rag_singleton import rag_service
from aistudio.services.translate_service import TranslateService
from aistudio.config.config import S3Config


class LibraryService:
    def __init__(self, config: S3Config):
        self.context_path_books = f"tmp/dialogs/library/books"
        self.init_folders()
        self.api_key = "kb_HaxfhtegAdRVy5iOoQ5nsu3193B2TMxFsRG8VmPc5e7CSikEOWm70YW7YYIJVIrI"
        self.header = {"Authorization": f"Bearer {self.api_key}"}
        self.tg_data_path = f"tmp/dialogs/library/books/tg"
        self.ru_data_path = f"tmp/dialogs/library/books/ru"
        self.translate_service = TranslateService(config)


    def init_folders(self):
        os.makedirs("tmp/dialogs", exist_ok=True)
        os.makedirs("tmp/dialogs/library", exist_ok=True)
        os.makedirs("tmp/dialogs/library/books", exist_ok=True)
        os.makedirs("tmp/dialogs/library/books/tg", exist_ok=True)
        os.makedirs("tmp/dialogs/library/books/ru", exist_ok=True)

    def get_file_path(self, id: int, format: str):
        return f"{self.context_path_books}/{format}_{id}.{format}"

    def save_file(self, pdf_file_stream, file_path):
        with open(file_path, "wb") as f:
            # 4. Write the content of the BytesIO object to the file
            # You can use .read() to get all content, or .getvalue() for the entire buffer.
            f.write(pdf_file_stream.read())
        return file_path

    def extract_text(self, file_path):
        all_extracted_text = []
        pdf_file = pymupdf.open(file_path)
        for page_index in range(len(pdf_file)):
            page = pdf_file.load_page(page_index)
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list, start=1):
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
#                image_ext = base_image["ext"]
                # Convert bytes to PIL Image object
                image = Image.open(io.BytesIO(image_bytes))
                try:
                    text = pytesseract.image_to_string(image, lang='tgk+rus' )
                except Exception as e:
                    text = str(e)

                if text:  # Only add if text is found
                     all_extracted_text.append(text)

        return "\n".join(all_extracted_text)

    def translate_tg_to_ru(self, id: int) -> None:
        ru_json_path = f"{self.ru_data_path}/{id}.json"
        if os.path.exists(ru_json_path):
            return
        json_path = f"{self.tg_data_path}/{id}.json"
        with open(json_path, 'r') as file:
             data = json.load(file)
             ru_data = data.copy()
             try:
                 title  = self.translate_service.translate(data['title'],language='ru', source_language='tg')
                 ru_data['title'] = title
                 ru_data['text'] = self.translate_service.translate(data['text'], language='ru', source_language='tg')
             except Exception as e:
                 err = str(e)
                 print(f"Error: {err}")
             with open(ru_json_path, "w") as ru_json_file:
                   json.dump(ru_data, ru_json_file, indent=4)

    def make_context_file(self, language: str, id: int) -> None:
        try:
            source_path = self.ru_data_path if language == 'ru' else self.tg_data_path
            dist_path = f"{self.context_path_books}/{language}_txt"

            with open(f"{source_path}/{id}.json", 'r') as file:
                data = json.load(file)

                with open(f"{dist_path}/{id}", "w", encoding="utf-8") as tfile:
                    tfile.write(data["text"])
        except Exception as ex:
           err = str(ex)
           print(f"{err}")

    def load_books(self):
        max_book_id = 300

        for i in  range(251, max_book_id):
            try:
                json_path = f"{self.tg_data_path}/{i}.json"
                if os.path.exists(json_path):
                    self.translate_tg_to_ru(i)
                    self.make_context_file("ru", i)
                    self.make_context_file("tg", i)
                    continue
                url = f"http://kitobdor.tj/api/books/{i}/content?full_text=true"
                response = requests.get(url, headers=self.header)
                response.raise_for_status()
                book_data = response.json()
                file_path = self.get_file_path(i, book_data['format'])
                if not os.path.exists(file_path):
                    file_url = f"http://kitobdor.tj{book_data['file_path']}"
                    response = requests.get(file_url)
                    pdf_file_stream = io.BytesIO(response.content)
                    file_path = self.save_file(pdf_file_stream, file_path)
                data = {"book_id": i,
                        "title": book_data['title'],
                        "file_path": file_path,
                        "type": book_data['format'],
                        "language": 'tg',
                        "content_type": book_data['content_type'],
                }
                if book_data['content_type'] == 'image':
                    data["text"] = self.extract_text(file_path)
                else:
                    data["text"] = book_data['text']

                #books.append(data)

                with open(json_path, "w") as json_file:
                    json.dump(data, json_file, indent=4)
                self.translate_tg_to_ru(i)
                self.make_context_file("ru", i)
                self.make_context_file("tg", i)

            except Exception as e:
                continue
        print("finish load")

