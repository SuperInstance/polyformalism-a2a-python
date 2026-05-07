"""
Tests for intent-directed compilation.
"""

import pytest
from polyformalism_a2a.channels import Channel, IntentProfile
from polyformalism_a2a.intent_compile import (
    classify_precision,
    batch_classify,
    check_with_precision,
    Precision,
)


def _profile_with_stakes(stakes: float) -> IntentProfile:
    p = IntentProfile()
    p.set_channel(Channel.STAKES, stakes)
    return p


class TestClassifyFromStakes:
    """Four threshold cases."""

    def test_int8(self):
        assert classify_precision(_profile_with_stakes(0.1)) == Precision.INT8

    def test_int16(self):
        assert classify_precision(_profile_with_stakes(0.35)) == Precision.INT16

    def test_int32(self):
        assert classify_precision(_profile_with_stakes(0.6)) == Precision.INT32

    def test_dual(self):
        assert classify_precision(_profile_with_stakes(0.9)) == Precision.DUAL


class TestBatchClassify:
    """Mixed-precision batch with AV-like profile spread."""

    def test_av_mix(self):
        pairs = [
            ({"lower": 0.0, "upper": 1.0, "value": 0.5}, _profile_with_stakes(0.1)),   # INT8
            ({"lower": 0.0, "upper": 1.0, "value": 0.5}, _profile_with_stakes(0.35)),  # INT16
            ({"lower": 0.0, "upper": 1.0, "value": 0.5}, _profile_with_stakes(0.6)),   # INT32
            ({"lower": 0.0, "upper": 1.0, "value": 0.5}, _profile_with_stakes(0.9)),   # DUAL
            ({"lower": 0.2, "upper": 0.8, "value": 0.5}, _profile_with_stakes(0.15)),  # INT8
            ({"lower": 0.0, "upper": 0.3, "value": 0.5}, _profile_with_stakes(0.8)),   # DUAL, mismatch
        ]
        results, stats = batch_classify(pairs)

        assert stats.total == 6
        assert stats.counts[Precision.INT8] == 2
        assert stats.counts[Precision.INT16] == 1
        assert stats.counts[Precision.INT32] == 1
        assert stats.counts[Precision.DUAL] == 2
        assert stats.throughput_projection > 0
        # Last pair should be a mismatch
        assert results[-1].mismatches == 1
        assert not results[-1].passed


class TestDifferentialZeroMismatches:
    """All in-range values pass verification."""

    def test_in_range(self):
        assert check_with_precision(0.5, 0.0, 1.0, Precision.INT8)
        assert check_with_precision(0.5, 0.0, 1.0, Precision.INT16)
        assert check_with_precision(0.5, 0.0, 1.0, Precision.INT32)
        assert check_with_precision(0.5, 0.0, 1.0, Precision.DUAL)

    def test_boundary_values(self):
        assert check_with_precision(0.0, 0.0, 1.0, Precision.INT8)
        assert check_with_precision(1.0, 0.0, 1.0, Precision.INT8)

    def test_out_of_range(self):
        assert not check_with_precision(1.5, 0.0, 1.0, Precision.INT8)
        assert not check_with_precision(-0.1, 0.0, 1.0, Precision.DUAL)
