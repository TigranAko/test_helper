import docx2txt
from langchain_openrouter import ChatOpenRouter
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
    # test = docx2txt.process("./files/text_01_03.docx")
    try:
        data = parse_test(test)

        with open("files/text_01_03.json", "w", encoding="utf-8") as file:
            file.write(data.model_dump_json(indent=4))

    except Exception as e:
        print("Не удалось распознать ", e)


if __name__ == "__main__":
    main()
