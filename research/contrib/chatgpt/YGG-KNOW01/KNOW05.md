# KNOW05 — paired-view projection alias control (research-only)

**Date:** 2026-11-19  
**Scope:** bounded negative-control hardening of existing KNOW04 source-only Q/P/Q bridge.  
**Branch:** existing PR #1327; no new PR, learner, owner, native weights or factual ingestion.

## Exact failure mode and invariant

KNOW04 requires unique *paired* public views of the form `((state, action0), (state, action1))` with a common first state coordinate. There are exactly `2 * 2 * 2 = 8` such encodings, but `ExplicitPublicViewProjection.shadow_plan()` passes **only the first** `(state, action0)` to `TypedFactualReadoutBridge.independent_native_plan()`: at most **four** distinct planner inputs. Injectivity of the full paired mapping does not imply injectivity of the actual planner input.

KNOW05 leaves valid factual `query()` results and all eight paired encodings unchanged. At construction, it counts first-view planner inputs. When two or more distinct Q/P/Q mappings project onto the same first view, `shadow_plan()` returns `ABSTAIN_AMBIGUOUS_NATIVE_PLAN_VIEW`, **does not call the planner** and does not update any factual or native checkpoint. Existing noncolliding shadow readouts keep their prior behavior. This is a conservative interface safety guard, *not* a causal-discovery mechanism.

## Regression and limits

Two fixture-only deterministic regression tests cover (1) pair-unique/first-view-colliding mappings that now abstain with zero planner calls and identical native/factual checkpoint bytes and (2) the finite eight-pair/four-first-view pigeonhole case. Inherited KNOW04 negative controls, read-only manifest pinning and full source tests remain required. No protected original-world source first-use, owner action, new training, state restoration, merge or model-policy activation is authorized by these tests.

The representation cannot express an arbitrary 21-million-triple graph, prove semantic identification of historical Q/P/Q facts with causal states or establish improved unfamiliar decisions. Even a noncolliding synthetic view remains merely a **proposal**, never an accepted native causal witness. All native model owner authentication, cold old-task retention, independently grounded source evidence, preregistered strongest-control science, and source #426 authority requirements remain unsatisfied.

**Qualification labels:** engineering negative controls require exact-source Linux/Windows CI; science **UNVERIFIED** (Amalgam historical DEV_NO_GO); deployment **NONE**. The central Amalgam work chat remains sole cumulative model coordinator.
