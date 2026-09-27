TITLE: YGG-C Near-Onset Alpha Authority Reconciliation
DATE: 2026-09-27
STATUS: ACCEPTED — PROSPECTIVE BRANCH-LOCAL GOVERNANCE
LANE: YGG-C — Efficiency and Scaling

PURPOSE
Reconcile the YGG-C lane authority boundary with the already-established near-onset resource-pressure lineage without changing any scientific result, threshold, arm, model, seed, or shared accepted baseline.

BACKGROUND
The YGG-C lane charter originally stated:
- alpha remains 0.25 unless a future explicit governance decision changes it.

Subsequent preregistered YGG-C experiments established and repeatedly used a near-onset learned-control regime, including:
- C16 near-onset pressure sweep;
- the C17-C19 near-onset interaction/retention lineage;
- C20-R3 explicit runtime-alpha correction;
- descendant C22-C32 mechanism experiments.

C20/C21 defect correction specifically demonstrated that runtime alpha must be explicitly frozen to the preregistered near-onset value for that lineage. The scientific lineage therefore has a coherent alpha contract, but the lane authority document was not updated at the time.

DECISION
Effective from this governance commit forward:

1. SHARED/REFERENCE ALPHA
- alpha=0.25 remains the YGG-C shared accepted baseline/reference regime.
- this decision does not replace, mutate, or promote a new shared baseline.

2. NEAR-ONSET DESCENDANT AUTHORITY
- descendants of the established C16-C32 near-onset lineage may use alpha=0.134765625 only when that exact value is explicitly preregistered for the experiment.
- runtime parent.ALPHA and parent.g.ALPHA must both be explicitly frozen to0.134765625 during every scientific arm that claims membership in this lineage.
- required alpha allowlists/harness globals must be restored after execution.

3. NO IMPLICIT ALPHA CHANGES
- any other alpha value requires a separate preregistered experiment and, if it would become a standing lane regime, a new governance decision.
- no post-result alpha tuning is authorized.
- descendants may not silently inherit a runtime default different from their preregistration.

4. SCIENTIFIC BOUNDARIES UNCHANGED
- H/C/S/FC/FS remain protected as in the accepted baseline.
- no learned C/S authority.
- no online adaptation.
- no recursive self-modification.
- no deployment/production authority.
- no cross-lane mutation.
- no shared-baseline promotion without explicit evidence review and decision.

5. PRIOR EVIDENCE
- this decision does not rewrite prior governance history.
- C16-C32 evidence remains preserved exactly as observed, with the 2026-09-27 governance-review note documenting the provenance gap.
- from this commit forward, the near-onset lineage has explicit branch authority.

RATIONALE
The near-onset alpha is not an arbitrary post-result retune. It was introduced through a preregistered onset/bisection lineage and later required explicit execution correction when a runtime default of0.25 invalidated mechanism attribution. Continuing descendants at the exact frozen near-onset value preserves lineage identity and scientific reproducibility.

GATE
A YGG-C successor using alpha=0.134765625 is governance-valid only if:
- its preregistration explicitly states that exact value;
- it is a descendant of the established near-onset lineage;
- runtime alpha is proven exact;
- all scientific and harness globals are restored;
- no other authority boundary is crossed.

DECISION
Governance conflict resolved prospectively. YGG-C may resume bounded near-onset descendant experiments under the conditions above.
