"""Offline tests for free local Ollama mode."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import openai  # noqa: F401
except ImportError:
    stub = ModuleType("openai")
    stub.OpenAI = type("OpenAI", (), {})
    sys.modules["openai"] = stub

from ollama_engine import DEFAULT_OLLAMA_MODEL, explain_local, quiz_local, local_models, OllamaError
from sample_data import PREVIEW_QUIZ


class TestLocalOllama(unittest.TestCase):
    def test_local_model_list(self):
        with patch('ollama_engine._request', return_value={"models": [{"name": "qwen3.5:9b"}]}) as request:
            self.assertEqual(local_models(), ["qwen3.5:9b"])
            self.assertEqual(request.call_args.args[0], '/api/tags')

    def test_explanation_sends_persona_and_few_shot(self):
        with patch('ollama_engine._request', return_value={"message": {"content": "### Core idea\nA clear explanation."}}) as request:
            result = explain_local('DNS', 'Beginner', 'English')
            self.assertIn('clear explanation', result)
            args = request.call_args.args
            self.assertEqual(args[0], '/api/chat')
            self.assertEqual(args[1]['model'], DEFAULT_OLLAMA_MODEL)
            self.assertEqual(args[1]['messages'][0]['role'], 'system')
            self.assertIn('Example 1:', args[1]['messages'][1]['content'])
            self.assertFalse(args[1]['stream'])

    def test_refinement_uses_previous_answer(self):
        with patch('ollama_engine._request', return_value={"message": {"content": "Simpler version"}}) as request:
            explain_local('TCP', 'Beginner', 'English', previous='old text', feedback='Make it simpler')
            prompt = request.call_args.args[1]['messages'][1]['content']
            self.assertIn('old text', prompt)
            self.assertIn('Make it simpler', prompt)

    def test_quiz_sends_schema_and_validates(self):
        with patch('ollama_engine._request', return_value={"message": {"content": json.dumps({"questions": PREVIEW_QUIZ})}}) as request:
            quiz = quiz_local('TCP', 'Medium', 'English', count=3)
            self.assertEqual(len(quiz), 3)
            payload = request.call_args.args[1]
            self.assertEqual(payload['format']['properties']['questions']['minItems'], 3)
            self.assertIn('JSON schema', payload['messages'][1]['content'])

    def test_missing_content_raises(self):
        with patch('ollama_engine._request', return_value={'message': {'content': ''}}):
            with self.assertRaises(OllamaError):
                explain_local('TCP', 'Beginner', 'English')


if __name__ == '__main__':
    unittest.main()
