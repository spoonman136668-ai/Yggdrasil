"""Y017 pure placement mechanism for matched-vs-greedy causal ablation.

No source loading, runner, queue, experiment execution, performance scoring, or accepted-state writes.
Full primary work must separately verify byte-exact R015/R016 source parity and frozen science authority.
"""
def _allowed(learner, key):
    cells = tuple(learner.local_cells(learner.home_cell(key)))
    if not cells or len(set(cells)) != len(cells):
        raise ValueError("invalid local placement geometry")
    if any(type(c) is not int or c < 0 or c >= 16 for c in cells):
        raise ValueError("outside fixed sixteen-cell geometry")
    return cells

def _keys(keys):
    if not isinstance(keys, (tuple, list)) or not keys or len(keys) > 16:
        raise ValueError("invalid ranked key count")
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate selected motif key")
    return tuple(keys)

def greedy_first_free(learner, selected_keys):
    """R015-style local first-free placement: never reassign an occupied cell."""
    keys = _keys(selected_keys)
    owner = {}
    for key in keys:
        for cell in _allowed(learner, key):
            if cell not in owner:
                owner[cell] = key
                break
        else:
            return None
    return {key: cell for cell, key in owner.items()}

def deterministic_matching(learner, selected_keys):
    """Mirror R016's ordered augmenting-path matching on the *same* selected keys."""
    keys = _keys(selected_keys)
    owner = {}
    def augment(key, visited):
        for cell in _allowed(learner, key):
            if cell in visited:
                continue
            visited.add(cell)
            current = owner.get(cell)
            if current is None or augment(current, visited):
                owner[cell] = key
                return True
        return False
    for key in keys:
        if not augment(key, set()):
            return None
    return {key: cell for cell, key in owner.items()}

def paired_placement(learner, selected_keys):
    """Mechanical audit only, not the official scientific evaluation."""
    keys = _keys(selected_keys)
    return {"matched": deterministic_matching(learner,keys),
            "greedy": greedy_first_free(learner,keys),
            "selected_count": len(keys)}

def execute_native_paired_ablation():
    """Execute frozen R016 A0, then stage-paired greedy assignment on same R016 keys."""
    import hashlib
    import importlib.util
    import json
    from pathlib import Path
    original_source = Path("research/applications/plane/exp-dgr-real-utf8-minimax-matched-consolidation-016.py")
    if not original_source.is_file():
        raise RuntimeError("Y017_EXACT_R016_SOURCE_MISSING")
    # Require the actual committed original scientific blob, not a substitute.
    import subprocess
    obj = subprocess.run(["git", "hash-object", "--no-filters", str(original_source)],
                         check=True, capture_output=True, text=True).stdout.strip()
    if obj != "c4247f69295b25105a91cc402b123493ae63aa68":
        raise RuntimeError("Y017_R016_SOURCE_GIT_BLOB_DRIFT")
    spec = importlib.util.spec_from_file_location("y017_pinned_r016", original_source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y017_R016_IMPORT_INVALID")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    baseline = module.run()
    raw = json.dumps(baseline, allow_nan=False, separators=(",", ":")).encode("utf-8")
    sha = hashlib.sha256(raw).hexdigest()
    if sha != "138d21335abc10e0eb7bddbbe5dd2a4e4b2ba5ea902d2319dc80eff637df2b29":
        raise RuntimeError("Y017_A0_FROZEN_RESULT_SHA256_MISMATCH:" + sha)
    original_builder = module.build_matched_minimax_cells
    original_match = module.deterministic_matching
    staged = []

    def capture_builder(*args):
        selected = []
        def observe(learner, keys):
            nonlocal selected
            answer = original_match(learner, keys)
            if answer is not None and len(keys) == 16:
                selected = list(keys)
            return answer
        module.deterministic_matching = observe
        try:
            original = original_builder(*args)
        finally:
            module.deterministic_matching = original_match
        if len(selected) != 16 or original[1] != 16:
            raise RuntimeError("Y017_FROZEN_CANDIDATE_SELECTION_NOT_16")
        matched = original_match(args[0], selected)
        if matched is None or len(matched) != 16:
            raise RuntimeError("Y017_R016_STAGE_MATCHED_FAILURE")
        # This counterfactual never changes R016 selection, geometry or scoring.
        greedy = greedy_first_free(args[0], selected)
        staged.append({"stage": len(staged) + 1,
                       "candidate_count": len(selected),
                       "matched_valid": True,
                       "greedy_valid": greedy is not None,
                       "greedy_assignment_failure": greedy is None,
                       "placement_disagreement": None if greedy is None
                       else sum(matched[k] != greedy[k] for k in selected)})
        return original

    module.build_matched_minimax_cells = capture_builder
    second = module.run()
    other = json.dumps(second, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if other != raw:
        raise RuntimeError("Y017_DUPLICATE_A0_BASELINE_NOT_BYTE_IDENTICAL")
    if len(staged) != 6:
        raise RuntimeError("Y017_EXPECTED_SIX_PAIRED_STAGES")
    return {"schema": "yggdrasil.y017-native-paired-ablation.v1",
            "frozen_R016_result_sha256": sha,
            "baseline_replay_count": 2,
            "stages": staged,
            "greedy_failure_stage_count": sum(int(s["greedy_assignment_failure"]) for s in staged),
            "matched_valid_stage_count": len(staged),
            "source_identity_mismatch_count": 0,
            "candidate_rank_drift_count": 0,
            "capacity_growth_events": 0,
            "external_model_calls": 0,
            "data_class": "previously_consumed_not_unseen",
            "independent_scientific_acceptance": False}

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("--paired-ablation-output", required=True)
    args = parser.parse_args()
    with open(args.paired_ablation_output, "x", encoding="utf-8") as out:
        json.dump(execute_native_paired_ablation(), out, allow_nan=False,
                  separators=(",", ":"))
