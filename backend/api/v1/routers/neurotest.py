import json
from pathlib import Path

import aiofiles
import docx2txt
from fastapi import APIRouter, Depends, UploadFile
from services.json2answer import (
    JsonToAnswerService,
    TestOutput,
    get_json2answer_service,
)
from services.text2json import (
    Test,
    TextToJsonService,
    get_text2json_service,
)

router = APIRouter(prefix="/api/v1")


@router.get("/")
def main():
    return "Hello from NeuroTest!"


@router.post("/files")
async def downloand_user_file(test_file: UploadFile) -> dict[str, str]:
    user_file: str = test_file.filename
    file_title: str = "_".join(
        user_file.split(".")[:-1]
    )  #  Лишние точки заменяются на _
    file_extension: str = user_file.split(".")[-1]
    file_name: str = f"{file_title}.{file_extension}"
    path: str = f"files/{file_title}.{file_extension}"
    content_type: str = test_file.content_type

    async with aiofiles.open(f"files/{file_title}.{file_extension}", "wb") as file:
        while chunk := await test_file.read(1024):
            await file.write(chunk)
    return {
        "input": user_file,
        "title": file_title,
        "extension": file_extension,
        "full_name": file_name,
        "path": path,
        "content_type": content_type,
    }


@router.get("/files/docx")
async def get_list_docx_files() -> list[str]:
    """Получить список всех файлов с расширением .docx (тексты тестов)"""
    dir = Path("files/")
    return [item.name for item in dir.iterdir() if item.name.endswith(".docx")]


@router.post("/files/json_text")
async def create_json(
    file_title: str,
    text2json: TextToJsonService = Depends(get_text2json_service),
) -> Test:
    """Создать JSON без ответов"""
    text = docx2txt.process(f"files/{file_title}.docx")
    questions_without_answers: Test = text2json.parse_test(text)
    async with aiofiles.open(
        f"files/{file_title}_text.json", "w", encoding="utf-8"
    ) as file:
        await file.write(questions_without_answers.model_dump_json())
    return questions_without_answers


@router.get("/files/json_text")
async def get_list_json_text_files() -> list[str]:
    """Получить список файлов с расширением .json но без ответов (промежуточные резульатаы)"""
    dir = Path("files/")
    return [item.name for item in dir.iterdir() if item.name.endswith("_text.json")]


@router.post("/files/json_answer")
async def create_json_answers(
    file_title: str,
    json2answer: JsonToAnswerService = Depends(get_json2answer_service),
) -> TestOutput:
    """Создать JSON с ответами"""
    async with aiofiles.open(f"files/{file_title}_text.json", encoding="utf-8") as file:
        data = await file.read()
        data = json.loads(data)
    answers: TestOutput = json2answer.process_test(data)
    answers_str = answers.model_dump_json(indent=4)
    async with aiofiles.open(
        f"files/{file_title}_answers.json", "w", encoding="utf-8"
    ) as file:
        await file.write(answers_str)

    return answers


@router.get("/files/json_answer")
async def get_list_json_anwer_files() -> list[str]:
    """Получить список файлов с расширением .json с ответами (Какие тесты уже есть)"""
    dir = Path("files/")
    return [item.name for item in dir.iterdir() if item.name.endswith("_answers.json")]
