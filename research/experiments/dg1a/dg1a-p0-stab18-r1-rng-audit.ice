TITLE: DG-1A-P0-STAB-18-R1 — Pre-Execution RNG Domain-Separation Audit
DATE: 2026-09-18
STATUS: PRE-EXECUTION METHOD AUDIT — NOT A SCIENTIFIC RESULT
TRACK: DG-1A
CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Verify that the R1 causal-probe pseudorandom construction removes the deterministic stream alias discovered in the original unexecuted STAB-18 candidate.

THIS RECORD DOES NOT
- qualify the repository test suite;
- replace executable pytest;
- execute the canonical seed-0 scientific candidate;
- establish a P0 gate result;
- establish formal statistical independence.

ORIGINAL DEFECT
Original probe:
    main random field < 0.25

Immediate first-step fire mask:
    same main random field <= 0.50

Therefore:
    ProbeDrop subset FirstFireMask
and conditional overlap:
    P(FirstFireMask | ProbeDrop) = 1.0

R1 CONSTRUCTION AUDITED
Fixed domain tag:
    DG1A_P0_STAB18_R1_CAUSAL_PROBE_V1

Probe seed:
    SHA256(main_generator_state_bytes || domain_tag)
    first 8 bytes unsigned big-endian
    AND 0x7FFFFFFFFFFFFFFF

Probe random field is sampled from a temporary torch.Generator.
The main future-trajectory generator is not advanced by probe construction.

REFERENCE FIXTURE
Runtime:
- CPU
- PyTorch 2.10 family
- main generator manual_seed(1)
- field shape [1,1,9,9]
- probe threshold < 0.25
- first-fire threshold <= 0.50

Observed:
- derived probe seed: 3494006018084941813
- probed cells: 14
- probed cells outside first fire mask: 7
- main generator unchanged: true
- probe equals first-main-stream <0.25: false
- same main state reproduces same probe: true
- different main state changes probe: true

1000-SEED SANITY STUDY
Main seeds:
    0..999

Field:
    [1,1,40,40]
    1600 cells

For each seed:
- derive R1 probe generator from main generator state;
- sample probe at threshold <0.25;
- independently sample first-main-stream fire field at threshold <=0.50 from an exact clone of the main state;
- measure probe fraction;
- measure fraction of probed cells also in the first fire mask.

Observed across 1000 seeds:
- mean probe fraction: 0.250284375
- mean conditional probe/fire overlap: 0.5002216281204747
- overlap standard deviation: 0.024788104684236624
- minimum conditional overlap: 0.40749414519906324
- maximum conditional overlap: 0.5687830687830688

INTERPRETATION
The R1 construction removes the original deterministic subset relationship.

Under this finite audit, the observed conditional overlap is centered at approximately 0.5, matching the canonical fire-rate marginal rather than the original forced overlap of 1.0.

This supports use of the fixed hash-derived probe domain as a practical pseudorandom domain-separation mechanism for the preregistered R1 experiment.

It does not prove mathematical independence.
The scientific interpretation remains group-level dependence under this intervention.

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = ANALYTIC_RUNTIME_EQUIVALENT
canonical_scientific_execution = false

RELATED RECORDS
research/experiments/dg1a/dg1a-p0-stab18-spec.ice
research/experiments/dg1a/dg1a-p0-stab18-r1-spec.ice
research/status/dg1a-p0-status.ice
