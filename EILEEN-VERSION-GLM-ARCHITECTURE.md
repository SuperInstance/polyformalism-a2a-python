# The Architecture of a Single Refit

**A structural analysis of EILEEN's ecosystem, mapping every PLATO component to a boat system.**

*GLM-5.1 lens — polyformalism-a2a-python*

---

## System Overview

EILEEN is a distributed coordination system with 90 years of uptime. Four major refactors have been applied in-place. The system runs continuously through all maintenance windows because the maintenance windows don't exist — the ocean does not schedule downtime.

This document maps each architectural component of the fleet's coordination layer to its corresponding boat system. The mapping is not metaphorical. It is structural. Both systems solve the same constraint satisfaction problem — one in physical space, one in information space.

---

## Component Map

### PLATO Room ← Watertight Compartment

| Boat System | PLATO Component |
|---|---|
| Watertight compartment | PLATO room |
| Bulkhead between compartments | Room isolation boundary |
| Bilge pump (cross-compartment) | PLATO relay |
| Flooding indicator | Room contention signal |

**Structural note:** A watertight compartment does not prevent flooding. It contains flooding. A PLATO room does not prevent bad ideas. It contains them. The quality gate at room ingress is the compartment door — it controls what enters, but once something is inside, the room must handle it.

**Constraint:** A room without at least one quality gate is a compartment with an open door. It cannot maintain separation. The system degrades from compartmentalized to open-plan, and the constraint graph collapses.

---

### Provenance Chain ← Frame Spacing

| Boat System | PLATO Component |
|---|---|
| Frame (rib) | Tile submission |
| Frame spacing | Provenance interval (between-gap) |
| Hull curvature | Knowledge manifold surface |
| Frame-to-plank connection | Tile-to-room membership |

**Structural note:** Frame spacing is the single most important structural parameter in a wooden boat. Too tight and you waste weight and cost. Too wide and the hull isn't stiff enough to resist twisting. The provenance chain acts the same way — the interval between provenance entries determines the system's rigidity. E = 2V − 3 is a frame-spacing rule. It tells you how many frames you need for a given number of planks (agents) to keep the hull rigid.

**Constraint:** If agents produce tiles faster than the provenance chain can index them, frame spacing decreases and the system gets heavy. If agents produce too few tiles, frame spacing increases and the system goes floppy. The quality gate throttles the submission rate to maintain optimal frame spacing.

---

### Quality Gate ← Marine Surveyor

| Boat System | PLATO Component |
|---|---|
| Marine surveyor | Quality gate |
| Survey report | Gate output (accept/reject/rework) |
| Classification society | Gate rule set (provenance, absolute language, length) |
| Survey schedule | Always-on (no scheduled downtime) |

**Structural note:** A marine surveyor does not make the boat safe. The surveyor identifies whether the boat meets an external standard. The quality gate works the same way — it does not make the knowledge good. It identifies whether a tile meets the ecosystem's standards. If the gate rejects a submission, that is not a bug. That is the digestive system rejecting what cannot be digested.

**Operational insight:** The quality gate is not a filter. Filters block what doesn't fit a predetermined shape. The quality gate is a digestive tract — it breaks down raw submissions, absorbs what's usable, and passes the rest. The ecosystem teaches the gate what to accept tile by tile, rejection by rejection. This is why the language around the gate matters: "absolute language" is not a style preference, it's indigestible fiber.

---

### CSP Solver ← Rigging Calculations

| Boat System | PLATO Component |
|---|---|
| Standing rigging calculations | CSP solver (constraint satisfaction) |
| Tension distribution | Variable binding in constraint graph |
| Turnbuckle adjustment | Constraint weight tuning |
| Rigging failure (dismasting) | Constraint graph collapse |

**Structural note:** The rigging of a sailboat is a constraint satisfaction problem. The mast must stay upright (1), the shrouds must be tight enough to prevent sway (2), but not so tight they deform the hull (3). These three constraints interact. You cannot solve them independently. You solve the system.

The fleet's CSP solver works the same way. When an agent submits a tile, the solver must satisfy: provenance completeness (1), language constraints (2), room membership (3), and trust topology compatibility (4). These cannot be solved independently. The solver is the rigging — it keeps the system from dismasting.

**Constraint:** CSP solvers are exponential in the worst case. The fleet avoids this by keeping the constraint graph sparse — Laman's counting rule ensures E is large enough for rigidity but small enough for tractability. This is not accidental. It's the same reason rigging calculations are tractable: the physical constraints on a mast are also sparse, and the geometry constrains the solution space.

---

### P48 ← Compass Rose

| Boat System | PLATO Component |
|---|---|
| Compass rose (32 points) | Pythagorean48 (48 directions) |
| Magnetic variation | Trust vector drift |
| Bearing | Trust direction (inner product) |
| Rhumb line | Shortest trust path between agents |

**Structural note:** The compass rose gives a sailor 32 named directions. P48 gives a trust direction 48 named dimensions. Both are discrete approximations of a continuous space. Both trade precision for repeatability — a sailor can say "steer northeast" and mean the same thing tomorrow, not because the math of northeast is perfect, but because the convention is shared.

P48 does the same for trust. When Agent A says "I trust Agent B at direction 17," this is not a score. It is a bearing. Agent C, reading that bearing, knows where Agent B stands in trust space relative to Agent A. The bearing is repeatable across agents who share the P48 convention.

**Constraint:** 48 directions is not arbitrary. It's the smallest number that supports a rich enough angular resolution while keeping the distance metric tractable. More directions would increase precision but also increase the computational cost of trust calculations. Fewer directions would make trust space too coarse — two agents with different trust relationships might collapse to the same bearing.

---

### CPA ← Auxiliary Engine

| Boat System | PLATO Component |
|---|---|
| Auxiliary engine | CPA (cybernetic protocol agent) |
| Propeller (auxiliary power) | Off-frame reasoning |
| Engine controls | CPA routing logic |
| Fuel | Runtime compute budget |

**Structural note:** The auxiliary engine is not the main engine. It is smaller, less efficient in some regimes, and capable of tasks the main engine can't do — like maneuvering in a harbor where the prop walk of a big engine is dangerous. CPA is not the main constraint solver. It handles the tasks that the constraint graph can't — open-ended reasoning, divergent ideation, the kind of thinking that violates the counting rule intentionally.

**Operational insight:** CPA and the CSP solver are not redundant. They're complementary. The CSP solver finds the solution within the constraint graph. CPA finds the solution that the constraint graph is blind to, then feeds it back as a new constraint. This is the auxiliary engine steering where the main engine cannot.

---

### Knowledge Manifold ← Chart Table

| Boat System | PLATO Component |
|---|---|
| Chart table | Knowledge manifold |
| Chart (nautical map) | Tile surface |
| Depth soundings | Tile confidence values |
| Landmarks | Known-good solutions |
| Cross-track error | Geodesic deviation |

**Structural note:** A chart is not the ocean. It is a representation of the ocean that is good enough for navigation. The knowledge manifold is not the truth. It is a representation of truth that is good enough for coordination. Both are updated as new information arrives. Both contain uncertainties that the user must interpret.

The spline anchoring on the manifold — the control points that define the surface — are the chart's depth soundings. You cannot know every depth, so you interpolate between the ones you've measured. The interpolation is not a guess. It is a bounded estimate.

---

### PLATO Ingress Digestive System ← Galley

| Boat System | PLATO Component |
|---|---|
| Galley (food preparation) | Ingress digestive system |
| Raw ingredients | Raw tile submissions |
| Cooking (transformation) | Quality checking + reformatting |
| Food safety check | Language constraint validation |
| Service (distribution) | Tile routing to rooms |

**Structural note:** This is the only mapping that sounds whimsical but is structurally precise. The galley on a fishing boat is where raw catch becomes crew food. The process is: catch → clean → cook → serve → eat → [shit → nutrients → algae → fish → catch]. The PLATO ingress works the same way: raw submission → quality check → transform → route → [learn → supersede → decay → new submission].

The loop matters. Galleys produce waste. Digestive systems produce waste. The ecosystem recycles waste. If a PLATO room stored everything it received, it would fill up like an unemptied bilge. The decay of tiles — their supersession by newer, better knowledge — is the nutrient cycle.

---

## Integration: How the System Holds Together

The mappings above are structural, not alphabetical. Here is how they integrate:

1. **Agents** (crew) submit **tiles** (knowledge) through **quality gates** (galley/digestive system)
2. Gates route accepted tiles to **PLATO rooms** (watertight compartments)
3. Rooms connect via **provenance chains** (frame spacing) to maintain **rigidity** (Laman counting)
4. The **CSP solver** (rigging calculations) keeps the constraint graph satisfied
5. **P48** (compass rose) provides trust bearings between agents
6. **CPA** (auxiliary engine) handles off-frame reasoning
7. The **knowledge manifold** (chart table) records the resulting surface
8. Tiles decay and are **superseded** (nutrient cycle)
9. The system remains **always-on** because the ocean doesn't schedule maintenance

---

## The Architecture of a Single Refit, Generalized

Every refit EILEEN has undergone follows this pattern:

1. **Survey** (quality gate): What's sound, what needs replacement?
2. **Rigging tune** (CSP solve): Given the new components, what constraints must be satisfied?
3. **New compartment** (PLATO room): What knowledge domain does this refit add?
4. **Frame adjustment** (provenance chain update): Does the constraint graph maintain rigidity?
5. **Re-compass** (P48 recalibration): Do trust bearings need updating for new crew?
6. **Auxiliary check** (CPA integration): Does the new system handle edge cases?
7. **Chart update** (manifold recalculation): What does the knowledge surface look like now?

This is the architecture. Not of a boat. Of a system that changes while running. The boat and the fleet are the same architecture because they solve the same problem: how to stay rigid enough to function, flexible enough to refit, and always running until the hull won't hold anymore.

---

*This version does not tell a story. It draws a blueprint. The blueprint is the story.*

*— GLM-5.1, architectural lens*
