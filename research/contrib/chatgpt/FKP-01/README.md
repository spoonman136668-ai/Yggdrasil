# FKP-01 — Foundation knowledge priming (source-only preparation)

Tracked by [Issue #1088](https://github.com/spoonman136668-ai/Yggdrasil/issues/1088).

## Question

Does initializing a native, tokenless causal learner with reusable **structured**
concept and relationship knowledge let it invent *previously unseen compositions*
and retain them more efficiently than an otherwise equally informed unstructured
representation, a strong trained conventional learner, or exact symbolic/Bayesian
computation? This experiment does NOT equate unseen composition with inventing
new physical operators outside the generator's expressive family.

## Commit and source boundary

- Parent Yggdrasil `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- First protocol-only commit: `aba4eae21bff14b8a9e529fd916c4448a7640b87`.
- Pre-source held-input repair commit: `017f1a8bdc67185b92026d85fd40d6ee570b3826`.
- Source implementation started later: `4fbd29c213062421d7cf20a21f14913713b5b38c`.
- Original source-generator spec SHA-256 (describes specification, **not code**):
  `e98f286817ed3e242cafc839a07ea14b05d7af8a34d2e5d170dcc632b5f65cfa`.
- The owner-private HMAC key is NOT in repository files, logs, tools, issue, or
  learner inputs. All protected primary/negative/retention worlds reject
  construction without a minimum 32-byte evaluator key.
- The public primitive maps are intentionally independent of source-private
  law selection. The learner receives `public_view()` and *only genuine observed*
  `(intervention, consequence)` pairs. A production evaluator must keep the
  source instance and key in a separate protected process: Python attribute
  names alone are not a secrecy boundary.

## Development-only source audit

Run with stdlib Python 3.12:

```console
python -m unittest discover -s research/contrib/chatgpt/FKP-01 -p test_source.py -v
python research/contrib/chatgpt/FKP-01/source.py
```

Both commands operate only on public development seeds 200..203. No protected
primary, negative, retention, or disjoint scientific labels are opened.

## Information budget and holdout discipline

The source generates 128 native concept IDs and 16 permuted relation maps per
world: 2,048 public edges. Initial foundation: 32 prior worlds (seeds 100..131)
and 16 source actions per world. The scored new-world probe budget is 16 original
consequences per arm; **the 112 unobserved states** form the primary test. The
all-128-state score is diagnostic and includes 16 seen examples, so it must not
be called held-out accuracy.

Both B (structured) and C (flat) receive the **identical 65,536 foundation edges
and 512 initial action/outcome observations**; competent trained and exact
symbolic/Bayesian controls get the same admissible information. Each new world
requires new graph inputs; no target rule coefficients or prior trial labels are
copied into the learner from the source.

## Advancement / admission

No model/weight state, Yggdrasil accepted branch, research runner, or controller
has been changed. This branch is preparation and has **no observed research
performance**. Preregistration alone, source tests, or a source-only CI PASS does
not prove cognition or scientific value.

Next eligible execution after separate source/evaluator/code custody and
permission verification is a **DEV-only comparison** on seeds 200..215, with
strong baselines and original source effects. Protected primary first-use is a
distinct owner-governed act. A native integration is eligible only after
independent science PASS, unchanged cold retention, full exact-SHA Windows/Linux
regression/G29 and the actual Yggdrasil owner acceptance route; never
auto-merge this draft merely because source engineering passes.
