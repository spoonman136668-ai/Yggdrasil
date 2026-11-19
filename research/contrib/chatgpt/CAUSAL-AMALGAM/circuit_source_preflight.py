"""Verify the staged external circuit roster without admitting evidence."""

from hashlib import sha1
from itertools import combinations, product
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
BLOBS = {
    "simcells.v": "3c38ca8b9cf8214dc8ec8b2b1448850052dee10d",
    "COPYING": "a3ca45b42e35a5d026ab7cab9b80fa34a3a089ca",
}
GATES = {
    "BUF": ("A", lambda a, b, c, d: a),
    "NOT": ("~A", lambda a, b, c, d: 1 - a),
    "AND": ("A & B", lambda a, b, c, d: a & b),
    "NAND": ("~(A & B)", lambda a, b, c, d: 1 - (a & b)),
    "OR": ("A | B", lambda a, b, c, d: a | b),
    "NOR": ("~(A | B)", lambda a, b, c, d: 1 - (a | b)),
    "XOR": ("A ^ B", lambda a, b, c, d: a ^ b),
    "XNOR": ("~(A ^ B)", lambda a, b, c, d: 1 - (a ^ b)),
    "ANDNOT": ("A & (~B)", lambda a, b, c, d: a & (1 - b)),
    "ORNOT": ("A | (~B)", lambda a, b, c, d: a | (1 - b)),
    "MUX": ("S ? B : A", lambda a, b, c, d: b if c else a),
    "NMUX": ("S ? !B : !A", lambda a, b, c, d: 1 - (b if c else a)),
    "AOI3": ("~((A & B) | C)", lambda a, b, c, d: 1 - ((a & b) | c)),
    "OAI3": ("~((A | B) & C)", lambda a, b, c, d: 1 - ((a | b) & c)),
    "AOI4": ("~((A & B) | (C & D))", lambda a, b, c, d: 1 - ((a & b) | (c & d))),
    "OAI4": ("~((A | B) & (C | D))", lambda a, b, c, d: 1 - ((a | b) & (c | d))),
}


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def verified_blob(source, filename):
    content = (source / filename).read_bytes()
    object_hash = sha1(f"blob {len(content)}\0".encode("ascii") + content).hexdigest()
    require(object_hash == BLOBS[filename], f"Git blob mismatch for {filename}")
    return content.decode("utf-8")


def signatures(transition, reward, triples):
    apply_transition = GATES[transition][1]
    apply_reward = GATES[reward][1]
    readings = []
    for context, first, second in triples:
        state = apply_transition(context, first, 0, 0)
        ports = (state, first, second, 0) if reward in ("MUX", "NMUX") else (
            state, second, context, first)
        readings.append((state, apply_reward(*ports)))
    return tuple(readings)


def run(source):
    content = verified_blob(source, "simcells.v")
    require(verified_blob(source, "COPYING").startswith("ISC License"), "License mismatch")
    modules = dict(re.findall(
        r"module\s+\\\$_([A-Z0-9]+)_\s*([^;]*;(?:(?!endmodule).)*)endmodule",
        content, re.DOTALL,
    ))
    for gate, (expected, _) in GATES.items():
        assignments = re.findall(r"assign Y = ([^;]+);", modules[gate])
        require(assignments == [expected], f"Unexpected source expression for {gate}")

    design = json.loads((HERE / "circuit-intake-design.json").read_bytes())
    triples = tuple(product((0, 1), repeat=3))
    labels = tuple("".join(map(str, triple)) for triple in triples)
    first, fit, recombined = zip(*design["circuits"], strict=True)
    require(len(first) == len(set(first)) == len(set(fit)) == 8 and set(recombined) == set(fit),
            "Unexpected circuit roster")
    menu = {(initial, last): signatures(initial, last, triples)
            for initial, last in product(first, fit)}
    selected = (*zip(first, fit, strict=True), *zip(first, recombined, strict=True))

    def identify(world, prefix):
        return [name for name, values in menu.items()
                if all(values[i] == menu[world][i] for i in prefix)]

    for size in range(len(triples) + 1):
        rosters = [prefix for prefix in combinations(range(len(triples)), size)
                   if all(identify(world, prefix) == [world] for world in selected)]
        if rosters:
            break
    actual_prefix = tuple(labels.index(label) for label in design["eval_prefix_triples"])
    require(actual_prefix in rosters and size == 6, "Staged probe roster is invalid")
    require(set(design["eval_scored_triples"]) == set(labels) - set(design["eval_prefix_triples"]),
            "Held prediction support overlaps the prefix")

    action_cases = []
    for i in range(0, len(triples), 2):
        prefix = tuple(j for j in range(len(triples)) if j not in (i, i + 1))
        supported = contrasts = guaranteed_contrasts = 0
        for world in zip(first, recombined, strict=True):
            compatible = identify(world, prefix)
            common = {0, 1}
            for name in compatible:
                values = [menu[name][j][1] for j in (i, i + 1)]
                common &= {action for action, value in enumerate(values) if value == max(values)}
            contrast = menu[world][i][1] != menu[world][i + 1][1]
            supported += bool(common)
            contrasts += contrast
            guaranteed_contrasts += contrast and len(common) == 1
        action_cases.append(dict(held=labels[i:i + 2], supported=supported,
                                 contrasts=contrasts, guaranteed_contrasts=guaranteed_contrasts))
    return dict(status="DESIGN_CHECK_PASS", gate_definitions=len(GATES), hypotheses=len(menu),
                minimal_common_prefix=size, minimal_prediction_rosters=len(rosters),
                candidate_action_cases=action_cases, source_actions=0, witnesses_admitted=0)


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))
