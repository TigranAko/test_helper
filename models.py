from pydantic import BaseModel, Field


class Answer(BaseModel):
    text: str = Field(description="Текст варианта ответа")
    isCorrect: None | bool = None


class Question(BaseModel):
    question: str = Field(description="Текст вопроса")
    answers: list[Answer]


class TestData(BaseModel):
    title: str | None
