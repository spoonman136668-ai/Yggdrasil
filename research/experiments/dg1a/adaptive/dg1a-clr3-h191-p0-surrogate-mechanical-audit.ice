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
