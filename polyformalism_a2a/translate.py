"""
Intent translation between paradigms.

The polyglot model: understand intent in one paradigm,
express it in another. NOT word-by-word translation.
"""

from .channels import Channel, IntentProfile
from typing import Optional


# Target paradigms and their channel emphasis
_PARADIGM_PROFILES = {
    "python": {
        Channel.PATTERN: 0.9,
        Channel.INSTRUMENT: 0.85,
        Channel.PROCESS: 0.7,
        Channel.BOUNDARY: 0.6,
    },
    "rust": {
        Channel.PATTERN: 0.9,
        Channel.BOUNDARY: 0.85,
        Channel.INSTRUMENT: 0.8,
        Channel.KNOWLEDGE: 0.7,
    },
    "chinese": {
        Channel.DEEP_STRUCTURE: 0.9,
        Channel.PATTERN: 0.85,
        Channel.PROCESS: 0.7,
        Channel.SOCIAL: 0.6,
    },
    "navajo": {
        Channel.PROCESS: 0.95,
        Channel.DEEP_STRUCTURE: 0.85,
        Channel.PARADIGM: 0.8,
        Channel.BOUNDARY: 0.5,
    },
    "yoruba": {
        Channel.SOCIAL: 0.95,
        Channel.DEEP_STRUCTURE: 0.85,
        Channel.STAKES: 0.8,
        Channel.PROCESS: 0.6,
    },
    "inuktitut": {
        Channel.PROCESS: 0.9,
        Channel.KNOWLEDGE: 0.9,
        Channel.BOUNDARY: 0.7,
        Channel.STAKES: 0.85,
    },
    "asl": {
        Channel.PATTERN: 0.9,
        Channel.BOUNDARY: 0.85,
        Channel.DEEP_STRUCTURE: 0.8,
        Channel.PROCESS: 0.7,
    },
    "engineering": {
        Channel.BOUNDARY: 0.9,
        Channel.PATTERN: 0.85,
        Channel.STAKES: 0.8,
        Channel.INSTRUMENT: 0.75,
    },
    "legal": {
        Channel.BOUNDARY: 0.95,
        Channel.KNOWLEDGE: 0.9,
        Channel.SOCIAL: 0.7,
        Channel.STAKES: 0.85,
    },
    "poetry": {
        Channel.DEEP_STRUCTURE: 0.95,
        Channel.PARADIGM: 0.9,
        Channel.PROCESS: 0.6,
        Channel.STAKES: 0.2,
    },
}


def translate(
    profile: IntentProfile,
    target: str,
    fidelity: float = 0.8,
) -> IntentProfile:
    """
    Translate an intent profile to a target paradigm.

    This is NOT word-by-word translation. It's understanding the intent
    in the source paradigm and expressing it in the target's channel emphasis.

    The polyglot model:
    1. Extract the fair curve (intent shape) from source profile
    2. Find where the curve crosses the target paradigm's emphasis points
    3. Create a new profile with target-emphasized channels

    Args:
        profile: Source intent profile
        target: Target paradigm name (e.g. 'python', 'chinese', 'yoruba')
        fidelity: How much of the original profile to preserve (0.0-1.0)

    Returns:
        New IntentProfile weighted toward target paradigm
    """
    target_key = target.lower()
    if target_key not in _PARADIGM_PROFILES:
        raise ValueError(
            f"Unknown paradigm '{target}'. Available: "
            f"{list(_PARADIGM_PROFILES.keys())}"
        )

    target_emphasis = _PARADIGM_PROFILES[target_key]
    translated = IntentProfile()

    for ch in Channel:
        source_val = profile.values[ch]
        target_weight = target_emphasis.get(ch, 0.3)

        # Blend: fidelity controls how much source we keep
        blended = fidelity * source_val + (1 - fidelity) * target_weight
        blended = max(0.0, min(1.0, blended))

        # Preserve source tolerance
        tol = profile.tolerance.get(ch, 0.5)
        translated.set_channel(ch, blended, tol)

    translated.metadata["source_profile"] = profile.to_dict()
    translated.metadata["target_paradigm"] = target_key
    translated.metadata["fidelity"] = fidelity
    return translated


def list_paradigms() -> list:
    """List available target paradigms."""
    return list(_PARADIGM_PROFILES.keys())
