"""Tests for polyformalism-a2a."""

from polyformalism_a2a import (
    Channel, IntentProfile, encode, decode, translate,
    align, draft_check, tolerance_stack, fairness_check,
    GL9Holonomy, holonomy_deviation, ToleranceSpec,
    HOSE_CLAMP, JIC_FITTING, DEEP_SEA_SEAL, select_fitting,
)


def test_channel_enum():
    assert len(Channel) == 9
    assert Channel.BOUNDARY.label == "Boundary"
    assert Channel.STAKES.question == "What matters vs what doesn't?"


def test_intent_profile():
    p = IntentProfile()
    p.set_channel(Channel.STAKES, 0.9)
    p.set_channel(Channel.PROCESS, 0.7)
    assert p.dominant_channel() == Channel.STAKES
    assert len(p.vector()) == 9
    assert p.vector()[8] == 0.9  # C9 = STAKES


def test_encode():
    p = encode("We need to deploy urgently by Friday for the safety demo")
    assert p.values[Channel.STAKES] > 0.5
    assert p.values[Channel.PROCESS] > 0.3
    assert len(p.vector()) == 9


def test_decode():
    p = encode("The system has a critical safety risk")
    text = decode(p)
    assert "draft=" in text
    json_str = decode(p, format="json")
    assert '"values"' in json_str
    channels = decode(p, format="channels")
    assert "C1" in channels


def test_cosine_similarity():
    p1 = IntentProfile()
    p1.set_channel(Channel.STAKES, 0.9)
    p1.set_channel(Channel.PROCESS, 0.8)

    p2 = IntentProfile()
    p2.set_channel(Channel.STAKES, 0.85)
    p2.set_channel(Channel.PROCESS, 0.75)

    sim = p1.cosine_similarity(p2)
    assert sim > 0.99  # Very similar


def test_translate():
    p = encode("Check the safety constraints")
    tp = translate(p, "yoruba")
    assert tp.metadata["target_paradigm"] == "yoruba"
    # Translation should produce a valid profile with 9 channels
    assert len(tp.vector()) == 9
    # Test all paradigms work
    from polyformalism_a2a.translate import list_paradigms
    assert len(list_paradigms()) >= 5
    # Low-fidelity should shift toward target emphasis
    tp_low = translate(p, "yoruba", fidelity=0.2)
    assert tp_low.values[Channel.SOCIAL] > tp.values[Channel.SOCIAL]


def test_alignment():
    sender = IntentProfile()
    sender.set_channel(Channel.STAKES, 0.9, tolerance=0.2)
    sender.set_channel(Channel.PROCESS, 0.8, tolerance=0.3)

    receiver = IntentProfile()
    receiver.set_channel(Channel.STAKES, 0.5, tolerance=0.5)

    result = align(sender, receiver)
    assert hasattr(result, "cosine_similarity")
    assert hasattr(result, "is_safe")
    assert len(result.channel_distances) == 9


def test_draft_check():
    sender = IntentProfile()
    sender.set_channel(Channel.STAKES, 0.95, tolerance=0.05)
    sender.set_channel(Channel.BOUNDARY, 0.9, tolerance=0.05)

    # Safe: high receiver capacity
    safe = draft_check(sender, receiver_capacity=0.8, speed_factor=0.0)
    assert safe["status"] == "SAFE"

    # Grounded: low capacity + rushed
    grounded = draft_check(sender, receiver_capacity=0.2, speed_factor=1.0)
    assert grounded["status"] == "GROUNDED"


def test_tolerance_stack():
    from polyformalism_a2a.channels import Channel
    tols = {Channel.STAKES: 0.1, Channel.PROCESS: 0.2, Channel.BOUNDARY: 0.15}
    result = tolerance_stack(tols)
    assert result["total_tolerance"] > 0
    assert "worst_channel" in result


def test_fairness():
    p = IntentProfile()
    for i, ch in enumerate(Channel):
        p.set_channel(ch, 0.5 + i * 0.01)  # Smooth curve

    result = fairness_check(p, threshold=0.15)
    assert result["is_fair"]


def test_holonomy():
    h = GL9Holonomy(tolerance=0.5)
    # Identity loop: 4 quarter-rotations = full circle = zero holonomy
    h.add_rotation(0, 1, math.pi / 2)
    h.add_rotation(0, 1, math.pi / 2)
    h.add_rotation(0, 1, math.pi / 2)
    h.add_rotation(0, 1, math.pi / 2)
    assert h.deviation < 0.01  # Near-zero holonomy
    assert h.is_aligned


def test_holonomy_drift():
    h = GL9Holonomy(tolerance=0.5)
    # 3 quarter-rotations ≠ full circle = nonzero holonomy
    h.add_rotation(0, 1, math.pi / 2)
    h.add_rotation(0, 1, math.pi / 2)
    h.add_rotation(0, 1, math.pi / 2)
    assert h.deviation > 0.1  # Detectable drift


def test_holonomy_deviation_profiles():
    p1 = IntentProfile()
    p1.set_channel(Channel.BOUNDARY, 0.9)
    p1.set_channel(Channel.STAKES, 0.8)

    p2 = IntentProfile()
    p2.set_channel(Channel.PROCESS, 0.9)
    p2.set_channel(Channel.PATTERN, 0.8)

    result = holonomy_deviation([p1, p2], tolerance=0.5)
    assert "deviation" in result
    assert "n_hops" in result


def test_serialization():
    p = IntentProfile()
    p.set_channel(Channel.STAKES, 0.9, tolerance=0.1)
    p.set_channel(Channel.SOCIAL, 0.7, tolerance=0.3)

    d = p.to_dict()
    p2 = IntentProfile.from_dict(d)
    assert p2.values[Channel.STAKES] == 0.9
    assert p2.tolerance[Channel.STAKES] == 0.1
    assert Channel.STAKES in p2.anchors


def test_fittings():
    from polyformalism_a2a.navigation import select_fitting
    assert select_fitting(0.1) == HOSE_CLAMP
    assert select_fitting(0.9) == DEEP_SEA_SEAL


import math

if __name__ == "__main__":
    # Run all tests
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  ✓ {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"  ✗ {test.__name__}: {e}")
    print(f"\n{passed}/{passed + failed} tests passed")
