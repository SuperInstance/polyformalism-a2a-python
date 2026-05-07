"""
LLM-based encoder for polyformalism-a2a.

Replaces heuristic keyword matching with model-driven intent extraction.
Uses any OpenAI-compatible API (DeepInfra, DeepSeek, etc.)
"""

import json
import re
from typing import Optional

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

from .channels import IntentProfile

SYSTEM_PROMPT = """You are a communication intent analyzer. Given a message, extract its 9-channel intent profile.

The 9 channels are:
C1 Boundary: "What are we talking about?" — Topic scope, domain boundaries
C2 Pattern: "How do pieces connect?" — Structural/logical relationships
C3 Process: "What's happening over time?" — Temporal dynamics, state changes
C4 Knowledge: "How sure am I?" — Confidence, certainty, evidence level
C5 Social: "Who cares and why?" — Social dynamics, stakeholders
C6 Deep Structure: "What's really being said?" — Hidden intent, subtext, implications
C7 Instrument: "What tools are available?" — Medium, format, channel constraints
C8 Paradigm: "What model of thought?" — Reasoning framework, worldview
C9 Stakes: "What matters vs what doesn't?" — Priority, urgency, consequences

For each channel, provide:
1. A salience value [0.0, 1.0] — how important is this channel for this message
2. A tolerance value [0.01, 1.0] — how much deviation is acceptable

Respond in EXACTLY this JSON format, nothing else:
{"channels":[{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5},{"salience":0.0,"tolerance":0.5}]}"""


class LLMEncoder:
    """Encode natural language into 9-channel IntentVectors using an LLM."""

    def __init__(self, endpoint: str, api_key: str, model: str):
        """
        Args:
            endpoint: OpenAI-compatible chat completions endpoint
            api_key: API key for the endpoint
            model: Model ID (e.g. "ByteDance/Seed-2.0-mini")
        """
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model

    def encode(
        self,
        message: str,
        context: Optional[str] = None,
        temperature: float = 0.3,
    ) -> IntentProfile:
        """Encode a message into a 9-channel IntentProfile via LLM.

        Args:
            message: The message to encode
            context: Additional context about the communication
            temperature: LLM temperature (low for consistency)

        Returns:
            IntentProfile with 9-channel salience + tolerance
        """
        user_content = f"Context: {context}\n\nMessage: {message}" if context else f"Message: {message}"

        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": 500,
            "temperature": temperature,
        }).encode()

        req = urllib.request.Request(
            f"{self.endpoint}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        content = data["choices"][0]["message"]["content"]

        # Parse JSON from response (handle markdown code blocks)
        json_str = re.sub(r"```json?\n?", "", content).replace("```", "").strip()
        parsed = json.loads(json_str)

        vector = IntentProfile()
        for i in range(min(9, len(parsed["channels"]))):
            vector.values[i] = max(0.0, min(1.0, parsed["channels"][i]["salience"]))
            vector.tolerance[i] = max(0.01, parsed["channels"][i]["tolerance"])

        return vector

    def encode_batch(self, messages, context=None, temperature=0.3):
        """Encode multiple messages sequentially."""
        return [self.encode(m, context=context, temperature=temperature) for m in messages]


def create_deepinfra_encoder(api_key: str, model: str = "ByteDance/Seed-2.0-mini"):
    """Convenience factory for DeepInfra endpoint."""
    return LLMEncoder(
        endpoint="https://api.deepinfra.com/v1/openai",
        api_key=api_key,
        model=model,
    )
