"""Tests for DivergenceAwareTolerance."""
import pytest
from polyformalism_a2a.divergence_tolerance import (
    DivergenceAwareTolerance, DriftTrend, PrecisionClass,
)


def test_no_drift_no_change():
    dat = DivergenceAwareTolerance()
    assert dat.effective_tolerances() == [0.5] * 9


def test_increasing_drift_tightens():
    dat = DivergenceAwareTolerance()
    dat.adjust(8, 0.7, DriftTrend.INCREASING)
    dat.adjust(8, 0.8, DriftTrend.INCREASING)
    assert dat.effective_tolerance(8) < 0.5


def test_decay_restores_tolerance():
    dat = DivergenceAwareTolerance(decay_rate=0.5)
    dat.adjust(2, 0.8, DriftTrend.INCREASING)
    tightened = dat.effective_tolerance(2)
    for _ in range(10):
        dat.decay()
    after = dat.effective_tolerance(2)
    assert after > tightened
    assert abs(after - 0.5) < 0.01


def test_precision_class_selection():
    dat = DivergenceAwareTolerance()
    assert dat.precision_classes()[8] == PrecisionClass.INT8
    dat.adjust(8, 0.9, DriftTrend.INCREASING)
    dat.adjust(8, 0.9, DriftTrend.INCREASING)
    assert dat.precision_classes()[8] == PrecisionClass.DUAL


def test_max_tightening_respected():
    dat = DivergenceAwareTolerance(max_tightening=0.5)
    for _ in range(100):
        dat.adjust(0, 1.0, DriftTrend.INCREASING)
    assert dat.effective_tolerance(0) >= 0.25


def test_multiple_channels_independent():
    dat = DivergenceAwareTolerance()
    dat.adjust(8, 0.8, DriftTrend.INCREASING)
    assert dat.precision_classes()[0] == PrecisionClass.INT8
    assert dat.precision_classes()[8] == PrecisionClass.DUAL


def test_checkpoint_restore():
    dat = DivergenceAwareTolerance()
    dat.adjust(3, 0.6, DriftTrend.STABLE)
    dat.adjust(7, 0.4, DriftTrend.DECREASING)
    cp = dat.to_dict()
    restored = DivergenceAwareTolerance.from_dict(cp)
    assert restored.effective_tolerances() == dat.effective_tolerances()


def test_reset_clears():
    dat = DivergenceAwareTolerance()
    dat.adjust(0, 0.9, DriftTrend.INCREASING)
    dat.reset()
    assert dat.effective_tolerances() == [0.5] * 9


def test_invalid_channel_ignored():
    dat = DivergenceAwareTolerance()
    dat.adjust(-1, 0.5, DriftTrend.INCREASING)
    dat.adjust(9, 0.5, DriftTrend.INCREASING)
    assert dat.effective_tolerances() == [0.5] * 9
