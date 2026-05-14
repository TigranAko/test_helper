from pathlib import Path

import aiofiles
import docx2txt
from fastapi import FastAPI, UploadFile
from uvicorn import run

from mvp1_text2json import parse_test
from mvp2_json2answer import process_test


from time import sleep
import json

app = FastAPI(title="Тест")


@app.get("/")
def main():
    return "Hello from test-helper!"


@app.post("/file")
async def upload_file(test_file: UploadFile):
    # TODO: нужно разделить на несколько эндпоинтов
    print(test_file.content_type)
    print(test_file.filename)
    file_title = test_file.filename.split(".")[0]
    # TODO: now if . in file than error
    # TODO: problem encoding
    folder = Path("files")
    folder.mkdir(exist_ok=True)
    async with aiofiles.open(f"backend/files/{test_file.filename}", "wb") as file:
        while chunk := await test_file.read(1024):
            await file.write(chunk)
            # TODO: файл можно не сохранять

    test_json = docx2txt.process(f"backend/files/{test_file.filename}")
    # try:
    data = parse_test(test_json)

    with open(f"backend/files/{file_title}.json", "w", encoding="utf-8") as file:
        file.write(data.model_dump_json())

    sleep(3)

    with open(f"backend/files/{file_title}.json") as file:
        answers = process_test(json.load(file))

    return {
        "filename": test_file.filename,
        "file_title": file_title,
        "result_json": data.model_dump(),
        "answers": answers,
    }

    # except Exception as e:
    #     print("Не удалось распознать ", e)

    return {
        "filename": test_file.filename,
        "file_title": file_title,
        "result": "may be error",
    }


if __name__ == "__main__":
    run(app=app)
