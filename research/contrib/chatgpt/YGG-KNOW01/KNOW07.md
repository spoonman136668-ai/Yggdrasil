# KNOW07 — stop exporting aliased public-view proposals

**Date:** 2026-11-19 (US Eastern)  
**Scope:** small source-only contract fix on existing research PR #1327, building on independent KNOW05 and KNOW06. No new PR, trainer, learner, owner or source first-use. The sole canonical coordinator is Unified Causal Intelligence Amalgam Work chat/PR #1278.

## Previously incomplete noninterference boundary

KNOW05 correctly prevented `shadow_plan(Q,P,Q)` from passing first-view collisions to the native planner, but `query(Q,P,Q)` still returned `SYNTHETIC_VIEW_PROPOSAL_ONLY` and a non-null `paired_public_views` mapping for the very same collision. A downstream consumer of the readout payload could therefore mistake a paired-view-unique mapping for a usable first-view-unique native plan input. The existing bridge's independent plan method remains separately callable: this contract narrows **one research API surface**, not general security authority.

## Implemented readout contract

For a direct supported fact whose first planner input is shared by two or more manifest bindings, `query()` returns `ABSTAIN_AMBIGUOUS_NATIVE_PLAN_VIEW` and `paired_public_views=None`. Direct `TypedFactualReadoutBridge.fact()` remains intact; historical factual membership is not erased or misrepresented as unknown. `ABSTAIN_UNKNOWN_FACT` takes precedence when the fact itself is unsupported. Noncolliding, explicitly mapped historical/development fixture facts retain their prior synthetic shadow-only proposal behavior. The KNOW05 `shadow_plan()` guard remains as defense in depth.

Three new fixture-only tests and two tightened KNOW05 tests enforce query-level collision abstention, history preservation, unknown-first precedence, and noncolliding backward compatibility. All native, specialist, factual and witness state remains unchanged. Existing KNOW06 real native-sublearner cold shadow continues to use two distinct first views and needs no contract change.

## Qualification and limits

Full source-only root + KNOW + G29 regression on Linux and Windows, pinned atlas seal, and existing real-image compatibility job must pass on the final candidate SHA. Any green engineering result does not establish Q/P/Q→causal-semantic alignment, real new knowledge acquisition, decision improvement, newly learned relations, canonical custody, owner acceptance or scientific superiority. SCIENCE remains UNVERIFIED with historical Amalgam DEV_NO_GO. Protected source first-use on issue #426 is blocked. No operator/runner or training/deployment authorization is conferred.
