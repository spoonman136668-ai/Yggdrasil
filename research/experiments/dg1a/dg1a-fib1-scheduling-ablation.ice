TITLE: DG-1A-FIB1 — Fibonacci Development and Regeneration Scheduling Ablation
DATE: 2026-09-17
STATUS: PLANNED / BLOCKED UNTIL DG-1A-P0 CLOSEOUT
TRACK: DG-1A
CONFIDENCE: SPECULATIVE AS AN AI MECHANISM; ESTABLISHED ONLY THAT FIBONACCI/GOLDEN-ANGLE PATTERNS OCCUR IN SOME BIOLOGICAL DEVELOPMENTAL SYSTEMS

QUESTION
Can Fibonacci-staged developmental or repair budgets reduce overshoot, instability, or unnecessary active work relative to matched linear, geometric, and adaptive schedules under equal total resource ceilings?

MOTIVATION
Fibonacci structure appears in several phyllotactic systems, while mechanistic models indicate that such structure can arise from local placement, inhibition, transport, growth, packing, and geometric constraints rather than from an organism explicitly counting Fibonacci numbers.

This distinction is foundational for Yggdrasil.

The project must not assume that Fibonacci numbers are intrinsically intelligent or universally optimal. They are a candidate bounded schedule and geometric prior that can be falsified by matched controls.

BIOLOGICAL EVIDENCE CONTEXT
SUPPORTED:
- spiral phyllotaxis commonly exhibits parastichy counts related to consecutive Fibonacci numbers;
- the golden divergence angle near 137.5 degrees is frequently associated with Fibonacci-type phyllotaxis;
- local developmental interaction models can generate phyllotactic order;
- some work argues Fibonacci spirals need not require explicit golden-angle control.

NOT ESTABLISHED:
- that Fibonacci schedules improve neural computation;
- that golden-ratio topology is optimal for artificial neural development;
- that biological phyllotaxis implies a direct neural-growth prescription.

REFERENCE ANCHORS
- Okabe, Biophysical optimality of the golden angle in phyllotaxis, Scientific Reports 2015, PMCID: PMC4607949.
- Jonsson et al., A plausible model of phyllotaxis, PNAS 2006, PMCID: PMC1345713.
- Godin et al., Fibonacci spirals may not need the Golden Angle, Quantitative Plant Biology 2023, PMCID: PMC10095852.
- Regenerating Soft Robots through Neural Cellular Automata, arXiv:2102.02579, as general NCA regeneration context rather than Fibonacci evidence.

PRIMARY HYPOTHESIS
H-FIB1-1
Under equal maximum cumulative repair allowance, a Fibonacci-staged repair schedule can reach stable post-lesion recovery with lower cumulative repair work or lower instability than at least one simple non-adaptive schedule.
CONFIDENCE BEFORE RUN: SPECULATIVE.

SECONDARY HYPOTHESES
H-FIB1-2
A learned adaptive schedule will equal or exceed fixed Fibonacci scheduling when enough training signal exists.
CONFIDENCE BEFORE RUN: PLAUSIBLE.

H-FIB1-3
If Fibonacci-like stage ratios emerge repeatedly from a learned scheduler without being imposed, that is stronger evidence for their relevance than a hand-coded Fibonacci win.
CONFIDENCE BEFORE RUN: PLAUSIBLE AS A TEST PRINCIPLE, UNKNOWN AS AN OUTCOME.

EXPERIMENTAL BOUNDARY
DG-1A-P0 remains the canonical control and must not be altered to use Fibonacci scheduling.

FIB1 begins only after P0 reproduction/regeneration is adequately characterized.

INITIAL SCHEDULE FAMILIES
All schedules must receive matched maximum cumulative resource allowance and matched evaluation horizons.

LINEAR
1, 2, 3, 4, 5, 6, ... incremental repair/development allowance.

GEOMETRIC
1, 2, 4, 8, 16, ... with clipping to the common total ceiling.

FIBONACCI
1, 2, 3, 5, 8, 13, 21, ... with clipping to the common total ceiling.

ADAPTIVE
A learned or locally triggered controller requests the next bounded repair allocation. The controller may not exceed the same common total ceiling.

OPTIONAL CONSTANT-BUDGET CONTROL
Equal-sized repair quanta until the same cumulative ceiling is reached.

SCHEDULING SEMANTICS
A stage number is a resource allowance, not a mandatory number of live cells.

Permitted future interpretations include:
- maximum repair update steps;
- maximum cells eligible for activation/differentiation;
- maximum new connections;
- communication budget;
- module growth budget.

The first FIB1 test should use only one interpretation to avoid confounding mechanisms.

RECOMMENDED FIRST TEST
Use repair-update budget only.

For each stage:
1. begin from the same damaged phenotype;
2. permit the declared additional developmental work;
3. measure task/morphology error and resource use;
4. stop immediately if stable recovery criterion is met;
5. otherwise advance to the next schedule stage;
6. never exceed the common cumulative ceiling.

WHY THIS TEST FIRST
It does not require structural replication or graph growth, so it can reuse validated P0 regeneration machinery while isolating scheduling effects.

PRIMARY METRICS
- valid lesion effect;
- final bounded RecoveryFraction;
- stable T50 and T90;
- cumulative developmental update steps;
- wall-clock repair time;
- active-cell trajectory;
- recovery AUC;
- post-repair relapse;
- numerical instability/non-finite events.

EFFICIENCY METRIC
RepairEfficiency = stable recovered fraction / cumulative repair work.

The exact work proxy must be frozen before confirmatory FIB1 runs.

FAIRNESS RULES
- identical trained phenotype per paired schedule comparison where technically possible;
- identical damage seed and lesion geometry;
- identical total maximum repair allowance;
- identical model/genome and grid limits;
- identical stop condition;
- multiple random seeds;
- no schedule receives extra training iterations unless the training-cost difference is itself part of the declared experiment.

SUCCESS CONDITION FOR INTEREST
Fibonacci scheduling is considered worth further study only if it provides a replicated efficiency/stability advantage over matched linear or geometric controls without sacrificing final recovery.

A single win is insufficient.

DISCONFIRMING RESULT
If Fibonacci scheduling performs similarly to or worse than matched simple schedules after adequate replication, do not preserve it as a privileged Yggdrasil principle.

EMERGENCE TEST — LATER
When adaptive structural growth exists, inspect learned stage ratios and topology without a Fibonacci prior.

If ratios cluster near Fibonacci/golden-ratio structure across seeds and tasks, record the observation and test causally.
Do not infer significance from visual resemblance alone.

GOLDEN-ANGLE TOPOLOGY — LATER, SEPARATE ABLATION
Potential graph/spatial placement using approximately 137.507764 degrees is a distinct hypothesis from Fibonacci repair scheduling.
It must not be bundled into FIB1 because that would confound scheduling and topology.

DECISION
Preserve Fibonacci/golden-ratio ideas as falsifiable developmental priors, not doctrine.

Do not modify DG-1A-P0 to include them.

NEXT ACTION
Complete P0 multi-seed regeneration characterization. After P0 closeout, implement FIB1 as a matched scheduling ablation before considering golden-angle graph topology.