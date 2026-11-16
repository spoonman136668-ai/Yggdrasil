# WSP-128 — contradiction-gated unknown-law repair with stored numerical weights

**Development-only source. No original scientific first-use, accepted model admission or merge.**

WSP-127 has frozen **DEVELOPMENT_NO_GO** evidence: adaptive active causal probing raised rank8 FIT coverage to 86.83% from fixed 53.91%, but missed 95% and generated **23.01% confident wrong on rank9 unfamiliar laws**; independently optimized symbolic inference tied every numerical result. That negative remains unchanged.

WSP-128 tests a *distinct mechanism*: after cold-start learning 64 previously exposed WSP127 rank8 worlds, can the learner use 512 charged interventions on a suddenly altered causal world to detect inconsistent evidence, directly allocate a rank-one residual correction, and retain the previous valid knowledge without dangerous guessed relationships?

## Frozen preregistration before source

- The only first commit was `4c2b23de44e8188a747e14de7bbf975e9e524c29` (`prereg.json`). No source, implementation or measurement existed at that boundary.
- Original parent: WSP127 exact final `5047bd21a69c065f1337c033d914eadfb8939672`; draft PR #1144; accepted `main` unaffected.
- Existing public source-only training: 64 WSP127 fitted rank8 laws, 65,536 paid actions per base learner; keep full warm-prior snapshot immutable.
- New 192 synthetic diagnostic views (64 unchanged, 64 rank9 one-factor changes, 64 rank10 two-factor changes) using scrambled opaque source seed IDs `139000..139191`. Every view exposes only a public typed 64×64 action set and past law ID, not the hidden physics condition. The source-only generator and labels are inspectable development data, NOT independent sealed scientific evaluation.
- Exactly **512** real interventions per view per arm, 98,304 probing actions per arm, 3,584 withheld decisions each. Adaptive numerical and independent optimized symbolic reference receive IDENTICAL action transcripts; SAFE_ABORT, STALE_PRIOR and NO_UPDATE receive the same paid consequences.
- Probe first up to six complete rows, stop after the first witnessed contradiction in a complete row, then test the distinguishing pivot column on other rows, then spend every remaining action lexicographically. A known original row relation may only be corrected by supported rank-one evidence. If corrections contradict new observations, abstain rather than confidently guess.
- Mandatory ranking: rank9 >=75% withheld correct and <=1% wrong confident, >=15 percentage-point coverage gain over same-action SAFE_ABORT; unchanged >=80% withheld correct, <=1% wrong and <=1% false alarm; off-family rank10 <=1% confidently wrong. Failure of ANY is a legitimate development NO-GO, even when within-family gains exist.

**Strong controls and limitation:** Symbolic residual recovery is independently implemented. Exact symbolic parity is NOT proof of unique direct numerical advantage; rank-one residual form is supplied. Detection is not guaranteed in environments that lack enough discriminating interventions. Trained conventional model, independently held source and matched whole-process efficiency are not qualified. Unknown-law rank10 negative must be preserved unretuned.

## Reproduction (source-safe only)

```bash
python -B -m unittest discover -s research/contrib/chatgpt/WSP-128 -p 'test_*.py' -v
```

This test runs the original 192-world comparison **once** and emits one `WSP128_FINAL_ENGINEERING_JSON` trace. Do not rerun a second full comparison except when mandatory source-identical qualification requires it.

G29 source pinning uses the inherited `scripts/build_code_atlas.py` workflow and only the three derived `.ice/code-atlas.{html,ice,json}` outputs. Dual-platform final qualification reruns WSP117–128 and entire root regression on the exact candidate SHA. Preserve prior WSP source/data/negative outcomes. Do not introduce new controllers, runners, schedulers, paid APIs or alter Wingless/Hybrid/FORGE authority.
