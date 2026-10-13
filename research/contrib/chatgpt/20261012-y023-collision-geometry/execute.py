"""Y023: frozen circular collision geometry and Hall-deficiency evaluation."""
import json


def generated_homes(seed, arm):
    homes = [(7 * key + seed) % 16 for key in range(16)]
    selected = [(3 * seed + 5 * j) % 16 for j in range(4)]
    assert len(set(selected)) == 4
    if arm == "four_collision":
        for idx in selected[1:]:
            homes[idx] = homes[selected[0]]
    elif arm == "two_pairs":
        homes[selected[1]] = homes[selected[0]]
        homes[selected[3]] = homes[selected[2]]
    else:
        assert arm == "bijective"
        assert len(set(homes)) == 16
    return homes


def adjacency(homes, radius):
    return [
        {(home + offset) % 16 for offset in range(-radius, radius + 1)}
        for home in homes
    ]


def augmenting_path_cardinality(neighbors):
    owners = {}
    def augment(key, seen):
        for cell in sorted(neighbors[key]):
            if cell in seen:
                continue
            seen.add(cell)
            previous = owners.get(cell)
            if previous is None or augment(previous, seen):
                owners[cell] = key
                return True
        return False
    for key in range(16):
        augment(key, set())
    return len(owners)


def independent_hall_cardinality(neighbors):
    # Hall deficiency, exhaustive over the 2**16 subsets of keys.
    masks = [sum(1 << cell for cell in adjacent) for adjacent in neighbors]
    union_masks = [0] * (1 << 16)
    largest_deficiency = 0
    for subset in range(1, 1 << 16):
        lowbit = subset & -subset
        key = lowbit.bit_length() - 1
        union_masks[subset] = union_masks[subset ^ lowbit] | masks[key]
        deficiency = subset.bit_count() - union_masks[subset].bit_count()
        largest_deficiency = max(largest_deficiency, deficiency)
    return 16 - largest_deficiency


def row(seed, arm):
    homes = generated_homes(seed, arm)
    result = []
    for radius in (1, 2):
        neighbors = adjacency(homes, radius)
        actual = augmenting_path_cardinality(neighbors)
        independently_verified = independent_hall_cardinality(neighbors)
        assert actual == independently_verified, "independent Hall oracle mismatch"
        result.append(actual)
    assert 0 <= result[0] <= result[1] <= 16
    if arm == "bijective":
        assert result == [16, 16]
    return {
        "seed": seed,
        "cohort": "development" if seed < 4 else "heldout",
        "arm": arm,
        "radius_one": result[0],
        "radius_two": result[1],
        "radius_two_margin": result[1] - result[0],
        "hall_deficiency_one": 16 - result[0],
        "hall_deficiency_two": 16 - result[1],
        "independent_hall_oracle_pass": True,
    }


def run():
    arms = ("bijective", "four_collision", "two_pairs")
    rows = [row(seed, arm) for seed in range(8) for arm in arms]
    heldout = [r for r in rows if r["cohort"] == "heldout" and r["arm"] != "bijective"]
    positive = [r for r in heldout if r["radius_two_margin"] > 0]
    residual = [r for r in heldout if r["hall_deficiency_two"] > 0]
    if not positive:
        classification = "NO_RADIUS_TWO_RESCUE"
    elif residual:
        classification = "MIXED_RESCUE_WITH_RESIDUAL_DEFICIENCY"
    else:
        classification = "RADIUS_TWO_RESCUE"
    return {
        "schema": "yggdrasil.y023-collision-hall-deficiency.v1",
        "predecessor_head": "740ad8cf6e77f6b67e63a1d7ed2d51bd00d51dad",
        "rows": rows,
        "classification": classification,
        "heldout_rescue_cases": len(positive),
        "heldout_residual_deficiency_cases": len(residual),
        "model_calls": 0,
        "claim_limit": "Synthetic matching and collision geometry; no learned memory or original R016 validation",
    }


if __name__ == "__main__":
    outcome = run()
    assert outcome == run()
    print(json.dumps(outcome, sort_keys=True, indent=2))
