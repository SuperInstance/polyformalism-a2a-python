"""
9-channel intent encoding.

The 9 communication channels are anchor points on a continuous intent curve.
The curve between them cannot be described in language — only traversed.
"""

from enum import IntEnum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


class Channel(IntEnum):
    """The 9 communication channels — Pythagorean anchor points in the ether."""
    BOUNDARY = 1       # C1: What are we talking about?
    PATTERN = 2        # C2: How do pieces connect?
    PROCESS = 3        # C3: What's happening over time?
    KNOWLEDGE = 4      # C4: How sure am I?
    SOCIAL = 5         # C5: Who cares and why?
    DEEP_STRUCTURE = 6 # C6: What's really being said?
    INSTRUMENT = 7     # C7: What tools are available?
    PARADIGM = 8       # C8: What model of thought?
    STAKES = 9         # C9: What matters vs what doesn't?

    @property
    def label(self) -> str:
        labels = {
            1: "Boundary", 2: "Pattern", 3: "Process", 4: "Knowledge",
            5: "Social", 6: "Deep Structure", 7: "Instrument",
            8: "Paradigm", 9: "Stakes",
        }
        return labels[self.value]

    @property
    def question(self) -> str:
        questions = {
            1: "What are we talking about?",
            2: "How do pieces connect?",
            3: "What's happening over time?",
            4: "How sure am I?",
            5: "Who cares and why?",
            6: "What's really being said?",
            7: "What tools are available?",
            8: "What model of thought?",
            9: "What matters vs what doesn't?",
        }
        return questions[self.value]


INTENT_CHANNELS = list(Channel)


@dataclass
class IntentProfile:
    """
    A 9-dimensional intent vector.

    Each dimension is a float in [0, 1] representing the salience of that channel.
    The profile is an anchor on the intent curve — the curve between profiles
    is continuous and undescribable in language.

    Attributes:
        values: Dict mapping Channel -> float salience [0, 1]
        tolerance: Per-channel tolerance (how much deviation is acceptable)
        anchors: Which channels are explicitly set (vs inferred)
    """
    values: Dict[Channel, float] = field(default_factory=dict)
    tolerance: Dict[Channel, float] = field(default_factory=dict)
    anchors: set = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        # Fill missing channels with 0.0
        for ch in Channel:
            if ch not in self.values:
                self.values[ch] = 0.0
            if ch not in self.tolerance:
                self.tolerance[ch] = 0.5  # Default ZHC tolerance

    def set_channel(self, channel: Channel, value: float, tolerance: float = 0.5):
        """Set a channel value and mark it as an explicit anchor."""
        self.values[channel] = max(0.0, min(1.0, value))
        self.tolerance[channel] = tolerance
        self.anchors.add(channel)

    def vector(self) -> List[float]:
        """Return the 9D intent vector as a list."""
        return [self.values[Channel(i)] for i in range(1, 10)]

    def cosine_similarity(self, other: "IntentProfile") -> float:
        """Cosine similarity between two intent vectors."""
        a = self.vector()
        b = other.vector()
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def euclidean_distance(self, other: "IntentProfile") -> float:
        """Euclidean distance between two intent vectors."""
        return math.sqrt(sum(
            (self.values[Channel(i)] - other.values[Channel(i)]) ** 2
            for i in range(1, 10)
        ))

    def flavor(self, top_n: int = 3) -> List[Tuple[Channel, float]]:
        """Return the top-N most salient channels (the 'flavor profile')."""
        sorted_channels = sorted(
            self.values.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_channels[:top_n]

    def dominant_channel(self) -> Channel:
        """Return the most salient channel."""
        return max(self.values.items(), key=lambda x: x[1])[0]

    def draft(self) -> float:
        """
        Calculate the 'draft' — how deep this intent's requirements are.

        Higher draft = more shared context needed for safe communication.
        Uses the tolerance-weighted salience as draft proxy.
        """
        total = sum(
            self.values[ch] / max(self.tolerance[ch], 0.01)
            for ch in Channel
        ) / 9.0
        # Normalize: max possible draft with all values=1.0 and min tolerance
        # is ~100, but practical range is 0-2. Clamp to [0, 2].
        return min(2.0, total / 10.0)

    def rigidity(self) -> float:
        """
        Check rigidity via Laman's theorem: 2V - 3 constraints for V vertices.

        9 channels need 15 constraints for full rigidity.
        Each explicitly anchored channel provides ~1.7 constraints (9*1.7 ≈ 15).
        """
        n_anchors = len(self.anchors)
        if n_anchors < 2:
            return 0.0
        # Laman: 2V-3 constraints needed, each anchor provides edges
        constraints_needed = 2 * 9 - 3  # = 15
        constraints_have = n_anchors * (n_anchors - 1) // 2
        return min(1.0, constraints_have / constraints_needed)

    def is_rigid(self) -> bool:
        """Whether the intent profile is geometrically rigid (won't wobble)."""
        return self.rigidity() >= 0.8

    def to_dict(self) -> Dict:
        """Serialize to dict."""
        return {
            "values": {ch.value: v for ch, v in self.values.items()},
            "tolerance": {ch.value: t for ch, t in self.tolerance.items()},
            "anchors": [ch.value for ch in self.anchors],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "IntentProfile":
        """Deserialize from dict."""
        profile = cls()
        for k, v in d.get("values", {}).items():
            profile.values[Channel(int(k))] = v
        for k, t in d.get("tolerance", {}).items():
            profile.tolerance[Channel(int(k))] = t
        for a in d.get("anchors", []):
            profile.anchors.add(Channel(int(a)))
        profile.metadata = d.get("metadata", {})
        return profile

    def __repr__(self) -> str:
        top = self.flavor(3)
        top_str = ", ".join(f"C{ch.value}({ch.label})={v:.2f}" for ch, v in top)
        return f"IntentProfile(draft={self.draft():.2f}, flavor=[{top_str}])"
