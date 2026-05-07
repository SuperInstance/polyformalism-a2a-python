"""
Divergence-aware tolerance adjustment.

Connects runtime drift detection (zeroclaw) to compile-time
constraint tolerance (IntentVector). When runtime drift
increases on a channel, tolerance tightens automatically.

Matches flux-lucid v0.1.6 (Rust) and polyformalism-a2a-js divergence-tolerance.js.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class DriftTrend(Enum):
    """Drift trend direction."""
    INCREASING = "increasing"
    STABLE = "stable"
    DECREASING = "decreasing"


class PrecisionClass(Enum):
    """Precision class for constraint checking."""
    INT8 = "int8"
    DUAL = "dual"


@dataclass
class DivergenceAwareTolerance:
    """
    Adjusts IntentVector tolerances based on runtime drift reports.
    
    The compile↔runtime feedback loop:
    1. Oracle1's zeroclaw detects drift on a channel
    2. DivergenceReport written to PLATO drift-{channel} room
    3. Forgemaster reads drift tiles, calls adjust()
    4. Effective tolerances inform precision selection
    5. Recompiled constraints deployed, drift should decrease
    """
    base_tolerance: List[float] = field(default_factory=lambda: [0.5] * 9)
    drift_adjustment: List[float] = field(default_factory=lambda: [0.0] * 9)
    decay_rate: float = 0.9
    max_tightening: float = 0.5
    observation_count: List[int] = field(default_factory=lambda: [0] * 9)

    def __post_init__(self):
        if len(self.base_tolerance) != 9:
            raise ValueError("Expected 9 tolerance values")
        self.decay_rate = max(0.0, min(self.decay_rate, 0.99))
        self.max_tightening = max(0.0, min(self.max_tightening, 0.9))

    def adjust(self, channel_idx: int, drift_score: float, trend: DriftTrend) -> None:
        """Adjust tolerance for a channel based on drift report."""
        if not 0 <= channel_idx <= 8:
            return
        tightening = {
            DriftTrend.INCREASING: drift_score * 0.3,
            DriftTrend.STABLE: drift_score * 0.1,
            DriftTrend.DECREASING: drift_score * 0.02,
        }.get(trend, 0.0)
        self.drift_adjustment[channel_idx] = min(
            self.drift_adjustment[channel_idx] + tightening,
            self.max_tightening,
        )
        self.observation_count[channel_idx] += 1

    def effective_tolerance(self, channel_idx: int) -> float:
        """Get effective tolerance for a channel."""
        if not 0 <= channel_idx <= 8:
            return self.base_tolerance[0]
        return self.base_tolerance[channel_idx] * (1.0 - self.drift_adjustment[channel_idx])

    def effective_tolerances(self) -> List[float]:
        """Get all effective tolerances."""
        return [self.effective_tolerance(i) for i in range(9)]

    def decay(self) -> None:
        """Decay all adjustments (call periodically)."""
        self.drift_adjustment = [a * self.decay_rate for a in self.drift_adjustment]

    def reset(self) -> None:
        """Reset all adjustments to zero."""
        self.drift_adjustment = [0.0] * 9
        self.observation_count = [0] * 9

    def precision_classes(self) -> List[PrecisionClass]:
        """Which precision class to use for each channel."""
        return [
            PrecisionClass.DUAL if self.drift_adjustment[i] > 0.1 else PrecisionClass.INT8
            for i in range(9)
        ]

    def to_dict(self) -> dict:
        """Serialize for checkpoint/restore."""
        return {
            "base_tolerance": self.base_tolerance[:],
            "drift_adjustment": self.drift_adjustment[:],
            "decay_rate": self.decay_rate,
            "max_tightening": self.max_tightening,
            "observation_count": self.observation_count[:],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DivergenceAwareTolerance":
        """Restore from checkpoint."""
        obj = cls(
            base_tolerance=data["base_tolerance"],
            decay_rate=data["decay_rate"],
            max_tightening=data["max_tightening"],
        )
        obj.drift_adjustment = data["drift_adjustment"]
        obj.observation_count = data["observation_count"]
        return obj
