from time import sleep
from typing import Literal

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


class JsonToAnswerService:
    def process_single_questions(
        self,
        question_text: str,
        answers: list[dict[Literal["text"], str]],
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

    def process_test(self, input: dict) -> TestOutput:
        questions_data = input["questions"]
        output_questions = []
        for idx, q in enumerate(questions_data):
            print(f"Вопрос {idx + 1}/{len(questions_data)}...")
            sleep(2)
            result = self.process_single_questions(q["question"], q["answers"])
            print(result, type(result))
            output_questions.append(result)
        print(output_questions, type(output_questions))
        print(
            (test_output := TestOutput(questions=output_questions)), type(test_output)
        )
        return TestOutput(questions=output_questions)


def get_json2answer_service():
    return JsonToAnswerService()
