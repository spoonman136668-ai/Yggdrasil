TITLE: DG-1A-AR-H150 — Repair-Probability Robustness Freeze / Provenance Note
DATE: 2026-09-19
STATUS: ROBUSTNESS EXECUTED / PRIMARY OUTCOMES NOT INSPECTED BEFORE SEED SELECTION
PARENT: dg1a-arh150-regeneration-scaling-micropatch-audit.ice

PURPOSE

Record the independently selected H150 repair-probability robustness family.

PROVENANCE NOTE

After all four p=0.50 primary axes completed,
but before their outcome statistics were inspected,
a fresh robustness seed family and harness copy were fixed locally.

An attempted repository update carrying this freeze
was blocked by the connector before execution.

The robustness run then used the already-fixed local values below.

No primary result was inspected
and no threshold or experimental semantic was changed
before this family was selected.

ROBUSTNESS SEEDS

20260919750000..20260919754319.

4320 worlds.

ROBUSTNESS HARNESS SHA-256

1f68748abcc39bc594b5da5a3c70cece9a1b6fb1758b252e27b07320e4b1148a

The robustness harness differs from the frozen primary harness only in
the CTRL seed-base constant.

CONDITIONS

Axis-A-like:
R = 8,15,30.
damage = 0.02,0.10,0.40.
p = 0.25,0.50,1.00.
80 worlds / condition.

Axis-C-like:
g = 1.00,0.50,0.25.
beta = 0,1,2.
p = 0.25,0.50,1.00.
80 worlds / condition.

EXECUTION CHECK

4320 unique seeds.
No duplicate seeds.
No 256-step censoring.

BOUNDARY

Synthetic robustness only.
No STAB-18-R1 execution.
No production threshold authority.
canonical_scientific_execution = false
canonical_r1_execution_spent = false
