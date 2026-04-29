from langchain_openrouter import ChatOpenRouter
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenrouterConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
    )
    openrouter_api_key: SecretStr


class Answer(BaseModel):
    text: str = Field(description="Текст варианта ответа")


class Question(BaseModel):
    question: str = Field(description="Текст вопроса")
    answers: list[str] = Field(
        description="Список  возможных ответов (без указания правильных)"
    )


class Test(BaseModel):
    questions: list[Question] = Field(description="Список всех вопросов теста")


# Just copy the exact text of each question and the exact text of each answer option.
# template = """
# You are a COPY MACHINE. Your ONLY task is to extract questions and their answer options from the given and output in a strict fromat.
# DO NOT answer the questions, DO NOT analyze the content, DO NOT change any words. DO NOT tranclate, DO NOT correct spelling or grammar, DO NOT invent anything.
# Just copy the text EXACTLY.

# Output a JSON object with a single key "questions" that contains an array of objects, eatch with "question" and "answers" (array of strings).

# {{format_instructions}}

# Rules:
# - Keep all queestion text EXACTLY as it is, including leading numbers like "1.".
# - Keep all answer markers (like "1." or "a)" or another marker), etc. inside the answer text.
# - Return ONLY the JSON object, without any commentary or markdown fences.

# --- EXAMPLW START ---
# Input text:
# Сколько будет 2+2?
# а) 3
# б) 4
# в) 5
# Развитием и поддержкой OS Android, главным образом, занимается компания:
# 1. Android
# 2. Apple
# 3. Google
# 4. Microsoft

# Ouput JSON:
# {{
#     "questions": [
#         {{
#             "question": "Сколько будет 2+2?",
#             "answers": ["3", "4", "5"]
#         }}
#         {{
#             "question": "Развитием и поддержкой OS Android, главным образом, занимается компания",

#             "answers": ["Android", "Apple", "Google", "Microsoft"]
#         }}
#     ]
# }}

# Now process the text below and output ONLY the JSON object (no extra text, no markdown fences):
# {{raw_text}}
# """

# template = """
# You are a COPY MACHINE. Your ONLY job is to convert the provided test into JSON strucure.
# DO NOT answer the questions. DO NOT analyze the content. DO NOT correct grammar. DO NOT invent anything.

# {{format_instructions}}

# Rules:
# - Keep all queestion text EXACTLY as it is, including leading numbers like "1.".
# - Keep all answer markers (like "1." or "a)" or another marker), etc. inside the answer text.
# - Set ALL "isCorrect" fields to null.
# - Return ONLY the JSON object, without any commentary or markdown fences.

# Here is an example of how a single question should look:
# {{
#     "title": "",
#     "questions": [
#         {{
#             "queston": "Сколько бует 2+2?",
#             "answers": [
#                 {{"text": "3", "isCorrect": null}},
#                 {{"text": "4", "isCorrect": null}},
#                 {{"text": "5", "isCorrect": null}}
#             ]
#         }}
#     ]
# }}

# Now process the following text and output the JSON:
# {{raw_text}}
# """

# prompt = ChatPromptTemplatete(
#     template=template,
#     input_variables=["raw_text"],
#     partitial_variables={"format_instructions": parser.get_format_instructions()},
# )


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
    try:
        data = parse_test(test)
        print(data)
        print(data.model_dump())
    except Exception as e:
        print("Не удалось распознать ", e)


if __name__ == "__main__":
    main()
