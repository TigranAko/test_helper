from time import sleep

from langchain_cerebras import ChatCerebras
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class TavilyConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    TAVILY_API_KEY: SecretStr
    CEREBRAS_API_KEY: SecretStr


config = TavilyConfig()


# ---------- Модели ----------
class Answer(BaseModel):
    text: str
    isCorrect: bool


class QuestionOutput(BaseModel):
    question: str
    answers: list[Answer]


class TestOutput(BaseModel):
    questions: list[QuestionOutput]


# ---------- Инструменты ----------
search = TavilySearch(
    max_results=2,
    search_depth="basic",
    tavily_api_key=config.TAVILY_API_KEY.get_secret_value(),
)

llm = ChatCerebras(
    api_key=config.CEREBRAS_API_KEY,
    model="gpt-oss-120b",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}},
    timeout=180,
)

parser = PydanticOutputParser(pydantic_object=QuestionOutput)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Ты — эксперт, определяющий правильные ответы на вопросы.
Используй ТОЛЬКО результаты поиска, приведённые ниже. Если информации недостаточно, отвечай на основе общеизвестных фактов, но не выдумывай.
Верни JSON с ответом строго по инструкции.

{format_instructions}

Вопрос:
{question}

Варианты ответа:
{answers}""",
        ),
        (
            "user",
            "Результаты поиска:\n{search_results}\n\nОпредели правильные варианты. Если их несколько, отметь все.",
        ),
    ]
)


def format_answers(answers: list[Answer]) -> str:
    return "\n".join(f"{i}. {a.text}" for i, a in enumerate(answers, 1))


def process_single_questions(
    question_text: str, answers: list[dict["text", str]]
) -> QuestionOutput:
    formatted_answers = "\n".join(
        f"{i}) {a.get('text')}" for i, a in enumerate(answers, 1)
    )
    search_results = search.invoke(question_text)
    print(search_results, type(search_results))
    search_text = "\n".join(r["content"] for r in search_results.get("results"))

    chain = prompt | llm | parser
    result = chain.invoke(
        {
            "question": question_text,
            "answers": formatted_answers,
            "search_results": search_text,
            "format_instructions": parser.get_format_instructions(),
        }
    )
    return result


def process_test(input: dict) -> TestOutput:
    questions_data = input["questions"]
    output_questions = []
    for idx, q in enumerate(questions_data):
        print(f"Вопрос {idx + 1}/{len(questions_data)}...")
        sleep(2)
        result = process_single_questions(q["question"], q["answers"])
        print(result, type(result))
        output_questions.append(result)
    print(output_questions, type(output_questions))
    print((test_output := TestOutput(questions=output_questions)), type(test_output))
    return TestOutput(questions=output_questions)


# ---------- Использование ----------
if __name__ == "__main__":
    # Пример исходного JSON (как в вопросе)
    input_json = {
        "questions": [
            {
                "question": "1. Матрица, размером (1х5) называется..........",
                "answers": [
                    {"text": "матрица-столбец"},
                    {"text": "единичная"},
                    {"text": "матрица-строка"},
                ],
            },
            {
                "question": "2. Матрица (1 0 0 0 5 0 0 0 9) называется...",
                "answers": [
                    {"text": "Единичная"},
                    {"text": "Нулевая"},
                    {"text": "Диагональная"},
                    {"text": "Симметричная"},
                ],
            },
        ]
    }

    test_in = input_json  # TestInput(**input_json)
    test_out = process_test(test_in)
    print(test_out.model_dump_json(indent=2))
    with open("files/test_answer.json", "w", encoding="utf-8") as file:
        file.write(test_out.model_dump_json(indent=4))
