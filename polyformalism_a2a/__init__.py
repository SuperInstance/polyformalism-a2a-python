"""
polyformalism-a2a: 9-channel polyglot communication framework.

Think like a polyglot, not a compiler.
"""

__version__ = "0.1.0"
__author__ = "SuperInstance"

from .channels import (
    Channel,
    IntentProfile,
    INTENT_CHANNELS,
)
from .encode import encode, decode
from .translate import translate
from .alignment import align, AlignmentResult
from .navigation import (
    draft_check,
    tolerance_stack,
    fairness_check,
    ToleranceSpec,
    HOSE_CLAMP,
    INDUSTRIAL_FITTING,
    JIC_FITTING,
    DEEP_SEA_SEAL,
    select_fitting,
)
from .holonomy import GL9Holonomy, holonomy_deviation

__all__ = [
    "Channel",
    "IntentProfile",
    "INTENT_CHANNELS",
    "encode",
    "decode",
    "translate",
    "align",
    "AlignmentResult",
    "draft_check",
    "tolerance_stack",
    "fairness_check",
    "ToleranceSpec",
    "GL9Holonomy",
    "holonomy_deviation",
]
