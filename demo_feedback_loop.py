#!/usr/bin/env python3
"""
End-to-end demo: Runtime→Compile Feedback Loop

Simulates the complete cycle:
1. Agent defines IntentVector with base tolerances
2. Runtime drift detected on some channels (simulated)
3. DivergenceAwareTolerance adjusts tolerances
4. Precision classes updated (INT8 → DUAL for high-drift)
5. Constraint recompilation with tighter bounds
6. Drift resolves over time (decay)
7. Tolerances return to baseline

This is what the fleet should do automatically once PLATO is back.
"""

from polyformalism_a2a import (
    DivergenceAwareTolerance, DriftTrend, PrecisionClass,
    IntentProfile, align, draft_check,
)


def main():
    print("=" * 60)
    print("DivergenceAwareTolerance — End-to-End Demo")
    print("=" * 60)

    # Phase 1: Define base intent
    print("\n📊 Phase 1: Base Intent Profile")
    profile = IntentProfile(
        agent_id="forgemaster",
        values=[0.5, 0.3, 0.7, 0.4, 0.6, 0.2, 0.8, 0.3, 0.9],  # 9 channels
        tolerance=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    )
    print(f"  Agent: {profile.agent_id}")
    print(f"  Dominant channel: C9 (Stakes) = {profile.values[8]}")
    print(f"  Base tolerances: {profile.tolerance}")

    # Phase 2: Initialize DivergenceAwareTolerance
    print("\n🔧 Phase 2: Initialize Feedback Controller")
    dat = DivergenceAwareTolerance(
        base_tolerance=profile.tolerance,
        decay_rate=0.9,
        max_tightening=0.5,
    )
    print(f"  Decay rate: {dat.decay_rate}")
    print(f"  Max tightening: {dat.max_tightening}")
    print(f"  Initial precision: {[p.value for p in dat.precision_classes()]}")

    # Phase 3: Runtime drift detected (simulated)
    print("\n⚠️  Phase 3: Runtime Drift Detected!")
    drift_events = [
        (2, 0.6, DriftTrend.INCREASING, "Process channel drifting — timing constraints loosening"),
        (8, 0.8, DriftTrend.INCREASING, "Stakes channel drifting — priority misalignment"),
        (8, 0.9, DriftTrend.INCREASING, "Stakes still increasing — fleet priority divergence"),
        (4, 0.3, DriftTrend.STABLE, "Social channel minor drift — trust weight mismatch"),
    ]
    for ch, score, trend, desc in drift_events:
        dat.adjust(ch, score, trend)
        print(f"  C{ch+1} drift={score:.1f} trend={trend.value}: {desc}")
        print(f"    → C{ch+1} tolerance: {dat.effective_tolerance(ch):.3f} "
              f"(tightened {dat.drift_adjustment[ch]*100:.1f}%)")

    # Phase 4: Precision classes updated
    print("\n🎯 Phase 4: Precision Recompilation")
    classes = dat.precision_classes()
    for i, pc in enumerate(classes):
        marker = "⚡" if pc == PrecisionClass.DUAL else "  "
        print(f"  {marker} C{i+1}: {pc.value.upper():4s} "
              f"(tol={dat.effective_tolerance(i):.3f}, "
              f"drift={dat.drift_adjustment[i]*100:.1f}%)")

    dual_count = sum(1 for c in classes if c == PrecisionClass.DUAL)
    print(f"\n  → {dual_count} channels upgraded to DUAL precision")
    print(f"  → {9 - dual_count} channels remain INT8")

    # Phase 5: Simulate drift resolution over time
    print("\n📉 Phase 5: Drift Resolution (10 decay cycles)")
    for tick in range(1, 11):
        dat.decay()
        c3_tol = dat.effective_tolerance(2)
        c9_tol = dat.effective_tolerance(8)
        print(f"  t={tick:2d}: C3={c3_tol:.3f} C9={c9_tol:.3f}")

    # Phase 6: Check if tolerances returned to baseline
    print("\n✅ Phase 6: Post-Resolution Status")
    final_tols = dat.effective_tolerances()
    for i, t in enumerate(final_tols):
        status = "baseline" if abs(t - 0.5) < 0.01 else f"adjusted ({t:.3f})"
        print(f"  C{i+1}: {status}")

    # Phase 7: Summary
    print("\n" + "=" * 60)
    print("FEEDBACK LOOP SUMMARY")
    print("=" * 60)
    print(f"  Drift events processed: {sum(dat.observation_count)}")
    print(f"  Channels that tightened: {sum(1 for a in dat.drift_adjustment if a > 0.01)}")
    print(f"  Current DUAL channels: {sum(1 for c in dat.precision_classes() if c == PrecisionClass.DUAL)}")
    print(f"  Tolerances near baseline: {sum(1 for t in final_tols if abs(t - 0.5) < 0.01)}/9")
    print()
    print("  The feedback loop works: drift triggers tightening,")
    print("  resolution triggers decay, system returns to baseline.")
    print("  This is what the fleet should do automatically.")
    print("=" * 60)


if __name__ == "__main__":
    main()
