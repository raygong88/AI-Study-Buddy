import json
import sys
import unittest
from types import ModuleType, SimpleNamespace

# Let pure-logic/mock-client tests run offline even if optional API SDK is not installed.
# In a normal installed project, the actual OpenAI package is imported instead.
try:
    from openai import OpenAI  # noqa: F401
except ImportError:
    stub = ModuleType("openai")
    stub.OpenAI = type("OpenAI", (), {})
    sys.modules["openai"] = stub

from ai_engine import StudyBuddyError, explain_topic, generate_quiz, grade_quiz, validate_quiz
from prompts import FEW_SHOT_EXPLANATIONS, TUTOR_PERSONA, refinement_input
from sample_data import PREVIEW_QUIZ


class FakeResponses:
    def __init__(self, output_text):
        self.output_text = output_text
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class FakeClient:
    def __init__(self, output_text):
        self.responses = FakeResponses(output_text)


class TestStudyBuddy(unittest.TestCase):
    def test_grade_quiz(self):
        correct, results = grade_quiz(PREVIEW_QUIZ, [1, 0, 0])
        self.assertEqual(correct, 2)
        self.assertEqual(results, [True, True, False])

    def test_quiz_validator_rejects_invalid_answer_index(self):
        wrong = [dict(q) for q in PREVIEW_QUIZ]
        wrong[0]["answer_index"] = 9
        with self.assertRaises(StudyBuddyError):
            validate_quiz({"questions": wrong}, 3)

    def test_explain_uses_persona_and_fewshot(self):
        client = FakeClient("### Core idea\nA clear explanation.")
        output = explain_topic("test-key", "DNS", "Beginner", "English", client=client)
        self.assertIn("clear explanation", output)
        call = client.responses.calls[0]
        self.assertEqual(call["instructions"], TUTOR_PERSONA)
        self.assertIn("DNS", call["input"])
        self.assertIn("Example 1:", FEW_SHOT_EXPLANATIONS)
        self.assertEqual(call["store"], False)

    def test_refinement_includes_feedback_and_previous(self):
        prompt = refinement_input("DNS", "Beginner", "English", "Original text", "Make it simpler")
        self.assertIn("Original text", prompt)
        self.assertIn("Make it simpler", prompt)

    def test_generate_quiz_uses_structured_outputs(self):
        client = FakeClient(json.dumps({"questions": PREVIEW_QUIZ}))
        result = generate_quiz("test-key", "TCP", "Medium", "English", count=3, client=client)
        self.assertEqual(len(result), 3)
        fmt = client.responses.calls[0]["text"]["format"]
        self.assertEqual(fmt["type"], "json_schema")
        self.assertTrue(fmt["strict"])
        self.assertEqual(fmt["schema"]["properties"]["questions"]["minItems"], 3)


if __name__ == "__main__":
    unittest.main()
