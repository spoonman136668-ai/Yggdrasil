TITLE: DG-1A-CLR3-H191-P0 — Shared Low-Rank Sleep Latent Surrogate Mechanical Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE IMPLEMENTATION PILOT / NOT H191 PRIMARY
TRACK: DG-1 / CAPABILITY HIBERNATION / SHARED LOW-RANK RESIDUAL STATE
BRANCH: dg1a-ar
PARENT_EXPERIMENT: dg1a-clr3-h191-shared-low-rank-sleep-latent-audit.ice

PURPOSE

The accepted H190 transient parent harness and primary matrices are no longer available.
H191 therefore remains provenance-blocked and MUST NOT be executed as accepted-lineage evidence
from a reconstructed parent.

H191-P0 asks a narrower implementation question:

DOES THE ALREADY-PREREGISTERED H191 GREEDY SHARED-GAUSSIAN LATENT RECRUITER
BEHAVE MECHANICALLY AS INTENDED
ON A CONTROLLED SURROGATE RESIDUAL FAMILY,
AND WHEN DOES IT BEAT A PER-CAPABILITY PROXY8 OMP CACHE?

THIS PILOT IS NON-EVIDENCE.

Its results cannot:
- pass or fail H191;
- replace H190;
- modify accepted H190/H191 provenance;
- justify a scientific closure;
- enter held-out H191 acceptance statistics.

BOUNDARY

Synthetic computational research only.
No living tissue.
No wetware.
No biological implementation claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

FIXED BODY / GEOMETRY

Use the exact declared DG-1 fine parent geometry:

integer lattice points (i,j) with i^2+j^2 <= 32^2,
normalized to (i/32,j/32).

This yields exactly:
3209 parent sites.

Parent Gaussian basis width:
sigma = 0.22.

CONTEXTS

Use the declared H183+ context geometry:

A:
center (-0.48, 0.00),
sd 0.20,
require x <= -0.05.

B:
center (+0.34, +0.34),
sd 0.20,
require x >= +0.05 and y >= +0.05.

C:
center (+0.34, -0.34),
sd 0.20,
require x >= +0.05 and y <= -0.05.

Reject points outside the unit disk.

SURROGATE WORLD FAMILY

Pilot worlds:
40.

Seeds:
20260924190000 through 20260924190039.

Per world, construct a residual teacher that is deliberately distributed but not identical
to the H191 candidate family.

1. Draw SIX shared Gaussian source factors.
   - centers drawn uniformly from the unit disk;
   - sigma drawn uniformly from [0.12, 0.42].

2. Draw one decoder coefficient per source factor and capability from N(0,1).

3. Add a SMALL capability-specific smooth residual:
   0.10 * a_T * sin(w_Tx*x + w_Ty*y + phase_T),
   with a_T drawn from [0.5,1.5],
   w_Tx,w_Ty drawn from [1.0,4.0],
   phase_T drawn from [0,2*pi).

4. Normalize each capability residual on its distillation set to unit RMS before fitting.

This gives:
shared low-rank pressure
+
a small non-Gaussian capability-specific remainder.

It is intentionally not guaranteed to be rank-4 or exactly representable by H191.

DATA

Per capability / world:

128 deterministic distillation coordinates.
512 disjoint held-out coordinates.

Coordinates use the context samplers above.

No task outputs exist in this pilot.
Only surrogate sleep-residual values are generated.

H191 LATENT RECRUITMENT

Use EXACTLY the preregistered H191 factor family and greedy rule:

- pooled 384 distillation coordinates as candidate centers;
- widths W25/W50/W75 from pooled nearest-neighbor distances;
- ridge alpha 0.001;
- greedy joint A/B/C normalized residual-MSE score;
- tie by lower pooled center index, then W25, W50, W75;
- nested LATENT2/LATENT4/LATENT8 prefixes.

PROXY8 COMPARATOR

For each capability independently:

- candidate bases are all 3209 parent Gaussian sites;
- parent sigma 0.22;
- OMP score:
  (x_j^T r)^2 / (x_j^T x_j + 0.001);
- tie lower parent-site index;
- after every selection refit all selected coefficients by ridge alpha 0.001;
- stop at 8 sites.

This mirrors the declared H190 PROXY8 mechanism on the surrogate residuals.

METRICS

Per world / capability / method:

- distillation NMSE;
- held-out NMSE.

Per world aggregate:

- mean A/B/C held-out NMSE;
- worst-capability held-out NMSE.

Across worlds report:

- median held-out NMSE per capability;
- median mean-capability NMSE;
- 90th percentile mean-capability NMSE;
- fraction of worlds with all A/B/C held-out NMSE <=0.01;
- fraction with all <=0.02;
- LATENT4 minus PROXY8 paired world delta;
- LATENT8 minus PROXY8 paired world delta;
- selected factor widths and center spread;
- decoder concentration by capability.

MECHANICAL PILOT CHECKS

This pilot is mechanically encouraging if:

1. LATENT4 median mean-capability held-out NMSE < PROXY8.
2. LATENT4 is not worse than PROXY8 by >0.005 in any capability median.
3. LATENT8 improves on LATENT4, showing rank nesting works.
4. Distillation-to-held-out gap does not indicate gross recruitment overfit.
5. Re-running identical seeds produces byte-identical serialized result rows.

These are pilot diagnostics only.
They are NOT H191 acceptance gates.

NO POST-RUN TUNING

After the first pilot world executes, do not change:

- surrogate generator;
- world count;
- context geometry;
- distillation / held-out counts;
- H191 recruitment;
- PROXY8 recruitment;
- ridge;
- rank set;
- pilot diagnostics.

PROVENANCE

evidence_class =
NON_EVIDENCE_SURROGATE_MECHANICAL_AUDIT

h191_primary_status =
NOT_STARTED_PROVENANCE_BLOCKED

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P0 SURROGATE MECHANICAL HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P0 SURROGATE WORLD.

HARNESS

Repository path:

research/experiments/dg1a/adaptive/harnesses/h191_p0_surrogate_mechanical_v1.py

Harness commit:

bcbc7969148f73fc0895a7e59cdcc48561119213

Git blob SHA:

6ac31f5cc3e091be7ef24ea74879903dd21cc2fa

Exact UTF-8 source byte length:

11507.

Exact source SHA-256:

da6643d35ae6bd5256d400d219702e37ed379ac867ea81583acd2986fa45eabb.

RNG

NumPy Generator
with:
PCG64(world_seed).

Source-factor parameter draws occur before:
context-coordinate sampling.

Each context draws:
640 accepted coordinates
in one deterministic rejection stream,
then splits:
first 128 distillation,
remaining 512 held-out.

SERIALIZATION

Canonical compact JSON:
sort_keys=true,
separators=(",",":"),
UTF-8,
one trailing newline.

The output file SHA-256 is recorded by the harness.

REPRODUCIBILITY CHECK

The complete frozen 40-world run
must be executed twice.

Both canonical output files
must have:
identical SHA-256.

If not:
the pilot is mechanically invalid.

NO POST-RUN CHANGE

No source edit,
seed edit,
generator edit,
candidate edit,
metric edit,
or:
diagnostic edit
is permitted
after:
the first world executes.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL H191-P0 NON-EVIDENCE PILOT CLOSURE — SHARED LATENT MECHANICAL AUDIT

DATE:
2026-09-20.

STATUS:
COMPLETE / NEGATIVE FOR THE PREREGISTERED NEAREST-NEIGHBOR WIDTH RULE /
DETERMINISM PASS / NON-EVIDENCE.

FROZEN HARNESS SHA-256

da6643d35ae6bd5256d400d219702e37ed379ac867ea81583acd2986fa45eabb.

FROZEN HARNESS COMMIT

bcbc7969148f73fc0895a7e59cdcc48561119213.

PILOT WORLD FAMILY

20260924190000..20260924190039.

40 surrogate worlds.

3 capability contexts / world.

Two complete executions were performed without source change.

RUN 1 OUTPUT SHA-256

bfb7778f25c253abdabb470c2454bb05b73640c2c8139196683ea5129cbf19ea.

RUN 2 OUTPUT SHA-256

bfb7778f25c253abdabb470c2454bb05b73640c2c8139196683ea5129cbf19ea.

Byte comparison:
identical.

DETERMINISM:
PASS.

HELD-OUT NMSE — MEDIANS

PROXY8:

A:
0.04065404099868991.

B:
0.017314566748504692.

C:
0.01779141097040926.

Median mean-capability held-out NMSE:
0.03570859490398067.

P90 mean-capability held-out NMSE:
0.11323014820456453.

LATENT2:

A:
2.7503293815554395.

B:
2.167666184383136.

C:
2.2420071047157424.

Median mean-capability:
3.2773268373072106.

LATENT4:

A:
2.7503293815554404.

B:
2.167666184383136.

C:
2.2420071047157424.

Median mean-capability:
2.9057337043260665.

P90:
6.55248985720454.

LATENT8:

A:
2.4200203544544294.

B:
1.7932009726446183.

C:
1.98334575072763.

Median mean-capability:
2.3923482796274635.

P90:
5.626829042884027.

PAIRED VALUE VERSUS PROXY8

LATENT4 minus PROXY8
median world mean-capability NMSE:

+2.882927390052756.

LATENT4 win rate:

0%.

LATENT8 minus PROXY8
median:

+2.369541965354152.

LATENT8 win rate:

0%.

THRESHOLD TELEMETRY

All A/B/C <=0.01:

PROXY8:
0%.

LATENT2:
0%.

LATENT4:
0%.

LATENT8:
0%.

All A/B/C <=0.02:

PROXY8:
5%.

LATENT2:
0%.

LATENT4:
0%.

LATENT8:
0%.

WIDTH DIAGNOSTIC

Median frozen width candidates across worlds:

W25 nearest-neighbor:
approximately 0.01723.

W50:
approximately 0.02765.

W75:
approximately 0.04246.

Selected LATENT4 factor widths:

median:
approximately 0.04246.

range:
approximately 0.02882..0.04565.

LATENT4 selections:

159 / 160

used:
the widest W75 slot.

Thus:

the recruiter itself
systematically asks for:
the broadest factor available,

but:

the broadest factor
is still:
only:
approximately 0.04
in normalized input coordinates.

For reference:

the accepted parent RBF width
is:
0.22.

The H191 preregistered
nearest-neighbor width rule

therefore:
constructs:
virtual factors
roughly:
five times narrower

than:
the parent local basis scale.

CAPABILITY LOCALIZATION DIAGNOSTIC

LATENT4 selected factor-center origins
across the 40 worlds:

A-context:
57.

B-context:
52.

C-context:
51.

This is:
balanced spatial recruitment.

However:

median LATENT4
decoder concentration:

0.9999995325750876.

A value near 1
means:
each selected factor
effectively serves:
one capability only.

Therefore:

the factors are:
nominally shared
in parameter structure

but:
functionally:
capability-local islands.

They are NOT:
operating as:
a cross-capability shared latent.

GENERALIZATION

Median distillation-to-held-out
mean NMSE gap:

PROXY8:
approximately 0.01614.

LATENT4:
approximately 0.14663.

LATENT8:
approximately 0.29685.

Thus:

adding more:
very narrow latent factors

improves:
distillation fit

but:
increases:
the held-out generalization gap.

MECHANICAL PILOT GATE REVIEW

1.
LATENT4 median mean held-out NMSE < PROXY8:

FAIL.

2.
LATENT4 no capability median worse than PROXY8 by >0.005:

FAIL strongly.

3.
LATENT8 improves on LATENT4:

PASS mechanically,
but remains grossly inferior to PROXY8.

4.
No gross distillation-to-held-out overfit:

FAIL.

5.
Byte-identical repeat:

PASS.

FINAL TECHNICAL INTERPRETATION

H191-P0 is:
NEGATIVE.

It does NOT:
fail the accepted H191 hypothesis,
because:
this pilot is explicitly:
NON-EVIDENCE
and:
the accepted H190 parent was not used.

It DOES:
falsify:
the mechanical suitability
of:
H191's original
nearest-neighbor-derived
Gaussian width rule.

The width generator
was measuring:
sample spacing,

not:
cross-context residual scale.

As a result:

the shared latent
degenerates into:
several tiny:
capability-local kernels.

Rank expansion
then:
adds more local islands

instead of:
discovering:
shared residual structure.

PRE-PRIMARY DESIGN CONSEQUENCE

H191 accepted-lineage primary
has NOT started.

Therefore:
a documented pre-primary
factor-width correction
is justified
before:
any accepted-lineage execution.

The correction must:

- remain geometry/model-scale derived;
- not use task targets;
- not use held-out H191 outcomes;
- preserve:
  ranks 2/4/8;
- preserve:
  6 learned scalars / factor;
- preserve:
  the greedy joint recruitment rule;
- preserve:
  LATENT4 equal-memory accounting.

PLAIN-SPEAK SUMMARY

What did we try?

We tested the exact planned H191 shared-latent selection machinery
on a separate synthetic residual problem,
without pretending it was the real H191 experiment.

What happened?

The sparse PROXY8 method worked reasonably well.
The planned shared latent failed badly.

Why?

The supposed shared factors were much too narrow.
The algorithm chose the widest factor almost every time,
but that width was still only about 0.04,
while Yggdrasil's parent basis width is 0.22.

So instead of one factor helping A, B, and C,
each factor mostly helped only one capability.

Did it work?

No.

The original width rule is mechanically unsuitable.

What did we learn?

The low-rank idea itself has not been disproved.
The problem is earlier:
the candidate latent geometry prevents sharing from happening.

Why does this matter?

A shared sleep core only helps Yggdrasil
if the same small state actually carries information across capabilities.
A set of tiny capability-local factors is just another sparse cache
with worse behavior.

What should we try next?

Correct the pre-primary width rule
so candidate factors exist at:
the parent functional scale
and:
broader cross-context scales,
then repeat the mechanical audit
on disjoint surrogate worlds.

H191 primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
