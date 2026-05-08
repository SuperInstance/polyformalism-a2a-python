# polyformalism-a2a

If you used the Rust crate and want to try it in Python — this is that. Same 9-channel intent vectors, same alignment checking, same precision classification. Plus an LLM encoder and a fleet-constraint bridge that wires intent profiles to the SoA mixed-precision pipeline.

```bash
pip install polyformalism-a2a
```

---

## The 9 channels

Every agent gets a profile across nine channels. This isn't arbitrary — it's the same model the Rust crate uses, derived from polyglot cognition research. Bilingual people don't translate word-by-word. They understand intent in one language and express it in another. This library formalizes that process.

| Channel | Name | What it captures |
|---------|------|-----------------|
| C1 | Boundary | Scope — what are we talking about |
| C2 | Pattern | How pieces connect |
| C3 | Process | What's happening over time |
| C4 | Knowledge | Confidence level |
| C5 | Social | Who cares and why |
| C6 | Deep Structure | What's really being said |
| C7 | Instrument | Available tools |
| C8 | Paradigm | Model of thought |
| C9 | Stakes | What matters vs. what doesn't |

---

## Quick start

```python
from polyformalism_a2a import IntentProfile, encode, decode, translate

# Encode a message into 9-channel profile
profile = encode("We need to deploy by Friday or we lose the contract")
print(profile.flavor())  # dominant channels

# Check alignment with another profile
similarity = profile.align(other_profile)
print(f"Alignment: {similarity:.2f}")
```

---

## LLM encoder

Replace heuristic keyword matching with model-driven intent extraction. Works with any OpenAI-compatible API — DeepInfra, DeepSeek, OpenAI, whatever you've got.

```python
from polyformalism_a2a.llm_encode import create_deepinfra_encoder

encoder = create_deepinfra_encoder(api_key="your-key")
profile = encoder.encode("The submarine hull pressure is approaching critical")
print(profile.flavor())  # Stakes-dominant, high C9

# Batch encoding
profiles = encoder.encode_batch(["message 1", "message 2", "message 3"])
```

One structured query extracts salience and tolerance for all nine channels.

---

## Fleet-constraint bridge

Connects intent profiles to constraint compilation. Sensor constraints get classified by stakes into precision tiers, then batched into struct-of-arrays for the SoA mixed-precision pipeline:

```python
from polyformalism_a2a.fleet_bridge import FluxLucidBridge

bridge = FluxLucidBridge()

constraints = [
    (45.2, 0.0, 300.0, 0.9, "depth_sensor"),      # DUAL — life-critical
    (12.3, -2.0, 35.0, 0.05, "water_temp"),         # INT8 — informational
    (101.3, 95.0, 110.0, 0.95, "pressure_hull"),    # DUAL — life-critical
]

batch = bridge.classify_and_emit(constraints)
results = bridge.check_with_dual_verification(batch)
print(results["stats"]["memory_reduction"])  # e.g. 0.58
```

### Precision tiers

C9 (Stakes) drives precision — same logic as the Rust crate:

| C9 Stakes | Precision | Use case |
|-----------|-----------|----------|
| < 0.25 | INT8 | Informational |
| 0.25–0.50 | INT16 | Operational |
| 0.50–0.75 | INT32 | Safety-critical |
| > 0.75 | DUAL | Life-critical |

DUAL constraints run XOR dual-path verification — two independent checks must agree, catching silicon-level errors.

---

## Intent-directed compilation

```python
from polyformalism_a2a.intent_compile import classify_precision, batch_classify

# Classify from an IntentProfile
precision = classify_precision(profile)

# Batch classify
results, stats = batch_classify([
    ({"lower": 0, "upper": 100, "value": 50}, high_stakes_profile),
    ({"lower": -10, "upper": 10, "value": 3}, low_stakes_profile),
])
print(stats.throughput_projection)
```

---

## Installation

```bash
pip install polyformalism-a2a
```

Requires Python 3.8+.

## License

Apache-2.0
