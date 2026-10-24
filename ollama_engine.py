"""Local Ollama integration: real generative AI, no paid cloud API key.

Connects only to 127.0.0.1, so user prompts are sent to the Ollama server
running on the same computer, not to a third-party cloud service.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai_engine import StudyBuddyError, quiz_schema, validate_quiz
from prompts import TUTOR_PERSONA, QUIZ_PERSONA, explanation_input, refinement_input, quiz_input

OLLAMA_BASE = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "qwen3.5:9b"


class OllamaError(Exception):
    """Raised when the local Ollama service/model is unavailable."""


def _request(path: str, payload: dict | None = None, timeout: int = 180) -> dict:
    url = OLLAMA_BASE + path
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("error", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            detail = ""
        raise OllamaError(
            f"Ollama error HTTP {exc.code}: {detail or exc.reason}. "
            "If your model is missing, run: ollama pull qwen3.5:9b"
        ) from exc
    except (URLError, ConnectionError, TimeoutError, OSError) as exc:
        raise OllamaError(
            "Cannot connect to Ollama at localhost:11434. Open the Ollama app "
            "on your Mac, then retry."
        ) from exc
    except (ValueError, UnicodeDecodeError) as exc:
        raise OllamaError("Ollama returned an unreadable response.") from exc
    if not isinstance(parsed, dict):
        raise OllamaError("Ollama returned an unexpected response.")
    return parsed


def local_models() -> list[str]:
    """Return models installed on the user's computer (never downloads models)."""
    result = _request("/api/tags", timeout=3)
    models = result.get("models", [])
    return [m["name"] for m in models if isinstance(m, dict) and isinstance(m.get("name"), str)]


def _chat(model: str, persona: str, user_prompt: str, schema: dict | None = None) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": persona},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "think": False,
        "options": {"temperature": 0.2, "num_predict": 2200 if schema else 850},
    }
    if schema is not None:
        payload["format"] = schema
    result = _request("/api/chat", payload, timeout=180)
    message = result.get("message")
    text = message.get("content", "") if isinstance(message, dict) else ""
    if not isinstance(text, str) or not text.strip():
        raise OllamaError("Local model returned no answer. Try again or use another installed model.")
    return text.strip()


def explain_local(
    topic: str, level: str, language: str, model: str = DEFAULT_OLLAMA_MODEL,
    previous: str | None = None, feedback: str | None = None,
) -> str:
    if not topic.strip():
        raise StudyBuddyError("Enter a topic first.")
    if bool(previous) != bool(feedback):
        raise StudyBuddyError("Refinement needs both a previous answer and feedback.")
    prompt = (
        refinement_input(topic, level, language, previous or "", feedback or "")
        if previous and feedback
        else explanation_input(topic, level, language)
    )
    return _chat(model, TUTOR_PERSONA, prompt)


def quiz_local(
    topic: str, difficulty: str, language: str, count: int = 3,
    model: str = DEFAULT_OLLAMA_MODEL,
) -> list[dict]:
    if not topic.strip():
        raise StudyBuddyError("Enter a quiz topic first.")
    if count not in (3, 4, 5):
        raise StudyBuddyError("Choose between three and five questions.")
    schema = quiz_schema(count)
    user_prompt = (
        quiz_input(topic, difficulty, language, count)
        + "\nOutput JSON only, matching this schema exactly:\n"
        + json.dumps(schema, ensure_ascii=False)
    )
    result = _chat(model, QUIZ_PERSONA, user_prompt, schema=schema)
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError as exc:
        raise StudyBuddyError("The local model returned invalid JSON. Please try again.") from exc
    if not isinstance(parsed, dict):
        raise StudyBuddyError("The local model returned an invalid quiz structure.")
    return validate_quiz(parsed, count)
