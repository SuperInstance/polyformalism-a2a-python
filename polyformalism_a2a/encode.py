"""
Intent encoding and decoding.

Encode natural language into 9-channel intent profiles.
Decode profiles back into structured representations.

Curve-first: the encode function sights the fair curve of intent,
then finds where it crosses the 9 channels.
"""

from .channels import Channel, IntentProfile
from typing import Optional, Dict


# Heuristic channel weights for common intent patterns
_INTENT_PATTERNS = {
    "deadline": {
        Channel.PROCESS: 0.9,
        Channel.STAKES: 0.95,
        Channel.KNOWLEDGE: 0.7,
    },
    "risk": {
        Channel.STAKES: 0.95,
        Channel.KNOWLEDGE: 0.8,
        Channel.BOUNDARY: 0.7,
    },
    "teamwork": {
        Channel.SOCIAL: 0.9,
        Channel.PROCESS: 0.7,
        Channel.PATTERN: 0.6,
    },
    "technical": {
        Channel.PATTERN: 0.9,
        Channel.INSTRUMENT: 0.85,
        Channel.KNOWLEDGE: 0.8,
    },
    "urgent": {
        Channel.STAKES: 0.95,
        Channel.PROCESS: 0.9,
        Channel.SOCIAL: 0.6,
    },
    "research": {
        Channel.PARADIGM: 0.9,
        Channel.KNOWLEDGE: 0.85,
        Channel.DEEP_STRUCTURE: 0.8,
    },
    "safety": {
        Channel.STAKES: 0.95,
        Channel.BOUNDARY: 0.9,
        Channel.KNOWLEDGE: 0.85,
    },
    "creative": {
        Channel.DEEP_STRUCTURE: 0.9,
        Channel.PARADIGM: 0.85,
        Channel.STAKES: 0.3,  # Low stakes = creative freedom
    },
}


def encode(
    text: str,
    explicit_channels: Optional[Dict[Channel, float]] = None,
    tolerance: float = 0.5,
) -> IntentProfile:
    """
    Encode natural language text into a 9-channel intent profile.

    This is a heuristic encoder. For production use, replace with
    a model-based encoder (LLM or fine-tuned classifier).

    Args:
        text: Natural language intent
        explicit_channels: Override specific channel values
        tolerance: Default tolerance for all channels

    Returns:
        IntentProfile with estimated channel saliences
    """
    text_lower = text.lower()
    profile = IntentProfile()

    # Pattern matching for heuristic channel assignment
    scores = {ch: 0.0 for ch in Channel}
    match_count = 0

    for pattern_name, channel_weights in _INTENT_PATTERNS.items():
        # Simple keyword matching
        keywords = _get_keywords(pattern_name)
        for kw in keywords:
            if kw in text_lower:
                for ch, weight in channel_weights.items():
                    scores[ch] = max(scores[ch], weight)
                match_count += 1
                break

    # If no patterns matched, distribute evenly
    if match_count == 0:
        for ch in Channel:
            scores[ch] = 0.3
        # Default: elevate BOUNDARY and STAKES
        scores[Channel.BOUNDARY] = 0.6
        scores[Channel.STAKES] = 0.5

    # Apply scores to profile
    for ch in Channel:
        profile.set_channel(ch, scores[ch], tolerance)

    # Apply explicit overrides
    if explicit_channels:
        for ch, val in explicit_channels.items():
            profile.set_channel(ch, val, tolerance)

    profile.metadata["source_text"] = text
    profile.metadata["encoding_method"] = "heuristic"
    return profile


def decode(profile: IntentProfile, format: str = "text") -> str:
    """
    Decode an intent profile into a human-readable representation.

    Args:
        profile: The intent profile to decode
        format: Output format ('text', 'json', 'channels')

    Returns:
        String representation of the decoded intent
    """
    if format == "json":
        import json
        return json.dumps(profile.to_dict(), indent=2)

    if format == "channels":
        lines = []
        for ch in Channel:
            val = profile.values[ch]
            bar = "█" * int(val * 10)
            tol = profile.tolerance[ch]
            lines.append(
                f"C{ch.value} {ch.label:15s} {bar:10s} "
                f"{val:.2f} (tol={tol:.2f})"
            )
        return "\n".join(lines)

    # Default: text summary
    top = profile.flavor(3)
    flavor_str = ", ".join(
        f"{ch.label} ({v:.2f})" for ch, v in top
    )
    draft = profile.draft()
    rigidity = profile.rigidity()

    return (
        f"Intent: draft={draft:.2f}, rigidity={rigidity:.2f}\n"
        f"Flavor: {flavor_str}\n"
        f"Dominant: {profile.dominant_channel().label}"
    )


def _get_keywords(pattern: str) -> list:
    """Get keywords for a pattern category."""
    keyword_map = {
        "deadline": ["deadline", "by friday", "urgent", "asap", "due", "hurry"],
        "risk": ["risk", "danger", "unsafe", "critical", "hazard", "failure"],
        "teamwork": ["team", "together", "collaborate", "we need", "us", "group"],
        "technical": ["code", "api", "system", "data", "algorithm", "implement"],
        "urgent": ["urgent", "emergency", "now", "immediately", "critical"],
        "research": ["research", "study", "hypothesis", "experiment", "theory"],
        "safety": ["safety", "safe", "verify", "validate", "certif", "compliance"],
        "creative": ["creative", "design", "art", "novel", "innovative", "imagine"],
    }
    return keyword_map.get(pattern, [])
