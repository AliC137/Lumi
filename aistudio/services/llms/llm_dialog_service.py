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
from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from aistudio.services.translate_service import TranslateService
from aistudio.config.config import S3Config


class LLMDialogService:
    def __init__(self, config: S3Config, type_dialog: str = "profile", id: int = None):
        self.type_dialog = type_dialog
        self.id = id
        self.context_path_books = f"tmp/dialogs/{self.type_dialog}/books"
        self.context_file_path = f"tmp/dialogs/{self.type_dialog}/{self.id}"
        self.context = self.get_context()
        self.activate_storage()
        self.translate_service = TranslateService(config)



    def get_context(self):
        os.makedirs("tmp/dialogs", exist_ok=True)
        os.makedirs("tmp/dialogs/{self.type_dialog}", exist_ok=True)
        if not os.path.exists(self.context_file_path):
            context = {"type_dialog": self.type_dialog,
                       "contexts": [],
                       "queries": []
            }
            return context
        with open(self.context_file_path, 'r') as file:
             return json.load(file)

    def activate_storage(self):
        os.makedirs(self.context_path_books, exist_ok=True)

    def forget(self):
        if os.path.exists(self.context_file_path):
            os.remove(self.context_file_path)

    def save_pdf(self, pdf_file_stream):

        file_paph = f"{self.context_path_books}/pdf_{self.id}.pdf"
        with open(file_paph, "wb") as f:
            # 4. Write the content of the BytesIO object to the file
            # You can use .read() to get all content, or .getvalue() for the entire buffer.
            f.write(pdf_file_stream.read())
        return file_paph

    def extract_text(self, file_path):
        all_extracted_text = []

        pdf_file = pymupdf.open(file_path)
        extracted_images = []
        for page_index in range(len(pdf_file)):
            page = pdf_file.load_page(page_index)
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list, start=1):
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                # Convert bytes to PIL Image object
                image = Image.open(io.BytesIO(image_bytes))
                text = pytesseract.image_to_string(image)

                if text:  # Only add if text is found
                     all_extracted_text.append(text)

        return "\n".join(all_extracted_text)

    def download_library_book(self):
        try:
            api_key = "kb_HaxfhtegAdRVy5iOoQ5nsu3193B2TMxFsRG8VmPc5e7CSikEOWm70YW7YYIJVIrI"
            header = {"Authorization": f"Bearer {api_key}"}
            url = f"http://kitobdor.tj/api/books/{self.id}/content?full_text=true"
            response = requests.get(url, headers=header)
            response.raise_for_status()
            book_data = response.json()
            extracted_text = book_data['text']
            if book_data['content_type'] != "text":
                file_url = f"http://kitobdor.tj{book_data['file_path']}"
                response = requests.get(file_url)
                pdf_file_stream = io.BytesIO(response.content)
                file_path = self.save_pdf(pdf_file_stream)
                extracted_text = self.extract_text(file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

            #            reader = PdfReader(pdf_file_stream)
#            extracted_text = ""
#            for page in reader.pages:
#                extracted_text += page.extract_text()

            print(f"{extracted_text}")
        except requests.exceptions.HTTPError as err:
            raise err

    def load_books(self):
        if not os.path.exists(f"{self.context_file_path}/{{self.id}}"):
            if self.type_dialog == "library":
                self.download_library_book()

    def test_dictionary(self, question, dictionary):
        for item in dictionary:
            if item in question.lower():
                return True
        return False
    def detect_info_context(self, question):
        dictionary = ["республик", "таджикист", "истори", "государств"]
        if self.test_dictionary(question, dictionary):
            return 'info'
        return None

    def detect_success_class(self, question):
        dictionary = ["успеваемост", "оценок", "анализ успеваимост"]
        if self.test_dictionary(question, dictionary):
            return 'teacher_class'
        return None
    def detect_profile_context(self, question):
        context = self.detect_info_context(question)
        if context:
            return context
        context = "student"
        if self.id == 920770:
            context = "teacher"
        elif self.id == 394005:
            context = "parent"
        if context == "teacher":
            success_context = self.detect_success_class(question)
            if success_context:
                context = success_context
        return context

    def activate_context(self, lang: str = None, question: str = ''):
        # self.load_books()
        if self.type_dialog == "library":
            context = f"{self.id}"
            if self.id == 287:
                context = "lumi"
            if self.id == 286:
                context = "omar"

            loader = TextLoader(f"tmp/dialogs/library/books/ru_txt/{context}", encoding="utf-8")
            documents = loader.load()
            rag_service.add_documents(documents, self.id)
        else:
            context = self.detect_profile_context(question)

            #context = "student"
            #if self.id == 920770:
            #    context = "teacher"
            #elif self.id == 394005:
            #    context = "parent"
            loader = TextLoader(f"tmp/dialogs/profile/contexts/{lang}/{context}", encoding="utf-8")
            documents = loader.load()
            rag_service.common_context(documents)


#            if len(self.context["contexts"]) == 0:
#            rag_service.add_documents(documents)

    def answer_filter(self, answer: str) -> str:
        #if self.type_dialog == "library":
        split_answer = answer.split("</think>")
        if len(split_answer) > 1:
            return split_answer[1]
        return answer
    
    def _detect_language(self, text):
        lang = self.translate_service.detect_language(text)
        if lang in ['ru', 'tg']:
            return lang
        return 'tg'

    def _correction(self, text:str):
        return text.replace("резюме", "дела")

    def answer(self, question: str) -> dict:
        rag_service.forget()
        lang = self._detect_language(question)
        if lang == 'tg':
            question = self.translate_service.translate(question, language= 'ru', source_language = 'tg')
            question = self._correction(question)
        self.activate_context('ru', question)
        #rag_service.common_context("Жила была бабушка")
        answer = rag_service.query(question)
        answer = self.answer_filter(answer)
        if lang == 'tg':
            answer = self.translate_service.translate(answer, language= 'tg', source_language = 'ru')

        return {"answer": answer}
