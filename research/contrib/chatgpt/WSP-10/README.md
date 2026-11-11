# WSP-10 — Direct full-table-to-weight programming (public DEV)

This experiment continues [WSP-09 PR #874](https://github.com/spoonman136668-ai/Yggdrasil/pull/874) in an **isolated research-only** descendant branch. It does not merge, promote, deploy or touch FORGE, owners, runners, schedules, queues or accepted research state.

## Question and exact claim

Can the **complete task-specific weights** of a small, functioning numeric threshold circuit be filled directly from an explicit Boolean function specification, with **zero gradient training**? Yes, for the frozen two/three-input truth-table domain. All task-specific connections start at zero. For each positive truth-table minterm, the compiler writes one polarity-specific sensory edge per bit to a previously disconnected threshold gate, then one edge from that gate to an OR output. The numerical circuit evaluates through weighted summation and thresholds; it never reads a function mask at runtime.

**Information honesty:** The compiler receives the entire task specification (4 or 8 outcome bits per function). It does not learn from zero information. It cannot invent unknown operator types, generalize to undisclosed functions, or establish compute/data/energy superiority over an exact symbolic compiler or a fully trained model. AND, NOT and OR capabilities, gate sites and threshold rules are supplied by the programmer. This tests the engineering of directly wiring neural weights, not spontaneous native model learning.

## Frozen test

[prereg.json](prereg.json) commit `ea12f8f699584afdbff691dbcf621c0d4e447ae7` preceded the first WSP-10 primary result. Exhaust all 16 two-input and 256 three-input Boolean functions, 2,112 output queries. Compare an exact symbolic truth-table reader with the numerical circuit, all-zero unprogrammed control, one output-link ablation for every nonzero mask (270), a bit-order negative, and every canonical checkpoint restore/rejection. The 3-input crossbar holds 56 task-specific binary synaptic weights; zero gradient steps.

## Reproduce focused DEV

```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-10 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-10/run_dev.py
```

Python standard library only. First author-visible local run: Python 3.13.5 / Linux x86_64, 12/12 focused tests and the 272-spec evaluator PASS. See [result.json](result.json) and [provenance.json](provenance.json) for metrics/source hashes. **Full original+WSP01–10 exact-final-SHA Windows/Linux regression, G29 pinned atlas and scientific qualification are separate outstanding requirements until corresponding independent run receipts exist.** Local tests do not satisfy those gates.
