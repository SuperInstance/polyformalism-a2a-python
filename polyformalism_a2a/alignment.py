"""
Intent alignment between profiles.

Measures how well two intent profiles can communicate without grounding.
Draft determines truth: the same message is safe or deadly depending on the receiver.
"""

from .channels import Channel, IntentProfile
from dataclasses import dataclass
import math


@dataclass
class AlignmentResult:
    """Result of aligning two intent profiles."""
    cosine_similarity: float
    euclidean_distance: float
    channel_distances: dict  # Channel -> float distance per channel
    draft_compatibility: float  # Can sender's draft fit in receiver's context?
    rigidity_combined: float  # Is the combined structure rigid?
    is_safe: bool  # Within tolerance on all channels?
    warnings: list  # Channels that are dangerously misaligned

    def __repr__(self):
        status = "✓ SAFE" if self.is_safe else "✗ GROUNDED"
        return (
            f"AlignmentResult({status}, similarity={self.cosine_similarity:.3f}, "
            f"distance={self.euclidean_distance:.3f}, "
            f"draft_compat={self.draft_compatibility:.3f})"
        )


def align(
    sender: IntentProfile,
    receiver: IntentProfile,
    safety_margin: float = 0.1,
) -> AlignmentResult:
    """
    Check alignment between sender and receiver intent profiles.

    Uses the draft-tolerance equation:
    Communication Tolerance = Receiver Context - Sender Required Depth

    If CT > 0: SAFE (receiver has margin)
    If CT = 0: MARGINAL (every ambiguity is felt)
    If CT < 0: GROUNDED (receiver lacks context)
    """
    cosine = sender.cosine_similarity(receiver)
    euclidean = sender.euclidean_distance(receiver)

    # Per-channel distance
    channel_distances = {}
    warnings = []
    for ch in Channel:
        dist = abs(sender.values[ch] - receiver.values[ch])
        channel_distances[ch] = dist
        sender_tol = sender.tolerance[ch]
        if dist > sender_tol + safety_margin:
            warnings.append(
                f"C{ch.value} ({ch.label}): distance={dist:.3f} "
                f"exceeds tolerance={sender_tol:.3f}"
            )

    # Draft compatibility: can the receiver handle the sender's depth?
    sender_draft = sender.draft()
    receiver_capacity = 1.0 - receiver.draft()  # Less draft = more capacity
    draft_compatibility = receiver_capacity - sender_draft

    # Combined rigidity
    n_anchors = len(sender.anchors | receiver.anchors)
    constraints_needed = 2 * 9 - 3  # Laman: 15
    constraints_have = n_anchors * (n_anchors - 1) // 2
    rigidity_combined = min(1.0, constraints_have / constraints_needed)

    # Safety: all channels within tolerance
    is_safe = len(warnings) == 0 and draft_compatibility > 0

    return AlignmentResult(
        cosine_similarity=cosine,
        euclidean_distance=euclidean,
        channel_distances=channel_distances,
        draft_compatibility=draft_compatibility,
        rigidity_combined=rigidity_combined,
        is_safe=is_safe,
        warnings=warnings,
    )
