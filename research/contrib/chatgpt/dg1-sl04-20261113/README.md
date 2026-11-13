# DG1-SL04 — stronger conventional context and cold-retention challenge

**Preregistration:** frozen commit \`7ca7da2595727ebf719d77c51c1c97be7c9d892c\`, before this source or any SL04 results.
**Parent:** fully engineering-qualified draft SL03 PR #985, source \`dacb637b034189029d6b22a885c63d520aedf1fd\`.
**Scope:** isolated external synthetic research, not native Yggdrasil integration.

This challenge **does not revise SL03**. It compares its frozen selective consolidation and conventional offline/online controls against an independently coded **HMM-style two-bank online Bayesian hazard filter** over the same 40-rule/action grammar, and a strong bounded recent-window conventional version-space baseline. The HMM-style baseline is **not full Bayesian online change-point detection**, uses two extra continuous weights, and is not claimed to be capacity/compute identical. Frozen candidate returns cannot be explained as novel architecture superiority if conventional/selective/same-compute models tie.

The 24 precommitted worlds cover unlabeled A→B→A recovery, three-context interference exceeding the two-bank capacity, and cubic out-of-grammar transfer. All models see the **same actual paid 64-step trajectory per world**, including 8 paid physical flips and 56 learning-capable physical actions. No model receives the seed, regime label, transition oracle, or evaluator-only audits. Cohort labels exist only at evaluation time.

Evaluator full 64-pair audits are performed at physical steps 20, 40 and 64; the no-training unseen subset is separately scored. All negative/abstention/confident-error results must be preserved. Preliminary scientific classification is **UNVERIFIED**, until prospective execution and qualification.

Reproduce from repo root:
\`\`\`sh
python -m unittest discover -s research/contrib/chatgpt/dg1-sl04-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-sl04-20261113/sl04.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
\`\`\`

Scientific outcomes, actual per-arm CPU/serialization sizes, source hashes, and full per-world receipts will be committed as \`result.json\` and \`provenance.json\` **in this repo**, never in a ChatGPT Library attachment. No protected science first-use, accepted ref/main/native model, controller, autonomous loop, Wingless, or parallel weight programming modification is allowed.
