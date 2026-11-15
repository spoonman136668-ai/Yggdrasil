#!/usr/bin/env python3
"""F49 frozen causal-world construction and admission only (no target observations).

Public arms receive source rows and public candidate trajectories. Evaluator-only
target laws and withheld test trajectories must never be delivered to learners.
No target intervention, learner fitting, performance scoring, or promotion here.
"""
from functools import lru_cache
from hashlib import sha1, sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
PREREG = HERE / "f49_prereg.json"
FROZEN_BLOB = "839309211feef018d1c308091716bc6e0d4e7a70"
SCHEMA = "yggdrasil.qtr01.f49.out-of-bank-causal-composition-dev.v1"
BANK_SIZES = (1024, 512, 256)
SEEDS = (163, 167, 173)
CANONICAL_BITS = 1 << 18
BITSET_BYTES = CANONICAL_BITS // 8
FULL = (1 << CANONICAL_BITS) - 1
LEAVES = 18
N_TRAIN = 64
N_PUBLIC = 256
N_EVAL = 256
NOISE_BOUND = (1 << 64) // 10


class F49Rejected(ValueError):
    """Invalid world, unregistered scope, or frozen protocol drift."""


def freeze(path=PREREG):
    raw = Path(path).read_bytes()
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != FROZEN_BLOB:
        raise F49Rejected("F49_FROZEN_PREREG_BLOB_CHANGED")
    p = json.loads(raw)
    task = p.get("task", {})
    if (p.get("schema") != SCHEMA
        or p.get("status") != "FROZEN_PRE_F49_IMPLEMENTATION_WORLD_GENERATION_AND_RESULTS"
        or p.get("source_parent") != "440518db7e4adc855841fe555c179db89f304b6c"
        or task.get("source_bank_sizes_high_first") != list(BANK_SIZES)
        or task.get("development_seeds") != list(SEEDS)
        or task.get("worlds_total") != 9
        or task.get("reserved_unopened") is None
        or p.get("custody", {}).get("first_use") is None
        or p.get("prereg_metrics", {}).get("requirements", {}).get("novel_target_functionally_outside_source_bank_all") is not True
        or not all(v is True for v in p.get("safety", {}).values())):
        raise F49Rejected("F49_FROZEN_POLICY_DRIFT")
    return p


def digest(*parts):
    return sha256("|".join(map(str, parts)).encode("ascii")).digest()


def random_uint(namespace, *parts):
    return int.from_bytes(digest(namespace, *parts)[:8], "big")


def leaf(i):
    if type(i) is not int or not 0 <= i < LEAVES:
        raise F49Rejected("F49_INVALID_LEAF")
    return ("leaf", i)


def ast_depth(ast):
    op = ast[0]
    if op == "leaf" and len(ast) == 2:
        leaf(ast[1])
        return 0
    if op == "not" and len(ast) == 2:
        child = ast_depth(ast[1])
        return 0 if child == 0 else child + 1
    if op in ("and", "or", "xor") and len(ast) == 3:
        return 1 + max(ast_depth(ast[1]), ast_depth(ast[2]))
    raise F49Rejected("F49_UNSUPPORTED_AST")


def evaluate(ast, a, previous, context):
    if (type(a) is not int or not 0 <= a < 256
        or type(previous) is not int or not 0 <= previous < 256
        or type(context) is not int or not 0 <= context < 4):
        raise F49Rejected("F49_INVALID_INPUT")
    if ast_depth(ast) > 4:
        raise F49Rejected("F49_AST_DEPTH_EXCEEDED")
    def go(node):
        op = node[0]
        if op == "leaf":
            i = node[1]
            return ((a >> i) & 1 if i < 8 else
                    (previous >> (i-8)) & 1 if i < 16 else
                    (context >> (i-16)) & 1)
        if op == "not":
            return go(node[1]) ^ 1
        x, y = go(node[1]), go(node[2])
        if op == "and": return x & y
        if op == "or": return x | y
        if op == "xor": return x ^ y
        raise F49Rejected("F49_UNSUPPORTED_AST")
    return go(ast)


@lru_cache(maxsize=1)
def canonical_leaf_masks():
    """Exhaustive 18-bit Boolean domain: 262144 assignments, not a sampled probe."""
    masks = []
    for bit in range(LEAVES):
        half = 1 << bit
        if bit < 3:
            one_byte = sum(1 << j for j in range(8) if (j >> bit) & 1)
            data = bytes((one_byte,)) * BITSET_BYTES
        else:
            block = (b"\0" * (half // 8) + b"\xff" * (half // 8))
            data = block * (BITSET_BYTES // len(block))
        masks.append(int.from_bytes(data, "little"))
    return tuple(masks)


def truth_bits(ast):
    masks = canonical_leaf_masks()
    def go(node):
        op = node[0]
        if op == "leaf": return masks[leaf(node[1])[1]]
        if op == "not": return FULL ^ go(node[1])
        x, y = go(node[1]), go(node[2])
        if op == "and": return x & y
        if op == "or": return x | y
        if op == "xor": return x ^ y
        raise F49Rejected("F49_UNSUPPORTED_AST")
    return go(ast)


def signature(ast):
    return sha256(truth_bits(ast).to_bytes(BITSET_BYTES, "little")).hexdigest()


def proposed_source(size, index, attempt):
    """Deterministic depth <= 2 grammar proposals with full-domain dedup."""
    b = digest("F49/source/v1", size, index, attempt)
    i, j, k, m = (b[x] % LEAVES for x in range(4))
    ops = ("and", "or", "xor")
    left = (ops[b[4] % 3], leaf(i), leaf(j))
    right = (ops[b[5] % 3], leaf(k), leaf(m))
    form = b[6] % 5
    if form == 0: return (ops[b[7] % 3], left, right)
    if form == 1: return (ops[b[7] % 3], left, leaf(k))
    if form == 2: return (ops[b[7] % 3], leaf(i), right)
    if form == 3: return ("not", left)
    return (ops[b[7] % 3], leaf(i), leaf(j))


@lru_cache(maxsize=3)
def source_bank(size):
    if type(size) is not int or size not in BANK_SIZES:
        raise F49Rejected("F49_BANK_NOT_REGISTERED")
    output, seen = [], set()
    for i in range(size):
        for attempt in range(10000):
            ast = proposed_source(size, i, attempt)
            sig = signature(ast)
            if sig not in seen:
                seen.add(sig)
                output.append(ast)
                break
        else:
            raise F49Rejected("F49_SOURCE_BANK_EXHAUSTED")
    return tuple(output)


def target_ast(size, seed):
    """Evaluator-only generation, never to be returned through public arm APIs."""
    if type(size) is not int or size not in BANK_SIZES or type(seed) is not int or seed not in SEEDS:
        raise F49Rejected("F49_PROTECTED_OR_UNREGISTERED_WORLD")
    indices, counter = [], 0
    while len(indices) < 5:
        i = random_uint("F49/target/v1", size, seed, counter) % 8
        counter += 1
        if i not in indices:
            indices.append(i)
    i, j, k, l, m = indices
    signs = [random_uint("F49/target/v1", size, seed, "sign", pos) & 1
             for pos in range(5)]
    def signed(bit, polarity):
        value = leaf(bit)
        return ("not", value) if polarity else value
    current = {bit: signed(bit, signs[pos]) for pos, bit in enumerate(indices)}
    previous = {bit: signed(bit+8, signs[pos]) for pos, bit in enumerate(indices)}
    c = lambda x: leaf(16+x)
    xor = lambda x,y: ("xor",x,y)
    AND = lambda x,y: ("and",x,y)
    OR = lambda x,y: ("or",x,y)
    NOT = lambda x: ("not",x)
    if seed == 163:
        return xor(AND(current[i], xor(current[j],current[k])), AND(c(0),current[l]))
    if seed == 167:
        return xor(AND(current[i],previous[j]), xor(current[k],c(1)))
    return xor(OR(AND(c(0),xor(current[i],current[j])),
                  AND(NOT(c(0)),AND(current[k],current[l]))),
               AND(c(1),previous[m]))


def check_target_admission(size, seed):
    """Complete evaluator-only novelty/interaction proof; no public outcome."""
    bank = source_bank(size)
    target = target_ast(size, seed)
    if len(bank) != size or max(map(ast_depth,bank)) > 2 or ast_depth(target) > 4:
        raise F49Rejected("F49_BANK_OR_TARGET_SHAPE_INVALID")
    tgt = signature(target)
    bank_sigs = [signature(ast) for ast in bank]
    if len(set(bank_sigs)) != size or tgt in bank_sigs:
        raise F49Rejected("F49_TASK_INVALID_SOURCE_COLLISION")
    probe_bit = 16 if seed in (163, 173) else (
        target[1][2][1][1] if target[1][2][0] == "not" else target[1][2][1])
    v = truth_bits(target)
    mask_zero = FULL ^ canonical_leaf_masks()[probe_bit]
    if not ((v ^ (v >> (1 << probe_bit))) & mask_zero):
        raise F49Rejected("F49_TASK_INVALID_NO_CAUSAL_CONTRAST")
    interaction = False
    masks = canonical_leaf_masks()
    for i in range(8):
        for j in range(i+1, LEAVES):
            zi, zj = 1 << i, 1 << j
            zero = FULL ^ (masks[i] | masks[j])
            if (v ^ (v >> zi) ^ (v >> zj) ^ (v >> (zi+zj))) & zero:
                interaction = True
                break
        if interaction:
            break
    if not interaction:
        raise F49Rejected("F49_TASK_INVALID_ONEHOT_DIRECT_CODE")
    return {"source_bank_size": size, "development_seed": seed,
            "source_unique_full_domain": True, "target_out_of_bank_full_domain": True,
            "target_function_digest_evaluator_only": tgt}


def trajectory(namespace, size, seed, law_index, index, nonce=0):
    b = digest(namespace, size, seed, law_index, index, nonce)
    a0, a1, ctx = b[0], b[1], b[2] & 3
    return (a0,a1,ctx) if a0 and a1 and a0 != a1 else None


@lru_cache(maxsize=3)
def training_inputs(size):
    bank = source_bank(size)
    output, occupied = [], set()
    for i in range(len(bank)):
        row = []
        for j in range(N_TRAIN):
            for nonce in range(10000):
                tr = trajectory("F49/train/v1",size,0,i,j,nonce)
                if tr is not None and tr not in occupied:
                    occupied.add(tr)
                    row.append(tr)
                    break
            else:
                raise F49Rejected("F49_TRAIN_POOL_EXHAUSTED")
        output.append(tuple(row))
    return tuple(output)


def _trajectories_for_world(size, seed):
    if type(size) is not int or size not in BANK_SIZES or type(seed) is not int or seed not in SEEDS:
        raise F49Rejected("F49_PROTECTED_OR_UNREGISTERED_WORLD")
    occupied = {x for row in training_inputs(size) for x in row}
    output = []
    for namespace, n in (("F49/queries/v1",N_PUBLIC),("F49/eval/v1",N_EVAL)):
        arr = []
        for index in range(n):
            for nonce in range(10000):
                tr = trajectory(namespace,size,seed,0,index,nonce)
                if tr is not None and tr not in occupied:
                    occupied.add(tr)
                    arr.append(tr)
                    break
            else:
                raise F49Rejected("F49_TRAJECTORY_POOL_EXHAUSTED")
        output.append(tuple(arr))
    return tuple(output)


def public_query_pool(size, seed):
    """Public inputs only; no evaluator-only trajectory returned."""
    return _trajectories_for_world(size, seed)[0]


def source_training_row(size, law_index):
    """All arms get the same public source sequences and independent 10% flips."""
    bank = source_bank(size)
    if type(law_index) is not int or not 0 <= law_index < len(bank):
        raise F49Rejected("F49_INVALID_SOURCE_LAW_INDEX")
    ast, result = bank[law_index], []
    for j,(a0,a1,ctx) in enumerate(training_inputs(size)[law_index]):
        y0 = evaluate(ast,a0,0,ctx)
        y1 = evaluate(ast,a1,a0,ctx)
        y0 ^= int(random_uint("F49/obs/v1",size,law_index,j,0,0) < NOISE_BOUND)
        y1 ^= int(random_uint("F49/obs/v1",size,law_index,j,1,0) < NOISE_BOUND)
        result.append(((a0,a1,ctx),(y0,y1)))
    return tuple(result)


def preflight_world(size, seed):
    freeze()
    admission = check_target_admission(size,seed)
    public,evaluation = _trajectories_for_world(size,seed)
    if len(public) != N_PUBLIC or len(evaluation) != N_EVAL:
        raise F49Rejected("F49_MISSING_TRAJECTORIES")
    return {"status":"F49_WORLD_ADMISSION_ONLY_NO_TARGET_OBSERVATIONS",
            "size":size,"seed":seed,"source_training_trajectories":size*N_TRAIN,
            "public_candidate_trajectories":len(public),
            "sealed_evaluator_trajectories":len(evaluation),
            "full_domain_source_unique":admission["source_unique_full_domain"],
            "target_out_of_source_bank":admission["target_out_of_bank_full_domain"],
            "scientific_pass":False,"accepted_weights_modified":False}


if __name__ == "__main__":
    freeze()
    print("F49_FROZEN_WORLD_CONSTRUCTION_MODULE_READY_NO_OUTCOMES")
