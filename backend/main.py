from pathlib import Path

import aiofiles
import docx2txt
from fastapi import FastAPI, UploadFile
from uvicorn import run

from mvp1_text2json import parse_test

app = FastAPI(title="Тест")


@app.get("/")
def main():
    return "Hello from test-helper!"


@app.post("/file")
async def upload_file(test_file: UploadFile):
    print(test_file.content_type)
    print(test_file.filename)
    file_title = test_file.filename.split(".")[0]
    # TODO: now if . in file than error
    # TODO: problem encoding
    folder = Path("files")
    folder.mkdir(exist_ok=True)
    async with aiofiles.open(f"files/{test_file.filename}", "wb") as file:
        while chunk := await test_file.read(1024):
            await file.write(chunk)
            # TODO: файл можно не сохранять

    test = docx2txt.process(f"./files/{test_file.filename}")
    try:
        data = parse_test(test)

        with open(f"files/{file_title}.json", "w", encoding="utf-8") as file:
            file.write(data.model_dump_json(indent=4))

        return {
            "filename": test_file.filename,
            "file_title": file_title,
            "result": data.model_dump(),
        }

    except Exception as e:
        print("Не удалось распознать ", e)

    return {
        "filename": test_file.filename,
        "file_title": file_title,
        "result": "may be error",
    }


if __name__ == "__main__":
    run(app=app)
