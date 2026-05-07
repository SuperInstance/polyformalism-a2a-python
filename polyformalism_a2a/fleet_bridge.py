"""
flux-lucid → fleet-constraint bridge.

Connects Forgemaster's SoA mixed-precision emitter to Oracle1's GuardRuntime.
IntentVector profiles drive constraint classification → GuardRuntime executes them.

Data flow:
    PLATO tile → IntentVector → classify_precision → SoAConstraintBatch
                                                           ↓
    GuardRuntime.evaluate_batch() → AVX-512 VPCMPD → ConstraintResults
                                                           ↓
    SafetyWatcher.monitor() → violations → KeeperBridge → PLATO
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
import math


# ============================================================================
# Precision Classification (mirrors Rust beam_tolerance module)
# ============================================================================

class PrecisionClass(Enum):
    INT8 = "INT8"      # 64 per AVX-512 register — informational
    INT16 = "INT16"    # 32 per register — operational
    INT32 = "INT32"    # 16 per register — safety-critical
    DUAL = "DUAL"      # 16 per register, dual path — life-critical


def classify_precision(stakes: float, value_range: float) -> PrecisionClass:
    """
    Classify constraint into precision class based on C9 stakes and value range.
    
    Rules:
    - stakes > 0.75 → DUAL (life-critical, dual-path verification)
    - stakes > 0.5 or range > 32000 → INT32 (safety-critical)
    - stakes > 0.25 or range > 127 → INT16 (operational)
    - otherwise → INT8 (informational)
    """
    if stakes > 0.75:
        return PrecisionClass.DUAL
    if stakes > 0.5 or value_range > 32000:
        return PrecisionClass.INT32
    if stakes > 0.25 or value_range > 127:
        return PrecisionClass.INT16
    return PrecisionClass.INT8


# ============================================================================
# Beam Material (mirrors Rust BeamMaterial)
# ============================================================================

@dataclass
class BeamMaterial:
    """Material properties for beam-intent equivalence."""
    name: str
    youngs_modulus: float  # GPa
    density: float         # g/cm³
    yield_strength: float  # MPa

    @staticmethod
    def steel() -> 'BeamMaterial':
        return BeamMaterial("Steel", 200.0, 7.8, 600.0)

    @staticmethod
    def fiberglass() -> 'BeamMaterial':
        return BeamMaterial("Fiberglass", 30.0, 2.0, 200.0)

    @staticmethod
    def oak() -> 'BeamMaterial':
        return BeamMaterial("Oak", 12.0, 0.7, 80.0)

    @staticmethod
    def cedar() -> 'BeamMaterial':
        return BeamMaterial("Cedar", 6.0, 0.4, 40.0)

    @staticmethod
    def rubber() -> 'BeamMaterial':
        return BeamMaterial("Rubber", 0.01, 1.1, 10.0)

    def max_tolerance(self, safety_factor: float = 1.0) -> float:
        """Maximum tolerance derived from beam deflection."""
        normalized = self.youngs_modulus / 200.0
        tol = 0.01 + (1.0 - normalized) * 0.99
        return min(max(tol / safety_factor, 0.01), 1.0)


def stakes_to_material(stakes: float) -> BeamMaterial:
    """Map C9 stakes to beam material."""
    if stakes > 0.75:
        return BeamMaterial.steel()
    if stakes > 0.5:
        return BeamMaterial.fiberglass()
    if stakes > 0.25:
        return BeamMaterial.oak()
    if stakes > 0.1:
        return BeamMaterial.cedar()
    return BeamMaterial.rubber()


# ============================================================================
# SoA Constraint Batch
# ============================================================================

@dataclass
class SoAConstraint:
    """A single constraint in the SoA batch."""
    value: float
    lower: float
    upper: float
    stakes: float
    precision: PrecisionClass
    name: str = ""


@dataclass
class SoABatch:
    """SoA (struct-of-arrays) constraint batch sorted by precision class."""
    int8_values: List[int] = field(default_factory=list)
    int8_lowers: List[int] = field(default_factory=list)
    int8_uppers: List[int] = field(default_factory=list)
    int8_names: List[str] = field(default_factory=list)
    
    int16_values: List[int] = field(default_factory=list)
    int16_lowers: List[int] = field(default_factory=list)
    int16_uppers: List[int] = field(default_factory=list)
    int16_names: List[str] = field(default_factory=list)
    
    int32_values: List[int] = field(default_factory=list)
    int32_lowers: List[int] = field(default_factory=list)
    int32_uppers: List[int] = field(default_factory=list)
    int32_names: List[str] = field(default_factory=list)
    
    dual_values: List[int] = field(default_factory=list)
    dual_lowers: List[int] = field(default_factory=list)
    dual_uppers: List[int] = field(default_factory=list)
    dual_names: List[str] = field(default_factory=list)

    @staticmethod
    def from_constraints(constraints: List[Tuple[float, float, float, float, str]]) -> 'SoABatch':
        """
        Create SoA batch from constraint tuples: (value, lower, upper, stakes, name).
        Each constraint is classified into its precision class and stored contiguously.
        """
        batch = SoABatch()
        for value, lower, upper, stakes, name in constraints:
            rng = abs(upper - lower)
            prec = classify_precision(stakes, rng)
            
            if prec == PrecisionClass.INT8:
                batch.int8_values.append(int(value))
                batch.int8_lowers.append(int(lower))
                batch.int8_uppers.append(int(upper))
                batch.int8_names.append(name)
            elif prec == PrecisionClass.INT16:
                batch.int16_values.append(int(value))
                batch.int16_lowers.append(int(lower))
                batch.int16_uppers.append(int(upper))
                batch.int16_names.append(name)
            elif prec == PrecisionClass.INT32:
                batch.int32_values.append(int(value))
                batch.int32_lowers.append(int(lower))
                batch.int32_uppers.append(int(upper))
                batch.int32_names.append(name)
            else:  # DUAL
                batch.dual_values.append(int(value))
                batch.dual_lowers.append(int(lower))
                batch.dual_uppers.append(int(upper))
                batch.dual_names.append(name)
        
        return batch

    def check_all(self) -> Dict[str, bool]:
        """Check all constraints at native precision (scalar fallback)."""
        results = {}
        
        for i, name in enumerate(self.int8_names):
            v, lo, hi = self.int8_values[i], self.int8_lowers[i], self.int8_uppers[i]
            results[name] = lo <= v <= hi
        
        for i, name in enumerate(self.int16_names):
            v, lo, hi = self.int16_values[i], self.int16_lowers[i], self.int16_uppers[i]
            results[name] = lo <= v <= hi
        
        for i, name in enumerate(self.int32_names):
            v, lo, hi = self.int32_values[i], self.int32_lowers[i], self.int32_uppers[i]
            results[name] = lo <= v <= hi
        
        for i, name in enumerate(self.dual_names):
            v, lo, hi = self.dual_values[i], self.dual_lowers[i], self.dual_uppers[i]
            # Path A: comparison
            pass_a = lo <= v <= hi
            # Path B: subtraction (different execution path)
            above_lo = v - lo
            below_hi = hi - v
            pass_b = above_lo >= 0 and below_hi >= 0
            # Both paths must agree
            results[name] = pass_a and pass_b
        
        return results

    def memory_stats(self) -> Dict:
        """Compute memory usage statistics."""
        n8, n16, n32, nd = (len(self.int8_values), len(self.int16_values),
                           len(self.int32_values), len(self.dual_values))
        total = n8 + n16 + n32 + nd
        
        actual_bits = n8 * 8 * 3 + n16 * 16 * 3 + n32 * 32 * 3 + nd * 64 * 3
        baseline_bits = total * 32 * 3
        
        return {
            "total_constraints": total,
            "int8_count": n8, "int16_count": n16,
            "int32_count": n32, "dual_count": nd,
            "actual_bits": actual_bits,
            "baseline_bits": baseline_bits,
            "memory_reduction": 1.0 - (actual_bits / baseline_bits) if baseline_bits > 0 else 0.0,
        }


# ============================================================================
# Bridge to fleet-constraint GuardRuntime
# ============================================================================

@dataclass
class DualDisagreement:
    """A dual-path disagreement — both paths must agree for safety."""
    name: str
    value: float
    path_a_result: bool
    path_b_result: bool


class FluxLucidBridge:
    """
    Bridge between flux-lucid SoA emitter and fleet-constraint GuardRuntime.
    
    Usage:
        bridge = FluxLucidBridge()
        
        # From PLATO tiles or sensor readings
        constraints = [
            (45.2, 0.0, 300.0, 0.9, "depth_sensor"),
            (12.3, -2.0, 35.0, 0.05, "water_temp"),
        ]
        
        batch = bridge.classify_and_emit(constraints)
        results = bridge.check_with_dual_verification(batch)
        
        if results["violations"]:
            safety_alert = watcher.monitor(results["results"], fleet_state)
    """

    def classify_and_emit(
        self,
        constraints: List[Tuple[float, float, float, float, str]],
    ) -> SoABatch:
        """Classify constraints and create SoA batch for execution."""
        return SoABatch.from_constraints(constraints)

    def check_with_dual_verification(
        self,
        batch: SoABatch,
    ) -> Dict:
        """
        Check all constraints with special dual-path verification.
        Returns results dict with violations and dual disagreements.
        """
        results = batch.check_all()
        
        # Check for dual-path disagreements
        disagreements = []
        for i, name in enumerate(batch.dual_names):
            v = batch.dual_values[i]
            lo = batch.dual_lowers[i]
            hi = batch.dual_uppers[i]
            pass_a = lo <= v <= hi
            above_lo = v - lo
            below_hi = hi - v
            pass_b = above_lo >= 0 and below_hi >= 0
            if pass_a != pass_b:
                disagreements.append(DualDisagreement(
                    name=name, value=float(v),
                    path_a_result=pass_a, path_b_result=pass_b
                ))
        
        violations = [name for name, passed in results.items() if not passed]
        
        return {
            "results": results,
            "violations": violations,
            "dual_disagreements": disagreements,
            "stats": batch.memory_stats(),
        }

    def to_guard_lines(
        self,
        constraints: List[Tuple[float, float, float, float, str]],
    ) -> List[str]:
        """
        Convert constraints to fleet-constraint GuardDSL format.
        
        GuardDSL format: name:var:op:value:priority
        We create lower and upper bound checks for each constraint.
        """
        lines = []
        for value, lower, upper, stakes, name in constraints:
            # Priority from stakes (higher stakes = higher priority)
            priority = int(stakes * 10)
            lines.append(f"{name}_lo:{name}:>={lower}:{priority}")
            lines.append(f"{name}_hi:{name}:<={upper}:{priority}")
        return lines


# ============================================================================
# Tests
# ============================================================================

if __name__ == "__main__":
    print("=== Flux-Lucid → Fleet-Constraint Bridge Test ===\n")
    
    # Simulate RARS-IMU sensor constraints
    constraints = [
        (45.2, 0.0, 300.0, 0.9, "depth_sensor"),      # DUAL
        (0.5, -30.0, 30.0, 0.7, "roll_rate"),           # INT32
        (12.3, -2.0, 35.0, 0.05, "water_temp"),         # INT8
        (180.0, 0.0, 360.0, 0.4, "heading"),            # INT16
        (101.3, 95.0, 110.0, 0.95, "pressure_hull"),    # DUAL
        (0.0, 0.0, 0.5, 0.95, "leak_detect"),           # DUAL
        (24.1, 20.0, 28.0, 0.8, "battery_voltage"),     # DUAL
        (8.5, 0.0, 15.0, 0.35, "motor_current"),        # INT16
        (50.0, 0.5, 200.0, 0.5, "sonar_range"),         # INT16
        (3.0, 0.0, 10.0, 0.2, "gps_fix"),               # INT8
    ]
    
    bridge = FluxLucidBridge()
    batch = bridge.classify_and_emit(constraints)
    results = bridge.check_with_dual_verification(batch)
    
    print(f"Classification:")
    stats = results["stats"]
    print(f"  INT8:  {stats['int8_count']} (informational)")
    print(f"  INT16: {stats['int16_count']} (operational)")
    print(f"  INT32: {stats['int32_count']} (safety)")
    print(f"  DUAL:  {stats['dual_count']} (life-critical)")
    print(f"  Memory reduction: {stats['memory_reduction']*100:.1f}%")
    
    print(f"\nConstraint check results:")
    for name, passed in results["results"].items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nViolations: {len(results['violations'])}")
    print(f"Dual disagreements: {len(results['dual_disagreements'])}")
    
    print(f"\nGuardDSL output:")
    for line in bridge.to_guard_lines(constraints)[:6]:
        print(f"  {line}")
    
    print(f"\n✅ Bridge operational — {stats['total_constraints']} constraints processed")
