# KNOW35 — persistent two-bank causal memory, mock-only development candidate

**Status: ENGINEERING CANDIDATE; prospective science UNVERIFIED; deployment NONE.**

KNOW34's six-slot recent-history buffer is eventually overwritten by A on an
A→B→A return. This candidate stores two independent capped Beta posteriors per
physical cell, with an observable-only likelihood-ratio gate shared by each
adjacent cell pair. Neither true phase labels nor evaluator laws enter updates.

- Budget: 8 physical cells × 2 Beta heads, 6 updates/head/cell, 4 pair gates,
  at most 256 witnessed public events, canonical cold checkpoint under 4 KiB.
- Mock-only functional diagnostic: noise-free A(64)→B1(64)→A(64)→B1(64),
  same public `(context, action, physical input)` geometry as KNOW34.
  Verify original A head survives, B posterior remains after returning to A,
  and the gated prediction can reselect B on reappearance; compare with
  uninterrupted A, and round-trip checksummed cold restore.
- Negative controls: corrupted checksum, duplicate JSON keys, fabricated
  evidence counts, malformed events, forbidden types.
- **Known failure risks:** posterior-head freezing after six witnesses prevents
  adaptation to within-regime drift; noisy outliers can induce false switches;
  the fallback bank starts with an uninformed Beta(1,1), and this is not a
  fully trained or compute-matched conventional HMM comparison.
- This is **NOT** a held trial, a scientific gain, native integration,
  independent reproduction, original-source experiment or authorized
  promotion. The existing KNOW34 preregistered negative remains unchanged.

**Science gate after engineering qualification:** preregister a *new* disjoint
synthetic held cohort and fixed noise conditions BEFORE implementation of any
held-source evaluator. Compare at matched information, actions, slot/byte
budget and compute against a fitted Bayesian/HMM switching learner, rolling
memory, single posterior and an equal-capacity two-bank random-gate ablation.
Require prequential B accuracy, old-A and B cold retention, no-label reactivation,
false-switch rate and support coverage. A passing mock cannot waive these.
Existing Amalgam #1278 remains the sole model-integration owner; protected
original-world #426 first-use is excluded.
