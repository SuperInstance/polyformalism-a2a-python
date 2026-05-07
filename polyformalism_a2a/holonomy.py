"""
GL(9) Zero Holonomy Consensus (Python port).

Measures whether a cycle of intent transforms returns to identity.
If it does (zero holonomy), the communication loop is aligned.
If it doesn't, something drifted — misalignment detected.

Ported from the Rust implementation in holonomy-consensus/src/zhc_gl9.rs
"""

import math
from typing import List, Optional, Tuple
from .channels import Channel, IntentProfile


def _identity_9x9() -> List[List[float]]:
    """Create a 9x9 identity matrix."""
    m = [[0.0] * 9 for _ in range(9)]
    for i in range(9):
        m[i][i] = 1.0
    return m


def _mat_mul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    """Multiply two 9x9 matrices."""
    result = [[0.0] * 9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            for k in range(9):
                result[i][j] += a[i][k] * b[k][j]
    return result


def _mat_sub(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    """Subtract two 9x9 matrices."""
    return [[a[i][j] - b[i][j] for j in range(9)] for i in range(9)]


def _frobenius_norm(m: List[List[float]]) -> float:
    """Frobenius norm of a matrix."""
    return math.sqrt(sum(m[i][j] ** 2 for i in range(9) for j in range(9)))


def _plane_rotation(dim_a: int, dim_b: int, angle: float) -> List[List[float]]:
    """
    Create a 9x9 plane rotation matrix in the (dim_a, dim_b) plane.

    This generalizes SO(3) axis-angle rotations to GL(9):
    rotate in any pair of the 9 intent dimensions.
    """
    m = _identity_9x9()
    m[dim_a][dim_a] = math.cos(angle)
    m[dim_a][dim_b] = -math.sin(angle)
    m[dim_b][dim_a] = math.sin(angle)
    m[dim_b][dim_b] = math.cos(angle)
    return m


class GL9Holonomy:
    """
    GL(9) holonomy consensus tracker.

    Accumulates transforms around communication cycles.
    If the accumulated transform deviates from identity,
    the communication loop has drift — misalignment.
    """

    def __init__(self, tolerance: float = 0.5):
        """
        Args:
            tolerance: Maximum acceptable holonomy deviation (default 0.5 = Oracle1's ZHC)
        """
        self.tolerance = tolerance
        self.accumulated = _identity_9x9()
        self.transforms: List[List[List[float]]] = []

    def add_transform(self, transform: List[List[float]]):
        """Add a transform to the cycle."""
        self.transforms.append(transform)
        self.accumulated = _mat_mul(self.accumulated, transform)

    def add_rotation(self, dim_a: int, dim_b: int, angle: float):
        """Add a plane rotation in the (dim_a, dim_b) plane."""
        rot = _plane_rotation(dim_a, dim_b, angle)
        self.add_transform(rot)

    def reset(self):
        """Reset the cycle."""
        self.accumulated = _identity_9x9()
        self.transforms = []

    @property
    def deviation(self) -> float:
        """Frobenius distance from accumulated transform to identity."""
        diff = _mat_sub(self.accumulated, _identity_9x9())
        return _frobenius_norm(diff)

    @property
    def is_aligned(self) -> bool:
        """Whether the cycle has zero holonomy (within tolerance)."""
        return self.deviation <= self.tolerance

    @property
    def n_transforms(self) -> int:
        return len(self.transforms)


def holonomy_deviation(
    profiles: List[IntentProfile],
    tolerance: float = 0.5,
) -> dict:
    """
    Compute holonomy deviation for a cycle of intent transforms.

    Each profile-to-profile transition is modeled as a transform
    that aligns the sender's intent with the receiver's interpretation.

    Args:
        profiles: Ordered list of intent profiles in the communication cycle
        tolerance: Maximum acceptable deviation

    Returns:
        Dict with holonomy analysis
    """
    if len(profiles) < 2:
        return {
            "deviation": 0.0,
            "is_aligned": True,
            "n_hops": 0,
            "status": "TRIVIAL",
        }

    h = GL9Holonomy(tolerance=tolerance)

    # Each hop: rotate from sender's dominant channel toward receiver's
    for i in range(len(profiles)):
        sender = profiles[i]
        receiver = profiles[(i + 1) % len(profiles)]

        s_dom = sender.dominant_channel().value - 1  # 0-indexed
        r_dom = receiver.dominant_channel().value - 1

        # Angle based on cosine similarity
        cos_sim = sender.cosine_similarity(receiver)
        angle = math.acos(max(-1.0, min(1.0, cos_sim)))

        h.add_rotation(s_dom, r_dom, angle)

    return {
        "deviation": h.deviation,
        "is_aligned": h.is_aligned,
        "n_hops": h.n_transforms,
        "tolerance": tolerance,
        "status": "ALIGNED" if h.is_aligned else "DRIFT_DETECTED",
    }
