# DG1-SL08 — matched-action physical-error confidence calibration

**Frozen pre-source preregistration:** `66a64101af5c926f43a91e991409034b3b18be35`.
**Exact predecessor:** DG1-SL07 draft PR #989, `c67aca9eb03353bab5b581cbdfed63a7dc18b147`.

## Scientific question

SL07 improved selected returning-world contexts but suffered overconfident predictions on a fourth, out-of-grammar context and lost against a strong conventional model. SL08 asks whether a bounded native, action-specific **paid physical mistake -> temporary abstention -> physically confirmed recovery** mechanism reduces confidently wrong predictions while preserving useful correct coverage. A conventional HMM-style three-bank learner receives an identical confidence mechanism and all six arms see *the same physically executed action history*.

The frozen mechanism is an **online calibration wrapper**, not a changed underlying causal grammar, new program discovery, action planner, token model, neural system or proof of AGI. It may accomplish nothing more than abstention; if so, classification remains negative. The conventional model may still win.

## Frozen protocol

32 newly registered synthetic worlds (eight per ABCA return, ABCB return, stationary and out-of-grammar fourth context). Six arms each perform **80 paid physical steps** including 10 exogenous flips, exactly 70 real cause/effect observations. Every arm performs the same fixed physical actions at every step; no intervention-policy action-selection confound. Each agent is independently cold-restored after step 60. A sealed exact-source checkout, dual Windows/Linux deterministic receipts and full inherited regression are required for engineering PASS.

Arms: native raw; native 2-consecutive-correct local recovery; native 1-correct permissive ablation; native 2-correct global contamination ablation; independent conventional raw; independent conventional 2-correct local recovery. Pre-update raw predictions on charged physical events exclusively update trust. Evaluation truth from the 64 state/action possibilities at 60/64/72/80 is completely hidden from learners. All matched-action trace SHA256, cost and unseen-pair outcomes remain evidence.

**Preregistered primary** requires native calibrated OOD confidently wrong at least 16 below native raw and at least eight below equally calibrated conventional, no excessive correctness/coverage loss on returned/stable worlds, and zero stationary confidently wrong. Merely lowering the error rate by refusing everything does not pass. Exact threshold table: [prereg.json](prereg.json).

## Reproduce (from project root, Python 3.12 stdlib)

```bash
python -m unittest discover -s research/contrib/chatgpt/dg1-sl08-20261113 -p "test_*.py" -v
python research/contrib/chatgpt/dg1-sl08-20261113/sl08.py > sl08-result.json
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build_code_atlas.py --check-if-present
```

The evaluator produces a `classification` regardless of positive or negative outcome; a CI test failure must not be misreported as a scientific negative. The final raw prospective results are recorded in repository GitHub Actions artifacts, not ChatGPT Library. If complete qualification succeeds, record result and provenance on this branch, with original prereg preserved.

## Boundaries

Isolated synthetic source-only research. Keep this contribution **DRAFT and UNMERGED**. No Yggdrasil native/main/accepted/owner/autonomous research loop/first-use change, no FORGE/Wingless/Hybrid/weight-programming edit or controller modifications. No external APIs, language tokens, gradients or deployment. Engineering success and scientific acceptance are separately assessed.
