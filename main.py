from pathlib import Path

import aiofiles
from fastapi import FastAPI, UploadFile
from uvicorn import run

app = FastAPI(title="Тест")


@app.get("/")
def main():
    return "Hello from test-helper!"


@app.post("/file")
async def upload_file(test_file: UploadFile):
    print(test_file.content_type)
    print(test_file.filename)
    folder = Path("files")
    folder.mkdir(exist_ok=True)
    async with aiofiles.open(f"files/{test_file.filename}", "wb") as file:
        while chunk := await test_file.read(1024):
            await file.write(chunk)
            # TODO: файл можно не сохранять
    return {"filename": test_file.filename}


if __name__ == "__main__":
    run(app=app)
