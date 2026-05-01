"""
Сервис конвертации docx2txt
"""
import docx2txt

class Docx2TxtService:
    def __init__(self):
        """
        Конструктор
        """
        pass

    def _convert(self, file):
        docx_file_path = f"tmp/docx/{file}.docx"
        # Specify the desired path for the output TXT file
        txt_file_path = f"tmp/docx/{file}.txt"

        # Extract text from the DOCX file
        text_content = docx2txt.process(docx_file_path)

        # Write the extracted text to a TXT file
        with open(txt_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(text_content)
        return True

    def convert(self):
        self._convert("student")
        self._convert("teacher")
        self._convert("parent")
        self._convert("info")
        return True