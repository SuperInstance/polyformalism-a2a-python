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

## Navigation Metaphors

This library implements five key principles from nautical navigation:

1. **Splines in the Ether** — The 9 channels are anchor points. The intent between them is continuous and undescribable.
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
