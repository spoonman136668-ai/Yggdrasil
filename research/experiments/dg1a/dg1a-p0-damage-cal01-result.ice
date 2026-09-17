TITLE: DG-1A-P0 DAMAGE-CAL-01 Result — Center-Lesion Severity
DATE: 2026-09-17
STATUS: EXPLORATORY CALIBRATION COMPLETE
TRACK: DG-1A
CONFIDENCE: SUPPORTED FOR SANDBOX PROTOCOL SELECTION; NOT CONFIRMATORY SCIENTIFIC EVIDENCE

QUESTION
What is the smallest candidate center-lesion fraction that produces valid functional loss across at least 4 of 5 regeneration seeds while remaining non-annihilating on at least 4 of 5 seeds?

EVIDENCE CLASS
MEASURED SANDBOX CALIBRATION.

PROVENANCE LIMIT
Runs were performed in the isolated reconstructed ChatGPT CPU workspace, not an authenticated commit-bound checkout. The result selects a protocol candidate only.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_damage_cal01.json

CANDIDATES
0.50 x 0.50
0.60 x 0.60
0.70 x 0.70

FROZEN VALIDITY RULE
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10;
- finite states.

FROZEN NON-ANNIHILATION RULE
- post-damage active cells > 0;
- at least 20% of pre-damage active cells remain.

MEASURED RESULT — 0.50
Valid lesions: 3 / 5
Non-annihilating: 5 / 5
Valid seeds: 0, 1, 3
RelativeDamageEffect by seed:
0 = 0.16290
1 = 0.12365
2 = 0.08343
3 = 0.12755
4 = 0.08879

RESULT
Fails the minimum 4/5 validity requirement.

MEASURED RESULT — 0.60
Valid lesions: 4 / 5
Non-annihilating: 5 / 5
Valid seeds: 0, 1, 3, 4
RelativeDamageEffect by seed:
0 = 0.23139
1 = 0.14116
2 = 0.09603
3 = 0.15910
4 = 0.12511

Fraction of active phenotype remaining after damage:
0 = 0.4500
1 = 0.4815
2 = 0.5909
3 = 0.5588
4 = 0.4583

RESULT
Passes both preregistered selection conditions.

MEASURED RESULT — 0.70
Valid lesions: 5 / 5
Non-annihilating: 5 / 5
Valid seeds: 0, 1, 2, 3, 4

RESULT
Passes both preregistered selection conditions but is not selected because a smaller candidate already passes.

SELECTION
0.60 x 0.60 center lesion.

RATIONALE
The selection rule requires the smallest passing candidate. Therefore 0.60 is mechanically selected; choosing 0.70 because it produces 5/5 valid lesions would violate the preregistered minimal-severity rule.

IMPORTANT OBSERVATION
Seed 2 remains just below the functional-loss threshold at 0.60 with RelativeDamageEffect = 0.09603 despite retaining 59.09% of its active cells after damage. This is retained as a weak-damage seed and must remain excluded from valid-pair recovery inference unless a future independently preregistered protocol changes.

RECOVERY OBSERVATION — NOT USED FOR SELECTION
All evaluated regeneration phenotypes recovered to bounded RecoveryFraction 1.0 across the candidate severities in this calibration, with stable T90 remaining attainable. This did not influence severity selection and must not be promoted to confirmatory evidence.

DECISION
Freeze 0.60 x 0.60 as the center-lesion severity for the next matched P0 growth-only versus regeneration gate.

Do not change the 10% RelativeDamageEffect validity threshold.
Do not use 0.70 for the next gate unless the 0.60 protocol independently fails under a new preregistered reason.
Do not introduce Fibonacci scheduling into P0.

NEXT EXPERIMENT
Create a follow-up P0 amendment freezing 0.60 lesion severity, then repeat the matched five-seed growth-only versus maturity-gated-regeneration family from the new protocol. Commit-bound execution remains required before confirmatory support is claimed.