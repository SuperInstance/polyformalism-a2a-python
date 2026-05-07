"""
Test LLM encoder against known messages.
Requires DEEPINFRA_KEY environment variable.
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use urllib-based encoder
from polyformalism_a2a.llm_encode import LLMEncoder, create_deepinfra_encoder, SYSTEM_PROMPT


class TestSystemPrompt(unittest.TestCase):
    """Test that the system prompt is well-formed."""

    def test_prompt_contains_all_channels(self):
        for ch in ["Boundary", "Pattern", "Process", "Knowledge", "Social",
                    "Deep Structure", "Instrument", "Paradigm", "Stakes"]:
            self.assertIn(ch, SYSTEM_PROMPT)

    def test_prompt_requests_json(self):
        self.assertIn('"channels"', SYSTEM_PROMPT)
        self.assertIn('"salience"', SYSTEM_PROMPT)
        self.assertIn('"tolerance"', SYSTEM_PROMPT)


class TestJSONParsing(unittest.TestCase):
    """Test that we can parse LLM-style JSON responses."""

    def test_parse_clean_json(self):
        raw = '{"channels":[{"salience":0.9,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.4,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.8,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.5,"tolerance":0.5},{"salience":0.9,"tolerance":0.5}]}'
        import re
        json_str = re.sub(r"```json?\n?", "", raw).replace("```", "").strip()
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed["channels"]), 9)
        self.assertAlmostEqual(parsed["channels"][0]["salience"], 0.9)

    def test_parse_markdown_json(self):
        raw = '```json\n{"channels":[{"salience":0.9,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.4,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.8,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.5,"tolerance":0.5},{"salience":0.9,"tolerance":0.5}]}\n```'
        import re
        json_str = re.sub(r"```json?\n?", "", raw).replace("```", "").strip()
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed["channels"]), 9)

    def test_parse_with_surrounding_text(self):
        raw = 'Here is the analysis:\n\n{"channels":[{"salience":0.9,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.4,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.8,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.5,"tolerance":0.5},{"salience":0.9,"tolerance":0.5}]}\n\nThe stakes are high.'
        import re
        # Extract JSON object from surrounding text
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        parsed = json.loads(match.group())
        self.assertEqual(len(parsed["channels"]), 9)


class TestEncoderFactory(unittest.TestCase):
    """Test factory functions."""

    def test_deepinfra_factory(self):
        enc = create_deepinfra_encoder("test-key")
        self.assertEqual(enc.endpoint, "https://api.deepinfra.com/v1/openai")
        self.assertEqual(enc.model, "ByteDance/Seed-2.0-mini")
        self.assertEqual(enc.api_key, "test-key")

    def test_custom_model(self):
        enc = create_deepinfra_encoder("test-key", model="custom-model")
        self.assertEqual(enc.model, "custom-model")


if __name__ == "__main__":
    unittest.main()
