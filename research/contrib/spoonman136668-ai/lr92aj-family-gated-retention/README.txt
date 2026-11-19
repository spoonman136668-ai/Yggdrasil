LR-92AJ — FAMILY-SELECTIVE CAUSAL-INFERENCE RETENTION
====================================================

Result: DEVELOPMENT NO-GO, 9/10 prospectively frozen checks PASS.
External bounded synthetic learning; NOT native Yggdrasil training,
SCIENTIFIC_PASS, scientific first-use, model promotion or deployment.

CHECKPOINT / AUTHORITY
----------------------
Repository: spoonman136668-ai/Yggdrasil
Base main: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9
Parent research: draft PR #1289, 6ec321ad4150e461788e0b07341104328e22440b
No main/source-index/controller/accepted model mutation.

Frozen prereg before scoring:
 commit eb99bb10168a2115c8aacdceaa19e866c33c5fb1
 decoded SHA256 90103119d7c69478f42cd2a547b885b7215589b03dd21413bd0214dcce4ee6e6
Frozen source before scoring:
 commit 4f716b6cc96d2b6d2eb68fd61906d2d5689ae039
 decoded SHA256 ea3e2a616234ba9e74ec28b60273a237c7cdadb05658717064e6ca88e1ace526
11/11 fixture-only preprimary tests PASS. All three exact predecessor
sources committed and hash-checked on GitHub before the one scored run.

EXPERIMENT
----------
Goal: avoid LR-92AI's one-step retention loss while preserving newly
learned two-step predictive relationships, without changing action count.

A previous-world retrospective DEV check fixed the threshold at 0.55.
No primary seed was inspected during threshold selection. On each new
world, the same 64 adaptive interventions and labels update:
 (a) LR-92AI's 7,936-state static/lag1/lag2 mixture and
 (b) the frozen LR-92AH first-order learner replaying exactly the
     SAME observed intervention outcomes.

If the largest posterior causal-family mass >= 0.55, use its conditional
predictive distribution. Otherwise use the frozen first-order learner's
prediction. No validation label influences the family choice.
The candidate is prediction-only, with NO mechanism acceptance or
promotion interface.

Controls:
 - Same gate with balanced (not adaptive) actions, equal 64 budget
 - Shuffled-history gate on the candidate's EXACT action tape/labels
 - Ungated mixture on the EXACT candidate tape
 - Family-conditional inference without fallback on the EXACT tape
 - Unchanged LR-92AH one-step EIG learner with its own chosen actions
 - Unchanged static EIG learner with its own chosen actions
 - Fully fitted RF32, same candidate 176 fit labels/history features
   (but no historical DELTA prior—descriptive, not information matched).

Fresh primary: seeds 929203101, 929203102, 929203103; 240 worlds,
81 static, 81 lag1, 78 lag2; 112 context0 and 64 context1 observations,
256 heldout per world, fixed 35% output-flip noise. Exactly ONE scored
primary; NO postscore tuning, additional seed sweeps or threshold edits.

RESULTS — accuracy of heldout binary consequences
--------------------------------------------------
Family        Gate EIG    Gate balanced   Gate sham   Ungated mix   Prior lag1 EIG
Static         64.337%       63.599%      64.304%      64.337%       64.246%
Lag1           55.628%       56.351%      53.308%      54.929%       56.916%
Lag2           56.435%       54.597%      51.052%      56.555%       51.422%

Full static EIG baseline: 64.844% static; RF32: 59.819% static, 53.540%
lag1, 53.175% lag2. The ablation WITHOUT first-order fallback scored
64.390% static, 54.798% lag1 and 56.941% lag2.

One failed frozen check:
 - Lag1 retention vs original learner: gate 55.628% vs original
   56.916%, a -1.288-percentage-point loss vs frozen max -0.5 pp.

Positive bounded findings:
 - Gate improves lag1 by +0.699 points over ungated mix.
 - Lag2 gain over original lag1 EIG +5.013 points, and vs sham +5.384.
 - Static retention loss vs old static EIG -0.506 points, within 1pp.
 - Lag2 gate improves 1.838 points over balanced gate, though that
   particular difference was descriptive rather than a frozen GO check.
 - All 64 intervention counts and cold historical DELTA match.

Because lag1 retention criterion failed, the frozen composite is
**DEVELOPMENT NO-GO** despite nine passed checks. Never relax the
threshold or retest primary to reclassify this result.

INDEPENDENT AUDIT / CUSTODY
---------------------------
Preprimary tests: 11/11 PASS.
Primary raw: 1,206,291 bytes; SHA256
  7c9a4f524d749d36def10a5da8611fd566af7fe608e4b33b3f3201703746b4a9
Independent read-only auditor: 146,426 assertions PASS; source SHA256
  b514737308d45d59698cbe22b243b27562cec6677b9e99bed10e58576aaac143
Audit receipt SHA256
  d0c689e2d8b1f0ac8c28ee448aa416353398749fe859fe58b8b26ea9041381ed

The audit recomputes grouped Bayesian likelihoods, selected-action
causal outcomes from stored potential-outcome tapes, matched action
histories and labels, prediction scores, prior baselines and RF refits.
The first auditor attempt failed because of an independent
previous-action history-roll bug. Only the auditor was corrected.
The frozen primary source and output remained byte-identical.
The auditor requires original primary record, which remains in isolated
local custody, **not** uploaded to GitHub in this PR.

GitHub includes every exact source/protocol/fixture file and frozen
predecessors, the auditor and receipt, all 240 paired world-by-eight-arm
correct counts, family choices, trust flags and aggregate results.

Paired ledger raw SHA256:
  404c35a82958afcb95f52c9ed2ce2b4ab97459774c195b2b2367a5417f1a861b
Encoding: zlib compressed then base64, stored as
  paired_ledger.bin.zlib.b64.
Decoded binary format: bytes 0..7 ASCII LR92AJ01; next 240 records of
24 bytes each: little-endian '<8B8H' = seed_index, world_id,
family_index (0 static, 1 lag1, 2 lag2), q, base_id, mask,
gate_trusted_0_or_1, gate_selected_family_index, followed by eight
uint16 correct-label counts in this order:
  gate_eig, gate_balanced, gate_sham, mix_eig, no_fallback,
  old_lag_eig, old_static_eig, rf32.
These are score summaries, not the raw action tapes.

REPRODUCTION
------------
In a NEW clean isolated directory download all *.py.zlib.b64 and the
prereg archive. Decode with:
 python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_bytes())))" lr92aj_run.py.zlib.b64
Also decode lr92ai_run.py, lr92ah_frozen.py, lr92af_frozen.py,
prereg.json, test_preprimary.py and audit_readonly.py.

Python 3.13.5, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0:
 python -m unittest -v test_preprimary  # 11/11 PASS
 python lr92aj_run.py                   # ONE SHOT; refuses overwrite
 sha256sum primary_result.json          # expect 7c9a4f524...1703746b4a9
 python audit_readonly.py               # expect 146426 checks PASS

Do NOT run over a previous experiment, requalify protected first-use,
modify a native Yggdrasil model or use the G29 source-atlas result
as evidence of causal intelligence. Indexed .py/.json/.md paths remain
unchanged; added research files are nonindexed .txt/.b64 artifacts.

RESEARCH CONCLUSION
-------------------
The evidence-specific fallback partly repairs one-step retention,
and preserves two-step prediction under the same action budget, but
did NOT meet the required retention standard. The candidate should
remain unpromoted. Investigate selective memory preservation using
PREDECLARED additional causal-evidence constraints and independent
unfamiliar causal structures, not another threshold sweep on these
240 used evaluation worlds.

Full native regression, cross-platform scientific reproduction,
whole-process compute-matched science, owner authorization for first
use and production acceptance: UNVERIFIED / HOLD.
