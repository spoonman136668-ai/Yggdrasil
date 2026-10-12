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
