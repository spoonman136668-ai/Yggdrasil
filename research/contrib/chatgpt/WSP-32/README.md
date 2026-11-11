# WSP-32 — cumulative fact acquisition: PREPARED, PRIMARY NOT RUN

This successor tests whether acquiring a second actual source fact improves answers
about a composed task while preserving all original facts and the first acquired
fact. WSP-31 is the parent: PR #921, candidate
`162f6bb911933cd68add7eb1eca989100cc61f26`, tree
`131fa5c2943052e4445271e98e23bdf84857c8f0`. Its exact-source Windows/Ubuntu
regression and G29 passed (runs 43081211073 and 43081211039), 321 tests per OS.
WSP-31's actual one-query gain is 170/3840 common unqueried labels; that remains a
finite-family DEV result, not complete training or independent scientific proof.

## Frozen comparison

Use the identical 120 acquired modules, including 13 imperfect modules, and all
1,920 worlds. Every arm receives the same original observations and memory
representation. No target is queried; all 5,760 target labels at inputs 3,5,6
remain unqueried for every arm.

| Arm | Actual source answers | Selection |
|---|---:|---|
| source_two | 2 | Impact selection, then replan after actual first answer |
| source_first_two | 2 | First remaining unknown address |
| source_one | 1 | Impact selection |
| no_query | 0 | No acquisition |

The preset hypothesis requires source_two gains of at least 58 answers over
source_one, at least 116 over no_query, no loss against source_first_two, and
within 57 of each of two same-information converged conventional heads. Any miss
is NEGATIVE. Every previous actual fact and source-bank byte must survive. Each
phase is cold restored; continuation uses the restored state. A symbolic control
must agree exactly, so a symbolic tie is expected rather than superiority.

Persistent numerical values use 208 bits: unchanged 206 binary facts/banks/routes
plus a two-bit counter. Count another 16 derived fallback bits and up to 8 impact
score bits, program/static policy, temporary branch state and Python overhead.
The memory primitive, finite route language and question heuristic are supplied.
This does not invent its own instruments, general architecture or learning rule.
Conventional controls are trained on yoked actual evidence with different
capacity and priors; no efficiency or universal direct-versus-gradient claim.

## Status and reproduction

The preregistration is committed locally at
`54486683c80df4cbb1dc4a3ff7db95d052bb3be2`. Its GitHub
push was rejected by automatic approval review, so it has NOT been published.
No WSP-32 primary run, new learned-result metric, hosted qualification or PR has
been produced. No valid scientific outcome has been consumed or retuned.

Focused tests exercise sequential retention, source locality, query budget,
atomic rejection, counterfactual isolation, cold continuation, checkpoint
corruption, unknown-label contamination and symbolic agreement. Full final
Windows/Ubuntu engineering qualification remains pending the permitted remote
preregistration and primary assay. The original regression's first local attempt
correctly rejected the changed uncommitted source and stale atlas; permanent
source pinning is required before rerunning it.

When remote publication is authorized, publish the preregistration commit first,
then the already prepared implementation, record the actual execution SHA before
running the primary assay, preserve complete stdout/result/provenance, pin atlas
to the evidence source and run full exact-final-source validation on both OSes.
Reuse `.github/workflows/wsp21-pr-validation.yml`; stack a draft on the WSP-31
branch. Do not run the primary twice to seek a positive outcome. Reproduction:
`python research/contrib/chatgpt/WSP-32/run_dev.py`; full qualification:
`python research/contrib/chatgpt/WSP-32/qualify.py`.

No main/accepted ref, merge, deployment, private runner, controller, queue,
scheduler, paid API, protected first-use, Hybrid or FORGE change is included.
