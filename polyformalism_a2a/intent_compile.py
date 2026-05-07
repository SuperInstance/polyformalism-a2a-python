"""
Intent-directed compilation: classify precision from C9 (Stakes) channel.

Mixed-precision pipeline — use the stakes to decide how many bits
the constraint solver needs before it can sign off.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

from .channels import Channel, IntentProfile


class Precision(Enum):
    """Precision levels for intent-directed compilation."""
    INT8 = "INT8"
    INT16 = "INT16"
    INT32 = "INT32"
    DUAL = "DUAL"


@dataclass
class ClassificationStats:
    """Summary stats from a batch classification run."""
    counts: Dict[Precision, int] = field(default_factory=lambda: {p: 0 for p in Precision})
    total: int = 0
    throughput_projection: float = 0.0

    # Throughput multipliers relative to DUAL=1.0
    _THROUGHPUT = {
        Precision.INT8: 8.0,
        Precision.INT16: 4.0,
        Precision.INT32: 2.0,
        Precision.DUAL: 1.0,
    }

    def recalc(self):
        self.total = sum(self.counts.values())
        if self.total == 0:
            self.throughput_projection = 0.0
            return
        weighted = sum(
            self.counts[p] * self._THROUGHPUT[p] for p in Precision
        )
        self.throughput_projection = weighted / self.total


@dataclass
class IntentCompileResult:
    """Result from intent-directed compilation."""
    precision: Precision
    stakes: float
    passed: bool = True
    mismatches: int = 0


# --- Classification thresholds on C9 (Stakes) ---

def classify_precision(profile: IntentProfile) -> Precision:
    """
    Classify the precision level from an IntentProfile's C9 (Stakes) channel.

    C9 < 0.25 → INT8
    C9 0.25–0.5 → INT16
    C9 0.5–0.75 → INT32
    C9 > 0.75 → DUAL
    """
    stakes = profile.values.get(Channel.STAKES, 0.0)
    if stakes < 0.25:
        return Precision.INT8
    elif stakes < 0.5:
        return Precision.INT16
    elif stakes < 0.75:
        return Precision.INT32
    else:
        return Precision.DUAL


def batch_classify(
    pairs: List[Tuple],
) -> Tuple[Dict, ClassificationStats]:
    """
    Batch-classify a list of (constraint_dict, profile) pairs.

    Each constraint_dict has 'lower', 'upper', 'value' keys.
    Returns (results_list, stats).
    """
    stats = ClassificationStats()
    results = []

    for constraint, profile in pairs:
        precision = classify_precision(profile)
        stats.counts[precision] += 1

        lower = constraint.get("lower", 0.0)
        upper = constraint.get("upper", 1.0)
        value = constraint.get("value", 0.5)

        # Differential verification: check value is in [lower, upper]
        passed = lower <= value <= upper
        mismatches = 0 if passed else 1

        results.append(IntentCompileResult(
            precision=precision,
            stakes=profile.values.get(Channel.STAKES, 0.0),
            passed=passed,
            mismatches=mismatches,
        ))

    stats.recalc()
    return results, stats


def check_with_precision(
    value: float, lower: float, upper: float, precision: Precision
) -> bool:
    """
    Differential verification with precision-appropriate epsilon.
    """
    epsilons = {
        Precision.INT8: 1e-2,
        Precision.INT16: 1e-4,
        Precision.INT32: 1e-7,
        Precision.DUAL: 1e-12,
    }
    eps = epsilons[precision]
    return (lower - eps) <= value <= (upper + eps)
