#!/usr/bin/env python3
"""F50 public source laws and three-step intervention inputs: no DEV outcomes.

Exact source-law deduplication uses Boolean algebraic normal form (ANF).
Over GF(2) with x*x=x, every Boolean function on 33 binary inputs has a
unique square-free multilinear polynomial. Equality of the canonical ANF
is exact over all 2**33 assignments, NOT a sampled probe or a hash test.
Target laws and sealed evaluator labels are deliberately absent here.
"""
from functools import lru_cache
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREREG = HERE / "f50_prereg.json"
PREREG_BLOB = "4bd3c4e0d3de0e3910094e38c14a0141c97ad380"
SCHEMA = "yggdrasil.qtr01.f50.law-conditioned-association-transfer.prereg.v1"
BANK_SIZES = (4096, 2048, 1024)
DEV_SEEDS = (4013, 4057, 4099)
RESERVED_SEEDS = (4127, 4159)
N_ACTION_BITS = 10
N_CONTEXT_BITS = 3
N_VARIABLES = 33  # current[10] + lag1[10] + lag2[10] + context[3]
TRAIN_EPISODES = 64
PUBLIC_QUERIES = 512
HELDOUT_QUERIES = 512
NOISE_BOUND = (1 << 64) // 10
MAX_ANF_PRODUCT_PAIRS = 100000
SOURCE_NS = "F50/source/v1"
TRAIN_NS = "F50/train/v1"
PUBLIC_NS = "F50/public-candidates/v1"
EVAL_NS = "F50/evaluator-only/v1"
NOISE_NS = "F50/noisy-public/v1"


class F50Rejected(ValueError):
    """Protocol drift, unproven equivalence, replay or invalid input."""


def freeze(path=PREREG):
    raw = Path(path).read_bytes()
    actual = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if actual != PREREG_BLOB:
        raise F50Rejected("F50_PREREG_BLOB_DRIFT")
    p = json.loads(raw)
    task = p.get("task", {})
    if (p.get("schema") != SCHEMA
        or p.get("status") != "FROZEN_PRE_CODE_PRE_NEW_DEVELOPMENT_WORLD_FIRST_USE"
        or p.get("source_parent") != "8ade5259a9cb8cac5137198806bc23ffe11bf4a5"
        or task.get("source_bank_sizes_high_first") != list(BANK_SIZES)
        or task.get("development_seeds") != list(DEV_SEEDS)
        or task.get("reserved_no_first_use_seeds") != list(RESERVED_SEEDS)
        or task.get("development_worlds") != 9
        or task.get("public_candidates_per_world") != PUBLIC_QUERIES
        or task.get("evaluator_only_heldout_trajectories_per_world") != HELDOUT_QUERIES
        or task.get("queries_per_arm") != [16, 32, 64]
        or p.get("frozen_metrics", {}).get("requirements", {}).get(
            "all_new_target_outside_public_source_bank_exact_symbolic") is not True
        or p.get("custody", {}).get("no_target_first_use_until_exact_source_full_ubuntu_windows_regressions") is not True
        or p.get("custody", {}).get("no_accepted_weights_changed") is not True):
        raise F50Rejected("F50_FROZEN_CONTRACT_DRIFT")
    return p


def digest(namespace, *parts):
    return sha256("|".join((namespace, *map(str, parts))).encode("ascii")).digest()


def random_uint(namespace, *parts):
    return int.from_bytes(digest(namespace, *parts)[:8], "big")


def leaf(index):
    if type(index) is not int or not 0 <= index < N_VARIABLES:
        raise F50Rejected("F50_INVALID_LEAF")
    return ("leaf", index)


def _as_ast(ast):
    if type(ast) is not tuple or not ast:
        raise F50Rejected("F50_INVALID_AST")
    op = ast[0]
    if op == "leaf" and len(ast) == 2:
        leaf(ast[1])
        return ast
    if op == "not" and len(ast) == 2:
        _as_ast(ast[1])
        return ast
    if op in ("and", "or", "xor") and len(ast) == 3:
        _as_ast(ast[1])
        _as_ast(ast[2])
        return ast
    raise F50Rejected("F50_INVALID_AST")


def ast_depth(ast):
    ast = _as_ast(ast)
    if ast[0] == "leaf":
        return 0
    return 1 + max(ast_depth(ch) for ch in ast[1:])


def _xor(a, b):
    return a.symmetric_difference(b)


def _and(a, b):
    if len(a) * len(b) > MAX_ANF_PRODUCT_PAIRS:
        raise F50Rejected("F50_EXACT_EQUIVALENCE_RESOURCE_STOP")
    result = set()
    for i in a:
        for j in b:
            item = i | j  # Boolean x_i^2=x_i: square-free monomial
            if item in result:
                result.remove(item)
            else:
                result.add(item)
    return frozenset(result)


@lru_cache(maxsize=12000)
def anf(ast):
    """Unique exact GF(2) algebraic normal form, no sample or approximation."""
    _as_ast(ast)
    op = ast[0]
    if op == "leaf":
        return frozenset((1 << ast[1],))
    if op == "not":
        return _xor(anf(ast[1]), frozenset((0,)))
    x, y = anf(ast[1]), anf(ast[2])
    if op == "xor":
        return _xor(x, y)
    product = _and(x, y)
    if op == "and":
        return product
    if op == "or":
        return _xor(_xor(x, y), product)
    raise F50Rejected("F50_INVALID_AST")


def dependencies(ast):
    out = set()
    for mask in anf(ast):
        for bit in range(N_VARIABLES):
            if mask & (1 << bit):
                out.add(bit)
    return frozenset(out)


def exact_signature(ast):
    terms = sorted(anf(ast))
    body = len(terms).to_bytes(8, "big")
    body += b"".join(term.to_bytes(5, "big") for term in terms)
    return sha256(b"F50/canonical-ANF/v1\0" + body).hexdigest()


def exact_equal(left, right):
    return anf(left) == anf(right)


def evaluate(ast, current, lag1, lag2, context):
    for action in (current, lag1, lag2):
        if type(action) is not int or not 0 <= action < (1 << N_ACTION_BITS):
            raise F50Rejected("F50_INVALID_ACTION")
    if type(context) is not int or not 0 <= context < (1 << N_CONTEXT_BITS):
        raise F50Rejected("F50_INVALID_CONTEXT")
    _as_ast(ast)
    masks = current | (lag1 << 10) | (lag2 << 20) | (context << 30)
    value = 0
    for monomial in anf(ast):
        value ^= int((masks & monomial) == monomial)
    return value


def _check_bank_size(size):
    if type(size) is not int or size not in BANK_SIZES:
        raise F50Rejected("F50_UNREGISTERED_SOURCE_BANK")
    return size


def _check_dev_seed(seed):
    if type(seed) is not int or seed not in DEV_SEEDS:
        raise F50Rejected("F50_RESERVED_OR_UNREGISTERED_SEED")
    return seed


def proposed_source(size, index, attempt):
    _check_bank_size(size)
    if (type(index) is not int or not 0 <= index < size
        or type(attempt) is not int or not 0 <= attempt < 256):
        raise F50Rejected("F50_SOURCE_PROPOSAL_SCOPE")
    b = digest(SOURCE_NS, size, index, attempt)
    i, j, k, m = [b[pos] % N_VARIABLES for pos in range(4)]
    first = ("and", "or", "xor")[b[4] % 3]
    second = ("and", "or", "xor")[b[5] % 3]
    third = ("and", "or", "xor")[b[6] % 3]
    a, c, d, e = leaf(i), leaf(j), leaf(k), leaf(m)
    left = (first, a, c)
    right = (second, d, e)
    form = b[7] % 6
    if form == 0:
        return (third, left, right)
    if form == 1:
        return (third, ("not", left), right)
    if form == 2:
        return (third, left, ("not", right))
    if form == 3:
        return ("not", (third, left, right))
    if form == 4:
        return (third, left, ("and", leaf(30 + b[8] % 3), right))
    return (third, ("xor", a, leaf(20 + b[9] % 10)), ("and", c, d))


@lru_cache(maxsize=3)
def source_bank(size):
    """Every source law has a distinct EXACT function across the whole cube."""
    _check_bank_size(size)
    freeze()
    output = []
    seen = set()
    for index in range(size):
        for attempt in range(256):
            candidate = proposed_source(size, index, attempt)
            if ast_depth(candidate) > 3:
                continue
            identity = anf(candidate)  # exact equality, not SHA-only
            if identity in seen or len(dependencies(candidate)) < 2:
                continue
            seen.add(identity)
            output.append(candidate)
            break
        else:
            raise F50Rejected("F50_SOURCE_EXACT_BANK_EXHAUSTED")
    if len(output) != size or len(seen) != size:
        raise F50Rejected("F50_SOURCE_BANK_INVALID")
    return tuple(output)


def source_bank_admission(size):
    bank = source_bank(size)
    identities = set(map(anf, bank))
    if len(identities) != size or any(ast_depth(x) > 3 for x in bank):
        raise F50Rejected("F50_EXACT_SOURCE_ADMISSION_FAILED")
    stream = sha256()
    for node in bank:
        stream.update(bytes.fromhex(exact_signature(node)))
    return {"size": size, "distinct_full_function_laws": len(identities),
            "canonical_exact_method": "square_free_boolean_ANF_GF2_33_vars",
            "source_identity_stream_sha256": stream.hexdigest(),
            "target_outcomes_consumed": 0, "scientific_pass": False}


@lru_cache(maxsize=3)
def source_split(size):
    _check_bank_size(size)
    ids = tuple(range(size))
    ordered = tuple(sorted(ids, key=lambda i: (digest("F50/source-law-split/v1", size, i), i)))
    n_fit = size * 4 // 5
    fit = frozenset(ordered[:n_fit])
    val = frozenset(ordered[n_fit:])
    if len(fit) != n_fit or len(val) != size - n_fit or fit & val or fit | val != set(ids):
        raise F50Rejected("F50_SOURCE_FIT_VALIDATION_LEAKAGE")
    return fit, val


def _trajectory(namespace, size, seed, law, index, nonce):
    b = digest(namespace, size, seed, law, index, nonce)
    actions = tuple((int.from_bytes(b[j:j+2], "big") & 1023) for j in (0, 2, 4))
    context = b[6] & 7
    if (len(set(actions)) != 3 or any(not 3 <= x.bit_count() <= 7 for x in actions)):
        return None
    return (*actions, context)


def validate_trajectory(episode):
    if (type(episode) not in (tuple, list) or len(episode) != 4
        or any(type(x) is not int for x in episode)
        or not all(0 < x < 1024 for x in episode[:3])
        or not 0 <= episode[3] < 8):
        raise F50Rejected("F50_INVALID_EPISODE")
    if len(set(episode[:3])) != 3 or any(not 3 <= x.bit_count() <= 7 for x in episode[:3]):
        raise F50Rejected("F50_NONINTERVENTIONAL_OR_DUPLICATE_ACTIONS")
    return tuple(episode)


def _episode_truth(ast, episode):
    """Source-law only: evaluator target ASTs are not available in this module."""
    a, b, c, ctx = validate_trajectory(episode)
    return (evaluate(ast, a, 0, 0, ctx),
            evaluate(ast, b, a, 0, ctx),
            evaluate(ast, c, b, a, ctx))


def _noise_bit(size, law_index, row_index, step):
    return int(random_uint(NOISE_NS, "source", size, law_index,
                           row_index, step, 0) < NOISE_BOUND)


@lru_cache(maxsize=1)
def _source_trajectory_registry(size):
    _check_bank_size(size)
    occupied, rows = set(), []
    for law_index in range(size):
        row = []
        for index in range(TRAIN_EPISODES):
            for nonce in range(1024):
                episode = _trajectory(TRAIN_NS, size, 0, law_index, index, nonce)
                if episode is not None and episode not in occupied:
                    occupied.add(episode)
                    row.append(episode)
                    break
            else:
                raise F50Rejected("F50_SOURCE_EPISODE_SPACE_EXHAUSTED")
        rows.append(tuple(row))
    if len(occupied) != size * TRAIN_EPISODES:
        raise F50Rejected("F50_SOURCE_EPISODE_REPLAY")
    return tuple(rows), frozenset(occupied)


def source_training_row(size, law_index, *, validation=False):
    _check_bank_size(size)
    if type(law_index) is not int or not 0 <= law_index < size or type(validation) is not bool:
        raise F50Rejected("F50_INVALID_SOURCE_ROW")
    fit, val = source_split(size)
    permitted = val if validation else fit
    if law_index not in permitted:
        raise F50Rejected("F50_TRAIN_VALIDATION_LAW_SPLIT_FENCE")
    bank = source_bank(size)
    rows = _source_trajectory_registry(size)[0][law_index]
    return tuple((episode, tuple(y ^ _noise_bit(size, law_index, i, step)
                                 for step, y in enumerate(_episode_truth(bank[law_index], episode))))
                 for i, episode in enumerate(rows))


def fit_source_laws(size):
    """Lossless public FIT source DAGs, without access to VALIDATION laws."""
    fit, _ = source_split(size)
    bank = source_bank(size)
    return tuple((i, bank[i]) for i in sorted(fit))


def validation_source_laws_for_pretrain_only(size):
    """Reserved solely for conventional TRAIN-source early stopping."""
    _, val = source_split(size)
    bank = source_bank(size)
    return tuple((i, bank[i]) for i in sorted(val))


@lru_cache(maxsize=9)
def public_candidate_pool(size, seed):
    _check_bank_size(size)
    _check_dev_seed(seed)
    _, occupied = _source_trajectory_registry(size)
    seen = set(occupied)
    candidates = []
    for index in range(PUBLIC_QUERIES):
        for nonce in range(1024):
            episode = _trajectory(PUBLIC_NS, size, seed, 0, index, nonce)
            if episode is not None and episode not in seen:
                seen.add(episode)
                candidates.append(episode)
                break
        else:
            raise F50Rejected("F50_PUBLIC_CANDIDATE_SPACE_EXHAUSTED")
    return tuple(candidates)


def sealed_heldout_inputs_for_evaluator_only(size, seed):
    """No labels returned. Never export these inputs to native arms."""
    _check_dev_seed(seed)
    pool = public_candidate_pool(size, seed)
    occupied = set(_source_trajectory_registry(size)[1])
    occupied.update(pool)
    result = []
    for index in range(HELDOUT_QUERIES):
        for nonce in range(1024):
            episode = _trajectory(EVAL_NS, size, seed, 0, index, nonce)
            if episode is not None and episode not in occupied:
                occupied.add(episode)
                result.append(episode)
                break
        else:
            raise F50Rejected("F50_SEALED_EPISODE_SPACE_EXHAUSTED")
    return tuple(result)


def check_fixture_novelty(size, candidate):
    """TEST-ONLY exact target-like novelty, not any F50 DEV target first-use."""
    _check_bank_size(size)
    if ast_depth(candidate) < 4 or ast_depth(candidate) > 6:
        raise F50Rejected("F50_TARGET_FIXTURE_DEPTH_INVALID")
    target_terms = anf(candidate)
    bank = source_bank(size)
    if target_terms in set(map(anf, bank)):
        raise F50Rejected("F50_TARGET_EXACT_SOURCE_COLLISION")
    deps = dependencies(candidate)
    actions = {i % 10 for i in deps if i < 30}
    if (len(actions) < 3 or not any(30 <= x < 33 for x in deps)
        or not any(10 <= x < 30 for x in deps)
        or not any(any((m & (m - 1)) for m in target_terms) for _ in (0,))):
        raise F50Rejected("F50_TARGET_NO_CAUSAL_COMPOSITION")
    return {"source_laws": size, "exact_nonmembership": True,
            "action_dependencies": len(actions),
            "has_context": True, "has_delayed_cause": True,
            "target_outcomes_consumed": 0, "scientific_pass": False}


if __name__ == "__main__":
    freeze()
    print("F50_SOURCE_WORLD_CONSTRUCTION_READY_NO_DEV_TARGET_FIRST_USE")
