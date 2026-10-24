"""OpenAI integration with schema-checked quiz output."""

import json
from typing import Any

from openai import OpenAI

from prompts import (
    QUIZ_PERSONA,
    TUTOR_PERSONA,
    explanation_input,
    quiz_input,
    refinement_input,
)

DEFAULT_MODEL = "gpt-4.1-mini"


class StudyBuddyError(Exception):
    """Raised when an AI response is empty or not usable."""


def _client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, timeout=40.0, max_retries=1)


def explain_topic(
    api_key: str, topic: str, level: str, language: str,
    previous: str | None = None, feedback: str | None = None,
    model: str = DEFAULT_MODEL, client: Any = None,
) -> str:
    """Generate or refine a concept explanation using the Responses API."""
    if not topic.strip():
        raise StudyBuddyError("Enter a topic first.")
    if bool(previous) != bool(feedback):
        raise StudyBuddyError("Refinement needs both a previous answer and feedback.")

    prompt = (
        refinement_input(topic, level, language, previous or "", feedback or "")
        if previous and feedback
        else explanation_input(topic, level, language)
    )
    sdk = client if client is not None else _client(api_key)
    response = sdk.responses.create(
        model=model,
        instructions=TUTOR_PERSONA,
        input=prompt,
        max_output_tokens=650,
        store=False,
    )
    result = (response.output_text or "").strip()
    if not result:
        raise StudyBuddyError("The AI returned an empty explanation. Please retry.")
    return result


def quiz_schema(count: int) -> dict:
    """Structured Outputs schema; every object field is required."""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "questions": {
                "type": "array",
                "minItems": count,
                "maxItems": count,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "question": {"type": "string"},
                        "options": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 4},
                        "answer_index": {"type": "integer", "minimum": 0, "maximum": 3},
                        "explanation": {"type": "string"},
                    },
                    "required": ["question", "options", "answer_index", "explanation"],
                },
            }
        },
        "required": ["questions"],
    }


def validate_quiz(data: dict, count: int) -> list[dict]:
    """Fail safely if the returned quiz cannot be graded reliably."""
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != count:
        raise StudyBuddyError("The AI did not return the requested number of questions.")
    for index, q in enumerate(questions, start=1):
        if not isinstance(q, dict) or not isinstance(q.get("question"), str):
            raise StudyBuddyError(f"Question {index} is incomplete.")
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4 or any(not isinstance(x, str) or not x.strip() for x in opts):
            raise StudyBuddyError(f"Question {index} must have four choices.")
        if len(set(opts)) != 4:
            raise StudyBuddyError(f"Question {index} contains duplicate choices.")
        if type(q.get("answer_index")) is not int or not 0 <= q["answer_index"] <= 3:
            raise StudyBuddyError(f"Question {index} has an invalid answer key.")
        if not isinstance(q.get("explanation"), str) or not q["explanation"].strip():
            raise StudyBuddyError(f"Question {index} is missing its teaching explanation.")
    return questions


def generate_quiz(
    api_key: str, topic: str, difficulty: str, language: str, count: int = 3,
    model: str = DEFAULT_MODEL, client: Any = None,
) -> list[dict]:
    if not topic.strip():
        raise StudyBuddyError("Enter a quiz topic first.")
    if count not in (3, 4, 5):
        raise StudyBuddyError("Choose between three and five questions.")
    sdk = client if client is not None else _client(api_key)
    response = sdk.responses.create(
        model=model,
        instructions=QUIZ_PERSONA,
        input=quiz_input(topic, difficulty, language, count),
        text={"format": {
            "type": "json_schema", "name": "study_quiz",
            "strict": True, "schema": quiz_schema(count),
        }},
        max_output_tokens=1800,
        store=False,
    )
    if not response.output_text:
        raise StudyBuddyError("The AI returned an empty quiz. Please retry.")
    try:
        parsed = json.loads(response.output_text)
    except json.JSONDecodeError as error:
        raise StudyBuddyError("The AI returned an unreadable quiz. Please retry.") from error
    if not isinstance(parsed, dict):
        raise StudyBuddyError("The AI returned the wrong quiz structure.")
    return validate_quiz(parsed, count)


def grade_quiz(questions: list[dict], answers: list[int | None]) -> tuple[int, list[bool]]:
    """Deterministic grading in Python; no extra API call or hallucinated score."""
    if len(questions) != len(answers):
        raise ValueError("Answers must match quiz length.")
    results = [answer == q["answer_index"] for q, answer in zip(questions, answers)]
    return sum(results), results
