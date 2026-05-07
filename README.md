# polyformalism-a2a

**Think like a polyglot, not a compiler.**

A 9-channel intent encoding framework for agent-to-agent communication. Based on the insight that bilingual people don't translate word-by-word — they understand intent in one language and express it in another. This library formalizes that process.

## The 9 Channels

| Channel | Name | Question |
|---------|------|----------|
| C1 | Boundary | What are we talking about? |
| C2 | Pattern | How do pieces connect? |
| C3 | Process | What's happening over time? |
| C4 | Knowledge | How sure am I? |
| C5 | Social | Who cares and why? |
| C6 | Deep Structure | What's really being said? |
| C7 | Instrument | What tools are available? |
| C8 | Paradigm | What model of thought? |
| C9 | Stakes | What matters vs what doesn't? |

## Quick Start

```python
from polyformalism_a2a import IntentProfile, encode, decode, translate

# Encode intent in 9 channels
profile = encode("We need to deploy by Friday or we lose the contract")
print(profile.flavor())  # dominant channels

# Translate intent to a different paradigm
pyramid_intent = translate(profile, target="pyramid")
navajo_intent = translate(profile, target="navajo")

# Check alignment between two profiles
similarity = profile.align(other_profile)
print(f"Alignment: {similarity:.2f}")
```

## LLM Encoder

Replace heuristic keyword matching with model-driven intent extraction. Works with any OpenAI-compatible API (DeepInfra, DeepSeek, etc.):

```python
from polyformalism_a2a.llm_encode import create_deepinfra_encoder

encoder = create_deepinfra_encoder(api_key="your-key")
profile = encoder.encode("The submarine hull pressure is approaching critical")
print(profile.flavor())  # Stakes-dominant, high C9

# Batch encoding
profiles = encoder.encode_batch(["message 1", "message 2", "message 3"])
```

The LLM encoder extracts salience and tolerance for all 9 channels in a single structured query, returning an `IntentProfile` compatible with the rest of the library.

## Fleet-Constraint Bridge

Connects intent profiles to constraint compilation via the **SoA mixed-precision pipeline**:

```python
from polyformalism_a2a.fleet_bridge import FluxLucidBridge, classify_precision

bridge = FluxLucidBridge()

# Sensor constraints: (value, lower, upper, stakes, name)
constraints = [
    (45.2, 0.0, 300.0, 0.9, "depth_sensor"),    # → DUAL (life-critical)
    (12.3, -2.0, 35.0, 0.05, "water_temp"),      # → INT8 (informational)
    (101.3, 95.0, 110.0, 0.95, "pressure_hull"),  # → DUAL (life-critical)
]

# Classify precision and build SoA batch
batch = bridge.classify_and_emit(constraints)
results = bridge.check_with_dual_verification(batch)

print(results["stats"]["memory_reduction"])  # e.g. 0.58 (58% memory savings)
```

### Precision Classification

Stakes (C9) drives the precision class:

| C9 Stakes | Precision | Constraints/Register | Use Case |
|-----------|-----------|---------------------|----------|
| < 0.25 | INT8 | 64 | Informational |
| 0.25–0.50 | INT16 | 32 | Operational |
| 0.50–0.75 | INT32 | 16 | Safety-critical |
| > 0.75 | DUAL | 16 (dual-path) | Life-critical |

DUAL constraints use **XOR dual-path verification** — comparison AND subtraction-based checks must agree, catching silicon-level errors.

### Intent-Directed Compilation

```python
from polyformalism_a2a.intent_compile import classify_precision, batch_classify

# Classify from an IntentProfile
precision = classify_precision(profile)  # INT8, INT16, INT32, or DUAL

# Batch classify constraints
results, stats = batch_classify([
    ({"lower": 0, "upper": 100, "value": 50}, high_stakes_profile),
    ({"lower": -10, "upper": 10, "value": 3}, low_stakes_profile),
])
print(stats.throughput_projection)  # weighted throughput vs all-DUAL
```

## Navigation Metaphors

This library implements five key principles from nautical navigation:

1. **Splines in the Ether** — The 9 channels are anchor points. The intent between them is continuous and irreducible.
2. **Fair Curve First** — Sight the intent first, find measurements second.
3. **Where the Rocks Aren't** — Negative knowledge (absence of danger) is primary.
4. **Draft Determines Truth** — The same message is safe or deadly depending on the receiver.
5. **The Physical World Solved This** — Survive by navigating, not by approximating truth.

## Installation

```bash
pip install polyformalism-a2a
```

## License

Apache-2.0
