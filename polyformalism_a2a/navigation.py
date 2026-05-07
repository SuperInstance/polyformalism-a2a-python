"""
Navigation metaphors as computational tools.

Draft determines truth. Tolerance stacks. Fairness checks.
The physical world already solved these problems.
"""

from .channels import Channel, IntentProfile
from dataclasses import dataclass
from typing import Dict, List, Optional
import math


@dataclass
class ToleranceSpec:
    """
    A tolerance specification for communication.

    Like a hydraulic fitting: right-size the tooling to the pressure.
    Hose clamp (50 PSI) for casual, JIC fitting (2500 PSI) for critical,
    deep-sea cone seal (10000 PSI) for safety-critical.
    """
    name: str
    psi_rating: int
    channel_tolerance: float
    description: str
    min_channels: int  # Minimum channels that must be anchored

    def __repr__(self):
        return f"ToleranceSpec({self.name}, {self.psi_rating} PSI, tol={self.channel_tolerance})"


# Predefined tolerance specs (hydraulic fitting metaphor)
HOSE_CLAMP = ToleranceSpec(
    name="hose_clamp", psi_rating=50, channel_tolerance=0.8,
    description="Casual communication — emoji, reactions, nods",
    min_channels=2,
)

INDUSTRIAL_FITTING = ToleranceSpec(
    name="industrial_fitting", psi_rating=300, channel_tolerance=0.5,
    description="Work communication — emails, standups, specs",
    min_channels=4,
)

JIC_FITTING = ToleranceSpec(
    name="jic_fitting", psi_rating=2500, channel_tolerance=0.2,
    description="Technical specification — API contracts, safety specs",
    min_channels=7,
)

DEEP_SEA_SEAL = ToleranceSpec(
    name="deep_sea_seal", psi_rating=10000, channel_tolerance=0.05,
    description="Safety-critical — DO-178C, ISO 26262, reactor SCRAM",
    min_channels=9,
)

FITTINGS = [HOSE_CLAMP, INDUSTRIAL_FITTING, JIC_FITTING, DEEP_SEA_SEAL]


def draft_check(
    sender: IntentProfile,
    receiver_capacity: float,
    speed_factor: float = 0.0,
) -> Dict:
    """
    Check if sender's draft fits in receiver's context depth.

    The squat effect: rushed messages have MORE draft.
    speed_factor: 0.0 = careful, 0.5 = rushed, 1.0 = emergency

    Args:
        sender: The intent being sent
        receiver_capacity: How much shared context the receiver has [0, 1]
        speed_factor: How rushed the communication is [0, 1]

    Returns:
        Dict with draft analysis
    """
    base_draft = sender.draft()
    effective_draft = base_draft * (1.0 + speed_factor)
    margin = receiver_capacity - effective_draft

    if margin > 0.2:
        status = "SAFE"
        recommendation = "Good margin. Message will land cleanly."
    elif margin > 0:
        status = "MARGINAL"
        recommendation = "Tight. Consider adding more anchors or reducing speed."
    else:
        status = "GROUNDED"
        recommendation = (
            "Will not land. Either lighten the message (reduce draft), "
            "wait for tide (build shared context), or find another channel."
        )

    return {
        "base_draft": base_draft,
        "effective_draft": effective_draft,
        "speed_factor": speed_factor,
        "receiver_capacity": receiver_capacity,
        "margin": margin,
        "status": status,
        "recommendation": recommendation,
    }


def tolerance_stack(
    tolerances: Dict[Channel, float],
) -> Dict:
    """
    Calculate the total tolerance stack across all snap steps.

    ε_total = √(ε₁² + ε₂² + ... + εₙ²)

    Each step in the communication chain adds tolerance error:
    1. Anchor → Curve (discrete to continuous)
    2. Curve → Surface (intent to meaning-in-context)
    3. Surface → Part (meaning to received-understanding)

    Args:
        tolerances: Per-channel tolerance values

    Returns:
        Dict with tolerance analysis
    """
    squares = sum(t ** 2 for t in tolerances.values())
    total = math.sqrt(squares)

    return {
        "total_tolerance": total,
        "per_channel": tolerances,
        "worst_channel": max(tolerances.items(), key=lambda x: x[1]),
        "best_channel": min(tolerances.items(), key=lambda x: x[1]),
        "is_within_spec": total < 1.0,  # Arbitrary spec: total < 1.0
    }


def fairness_check(
    profile: IntentProfile,
    threshold: float = 0.15,
) -> Dict:
    """
    Check if the intent profile is 'fair' — smooth curve, no wanderings.

    A fair curve has no unexplained wiggles. In intent profiles,
    this means no sudden jumps between adjacent channel values.

    Args:
        profile: The intent profile to check
        threshold: Maximum acceptable jump between adjacent channels

    Returns:
        Dict with fairness analysis
    """
    values = profile.vector()
    jumps = []
    for i in range(len(values) - 1):
        jump = abs(values[i] - values[i + 1])
        jumps.append({
            "from": f"C{i+1}",
            "to": f"C{i+2}",
            "jump": jump,
            "fair": jump < threshold,
        })

    max_jump = max(j["jump"] for j in jumps)
    is_fair = all(j["fair"] for j in jumps)

    return {
        "is_fair": is_fair,
        "max_jump": max_jump,
        "jumps": jumps,
        "recommendation": (
            "Curve is fair — no wanderings detected."
            if is_fair else
            f"Curve has wanderings. Max jump {max_jump:.3f} exceeds "
            f"threshold {threshold:.3f}. Consider smoothing or adding anchors."
        ),
    }


def select_fitting(stakes_level: float) -> ToleranceSpec:
    """
    Select the right hydraulic fitting for the communication pressure.

    Args:
        stakes_level: How critical is this communication? [0, 1]

    Returns:
        The appropriate ToleranceSpec
    """
    if stakes_level < 0.25:
        return HOSE_CLAMP
    elif stakes_level < 0.5:
        return INDUSTRIAL_FITTING
    elif stakes_level < 0.75:
        return JIC_FITTING
    else:
        return DEEP_SEA_SEAL
