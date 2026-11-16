# NKR-10 — Historical TRAIN relationship-rule induction (read-only)

**Status:** source-safe development candidate. Scientific acceptance: **NO**. Accepted Yggdrasil: **UNCHANGED**.

## Question and difference
NKR-09 (#1137) can read the 21,343,681-record historical factual image, but its induced (P1,P2)->P3 templates were demonstrated using synthetic Q/P/Q edges. This isolated successor checks whether any templates have **direct witnesses in the original previously consumed historical TRAIN triples themselves**. WSP-105/116 already investigate path retrieval and knowledge-dose effects; WSP-110/111 already study synthetic programmed operators. This experiment adds neither a retrieval benchmark nor a new operator substrate.

## Frozen procedure
Parent NKR-09 SHA `5c9c9c93c63d3705383f9bd3d5d088f983030b3d`.
Prereg-first commit `274a919c3c324d44a10d52a4fbf9975fdf29451e`.
Only already qualified NKR-05 installed historical TRAIN image is accepted; SHA256 `6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1`. No valid/test, no new source download.

With a read-only, SHA-verified installed session, sample 32,768 evenly spaced **sorted row indices** from the 21.3M triple image. For each direct triple (X,P3,Z), inspect at most eight sorted outgoing X edges, then eight outgoing edges for each intermediary Y. Only when both X-P1-Y and Y-P2-Z are source-observed does the candidate count **one unique support subject** for template (P3,P1,P2). A candidate needs six different supporting subjects. Never treat an absent triple as false. Freeze these limits, even when they produce zero templates; no exploratory rerun with a different sampling rule after seeing the outcome.

This sample is **not representative**: lexicographic stride and first-eight outgoing restrictions can exclude useful contexts. A rule is source-backed graph correlation, not an authenticated causal law, not current truth, and not a new Wikidata fact.

## Evidence and controls
Source-safe unit tests compare against an independent exhaustive set/Counter join on a small graph; duplicates, missing path legs, byte/type drift, forbidden admission, and explicit sampling bias must fail or abstain. NKR-09 full 21M interface proof is inherited, not recreated. No inferred proposition is entered into factual or causal memory, no historical image is rewritten.

Before any optional historical TRAIN scan, require the exact final candidate: both OS focused and mandatory root regression, source-pinned G29, and previous image identity/expiry checks. After scanning, store compact metrics and support counts only; **never re-upload the 256 MB source image**. Zero supported templates is a valid bounded negative. A positive must be reported as `HISTORICAL_TRAIN_CORRELATION_DIAGNOSTIC`, never `SCIENTIFIC_PASS`.

Execution for an already installed, verified NKR-06 session (research owner selected):
```bash
python -B research/contrib/chatgpt/NKR-10/mine_historical.py --installed-session /path/to/already-installed-session
```

## Authority
Development-only research branch; no accepted ref mutation, live model, permanent storage or owner install, protected scientific first use, new scheduler/controller, private runner, paid API or merge. A future genuine causal-law test must use authentic intervention consequences and independently trained matched controls. The present experiment does not.
