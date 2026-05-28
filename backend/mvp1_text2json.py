import docx2txt
from langchain_openrouter import ChatOpenRouter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenrouterConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    openrouter_api_key: SecretStr


class Answer(BaseModel):
    text: str = Field(description="Текст варианта ответа")


class Question(BaseModel):
    question: str = Field(description="Текст вопроса")
    answers: list[Answer] = Field(
        description="Список  возможных ответов (без указания правильных)"
    )


class Test(BaseModel):
    questions: list[Question] = Field(description="Список всех вопросов теста")


config = OpenrouterConfig()


llm = ChatOpenRouter(
    api_key=config.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
    model="openrouter/free",
    temperature=0.1,
)

structured_llm = llm.with_structured_output(Test)


def parse_test(raw_text: str) -> Test:
    spliter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = spliter.split_text(raw_text)
    all_questions = []
    tail = ""
    for i, chunk in enumerate(chunks, 1):
        chunk = chunk.replace("\n\n", "\n")
        print(f"Чанк: {i}/{len(chunks)}\nДлина чанка {len(chunk)} символов")
        print(chunk)
        questions = parse_chunk(chunk, tail)  # TODO: Тут используется модель
        all_questions.extend(questions)
        print(f"Добавлено {len(questions)} вопросов")
        print("NEED FOR SPLIT", questions)
        tail = chunk[-500:] if len(chunk) > 500 else chunk
        print("Обрезанный конец", tail)
        # TODO: нужно выбрать последний вопрос предыдущего чанка
    # TODO: нужо обрабатыввать последний вопрос


def parse_chunk(chunk_text: str, tail: str) -> list[Question]:
    return []
    prompt = f"""
    Извлеки из приведенного ниже текста все вопросы и варианты ответов.

    Текст:
    {raw_text}
    """
    result = structured_llm.invoke(prompt)
    return result


def main():
    print("Запуск mvp1")
    test = """
    Развитием и поддержкой ОС Android, главным образом, занимается компания:
1). Android
2). Apple
=3). Google
4). Microsoft
Ядро какой операционной системы использовалось в качестве базы для ОС Android?
=1). Linux
2). Windows
3). Mac OS
4). OS/2
"""
    test = docx2txt.process("./files/01_02.docx")
    try:
        data = parse_test(test)

        with open("files/text_01_03.json", "w", encoding="utf-8") as file:
            file.write(data.model_dump_json(indent=4))

    except Exception as e:
        print("Не удалось распознать ", e)


if __name__ == "__main__":
    main()
