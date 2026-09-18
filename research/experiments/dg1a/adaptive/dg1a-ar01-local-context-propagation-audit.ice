TITLE: DG-1A-AR-01 — Local Seasonal Context Propagation Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX COMMUNICATION AUDIT — NOT A YGGDRASIL SCIENTIFIC RESULT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-ar01-context-corruption-robustness-audit.ice

PURPOSE
Test whether AR-01 seasonal context could eventually be delivered through a small number of sensor cells and local communication rather than permanently broadcasting the context to every cell.

This is intentionally prior to implementation.
It measures communication timescale only.

BOUNDARY
- no Yggdrasil training;
- no STAB-18-R1 execution;
- no claim that the toy relay rule is the final architecture;
- no claim that external broadcast must be removed from AR-01;
- no new persistent Yggdrasil channel is authorized by this audit.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX
ANALYTIC where explicitly marked

LITERATURE MOTIVATION
Stovold, Neural Cellular Automata Can Respond to Signals (ALIFE 2023):
an external signal can be presented through one cell for one timestep and alter NCA behavior.

Learning spatio-temporal patterns with Neural Cellular Automata (PLOS Computational Biology, 2024):
with stochastic updates, the authors report an effective communication range of only about 8 pixels over an 8-timestep interval in one experiment, emphasizing the locality constraint.

Smart cellular bricks for decentralized shape classification and damage recovery (Nature Communications 2026):
hundreds of locally communicating modules can infer global shape;
morphogen-like information is observed propagating through the collective;
damage direction is locally inferred with high accuracy.

These establish that local signal propagation is plausible while also making propagation latency a real scaling concern.

SYNTHETIC BODY
40 x 40 lattice.

Disk-shaped live masks:
radius 6:
113 live cells

radius 10:
317 live cells

radius 14:
613 live cells

These are communication geometry toys only.

SOURCE CELLS
Environmental sensor cells are selected approximately evenly around the disk boundary.

Sensor counts tested:
1
2
4
8
16
32
64 where boundary size permits.

SEASON SWITCH
The body begins holding an old scalar context projection:
-1

Sensor cells switch to the new context:
+1

This represents the hardest antipodal CIRCLE-2 switch projected onto the new mode axis.

PASSIVE DIFFUSION BASELINE
Per NCA step:
- stochastic fire/update probability = 0.5;
- each updating non-sensor cell reads transmitting live 8-neighbors;
- neighbor messages are averaged;
- state update:
  new = 0.4 * old + 0.6 * neighbor_mean;
- sensor cells remain clamped to +1.

Communication dropout:
each live cell independently fails to transmit during the current step with the declared probability.

SUCCESS
At least 90% of live cells have:
context_projection >= 0.8

Maximum horizon:
2048 steps

Seeds:
8 per condition

PASSIVE DIFFUSION — ZERO COMMUNICATION DROPOUT

body cells | sensors | median steps to success
113        | 1       | >2048 / failed
113        | 2       | 841.5
113        | 4       | 356
113        | 8       | 172
113        | 16      | 129
113        | 32      | 116

317        | 1       | >2048 / failed
317        | 2       | >2048 / failed
317        | 4       | 1331.5
317        | 8       | 650.5
317        | 16      | 439.5
317        | 32      | 371
317        | 64      | 353

613        | 1       | >2048 / failed
613        | 2       | >2048 / failed
613        | 4       | >2048 / failed
613        | 8       | 1588
613        | 16      | 1042
613        | 32      | 794.5
613        | 64      | 729

PRIMARY NEGATIVE
Passive local averaging is far too slow for a practical organism-wide mode switch at these body sizes.

Even the canonical-size 113-cell disk requires:
172 median steps with 8 boundary sensors.

That exceeds a 96-step AR-01 lifecycle phase.

At 613 cells:
even 64 boundary sensors require:
729 median steps.

Therefore:
PASSIVE DIFFUSION IS NOT A SUFFICIENT SEASONAL CONTROL BUS.

FRESHNESS-RELAY TOY
A second synthetic mechanism tests whether locality itself is the problem or whether passive diffusion is the problem.

Each cell has:
- current context;
- one binary freshness marker for this single switch.

Old cells:
fresh = 0

new-context sensor cells:
fresh = 1

On a stochastic update:
if an old cell receives at least one transmitting fresh neighbor,
it adopts:
context = new context
fresh = 1

No global coordinator is used.

This is a wavefront relay, not diffusion.

IMPORTANT LIMITATION
The binary freshness bit solves only ONE declared transition.

It cannot safely order arbitrary repeated future switches by itself.

A real repeated-switch system would need one of:
- a bounded epoch/generation mechanism;
- a known successor relation;
- a learned temporal novelty state;
- another method that prevents stale context from overwriting newer context.

FRESHNESS RELAY RESULTS
20 seeds per condition.
Success:
90% fresh/new-context cells.

ZERO DROPOUT

body cells | sensors | median steps
113        | 1       | 11
113        | 2       | 8
113        | 4       | 6
113        | 8       | 5

317        | 1       | 18
317        | 2       | 12
317        | 4       | 9
317        | 8       | 8

613        | 1       | 26
613        | 2       | 16
613        | 4       | 12
613        | 8       | 11

50% MESSAGE DROPOUT

body cells | sensors | median steps
113        | 1       | 16.5
113        | 2       | 12
113        | 4       | 8
113        | 8       | 6

317        | 1       | 26
317        | 2       | 17
317        | 4       | 13
317        | 8       | 11

613        | 1       | 36
613        | 2       | 23.5
613        | 4       | 17
613        | 8       | 15

75% MESSAGE DROPOUT

body cells | sensors | median steps
113        | 1       | 28
113        | 4       | 14.5
113        | 8       | 11.5

317        | 1       | 45.5
317        | 4       | 22
317        | 8       | 17

613        | 1       | 59.5
613        | 4       | 28.5
613        | 8       | 24

All listed relay conditions achieved 100% success within the 256-step relay horizon.

KEY RESULT
The locality constraint is not by itself fatal.

A change-sensitive relay can cross a 613-cell disk from one boundary sensor to 90% of cells in about:
26 median steps with no communication dropout;
36 median steps with 50% dropout;
59.5 median steps with 75% dropout.

That fits within a 96-step phase.

The difference between:
passive diffusion
and
change-sensitive relay
is more than an order of magnitude in several tested conditions.

ANALYTIC HARD LIMIT — CONNECTIVITY
If local communication is the only communication path:

a disconnected live component that contains:
- no environmental sensor;
- no surviving memory of the new context;

cannot acquire the new exogenous context.

This is an information-path impossibility, not a training defect.

Therefore any future non-broadcast environmental context system must address:
- component disconnection after damage;
- sensor redundancy;
- context persistence;
or
- explicit reconnection.

ARCHITECTURAL IMPLICATION
Do not replace AR-01 global broadcast with naive diffusion.

A future decentralized seasonal-control experiment should instead test:
sensor cells
->
change/freshness-sensitive local relay
->
distributed context memory

and measure:
- switch latency;
- stale-signal overwrite;
- disconnected components;
- sensor ablation;
- message dropout;
- false relay initiation.

RELATION TO YGGDRASIL END GOAL
This is important for scale.

If every future cell must receive an instantaneous global control variable, the organism retains a hidden centralized dependency.

If a compact environmental signal can be sensed sparsely and propagated robustly through local state, the developmental organism can preserve a genuinely local execution model.

The synthetic relay result makes that route plausible but not yet learned.

DECISION
1. Keep broadcast CIRCLE-2 for first AR-01 scientific discrimination.
2. Do not burden the first AR-01 run with communication research.
3. Preserve decentralized context propagation as a separate follow-on.
4. Do not use passive diffusion as the default design.
5. Before decentralized implementation, solve repeated-switch freshness ordering explicitly.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX_AND_ANALYTIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
passive_seeds_per_condition = 8
relay_seeds_per_condition = 20
