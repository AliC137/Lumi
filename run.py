# run.py
import uvicorn
import os
import uvicorn
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()


# def main():
#     uvicorn.run("aistudio.main:app", host="127.0.0.1", port=8000, reload=True)


def main():
    uvicorn.run(
        "aistudio.main:app",
        host="127.0.0.1",
        port=8005,
        reload=True,
        reload_dirs=[os.path.abspath("./aistudio")]
    )


if __name__ == "__main__":
    main()
