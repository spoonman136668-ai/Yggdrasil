"""NCI-ID-A1: source-cached input-only identifiability diagnostic.

Never imports source generators or calls original do/reset. Reports structural
support under generic GF(2) degree4/5 classes, without reading held outcomes.
"""
import argparse
import json
import subprocess
from pathlib import Path
from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest, feature_row
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_prior_hypothesis import input_order

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SEEDS = (101, 202, 303)
SLOTS = (0, 1, 2, 3, 12, 13, 14, 15)
BUDGETS = (384, 512)
DEGREES = (4, 5)
MAX_PROPOSALS = 32

def require(ok, reason):
    if not ok:
        raise ValueError("NCI_ID_A1_" + reason)

def rank_state(rows, degree):
    """Independent label-blind bit elimination over input feature support."""
    basis = {}
    for mask in rows:
        require(type(mask) is int and 0 <= mask < 2048, "INPUT_MASK")
        value = feature_row(mask, degree)
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return basis

def extend_basis(basis, mask, degree):
    """Mutable local rank accounting; no outcome is ever accepted."""
    value = feature_row(mask, degree)
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = value
            return True
        value ^= basis[pivot]
    return False

def proposed_inputs(observed, degree=5, limit=MAX_PROPOSALS):
    require(type(observed) in (tuple, list) and len(set(observed)) == len(observed)
            and 0 <= limit <= 32, "PROPOSAL_INPUTS")
    basis = rank_state(observed, degree)
    start = len(basis)
    held = sorted(set(range(2048)).difference(observed), key=input_order)
    selected = []
    for mask in held:
        if extend_basis(basis, mask, degree):
            selected.append(mask)
        if len(selected) == limit:
            break
    return {'masks': selected, 'starting_rank': start, 'ending_rank': len(basis),
            'potential_rank_gain': len(basis) - start,
            'masks_sha256': digest(canonical(selected)),
            'action_performed': False, 'outcome_accessed': False}

def fit_from_witnesses(rows, held, degree, budget):
    require(len(rows) == 512 and len(held) == 1536 and budget in BUDGETS
            and degree in DEGREES, "BUDGET")
    training = rows[:budget]
    observed = [c | (a << 10) for c, a, _ in training]
    rank = len(rank_state(observed, degree))
    feature_count = sum(__import__('math').comb(11, d) for d in range(degree + 1))
    require(rank <= budget and rank <= feature_count, "RANK_UPPER_BOUND")
    try:
        model = NativeContextBasis(10).stage_fit(
            0, training, digest(canonical(training)), max_degree=degree)
    except ValueError as exc:
        if str(exc) != 'CKAD_NATIVE_MODEL_CLASS_INADEQUATE':
            raise
        return {'degree': degree, 'budget': budget, 'consistent': False,
                'rank': rank, 'feature_count': feature_count,
                'rank_deficit': feature_count - rank,
                'unseen_identified': 0, 'unseen_abstained': 1536}
    info = model.profile_info(0)
    require(info['rank'] == rank and info['feature_count'] == feature_count
            and info['source_records'] == budget
            and info['source_sha256'] == digest(canonical(training)),
            "NATIVE_RANK_PARITY")
    identified = sum(model.predict(0, m & 1023, m >> 10) is not None for m in held)
    require(0 <= identified <= 1536, "HELD_COUNT")
    return {'degree': degree, 'budget': budget, 'consistent': True,
            'rank': rank, 'feature_count': feature_count,
            'rank_deficit': feature_count - rank,
            'unseen_identified': identified, 'unseen_abstained': 1536 - identified}

def run():
    previous = json.loads((ROOT/'research/contrib/chatgpt/CKAD-08/result.json').read_text())
    twelve = json.loads((ROOT/'research/contrib/chatgpt/CKAD-12/result.json').read_text())
    parents = {c['seed']: c for c in previous['cases']}
    view_pins = {(c['seed'], c['slot']): c for c in twelve['cases']
                 if c['recipe'] == 'WIDE' and c['condition'] == 'REAL'
                 and c['exposure'] == 512}
    require(set(parents) == set(SEEDS), "PARENT_SEEDS")
    require(len(view_pins) == 48, "QUALIFIED_VIEW_COUNT")
    cases = []
    for seed in SEEDS:
        case = parents[seed]
        path = ROOT/'research/contrib/chatgpt/CKAD-08'/case['checkpoint_name']
        raw = path.read_bytes()
        require(digest(raw) == case['checkpoint_sha256'], "PARENT_PIN")
        source = NativeContextQuarantine.restore(raw, digest(raw))
        for slot in SLOTS:
            require(not source._failures[slot], "QUARANTINED")
            seen = source._native._seen[slot]
            require(type(seen) is int and seen.bit_count() == 512, "WITNESSED_COUNT")
            masks = sorted((m for m in range(2048) if seen & (1 << m)), key=input_order)
            addr, retained = (slot, False) if slot < 7 else (slot - 7, True)
            rows = [[m & 1023, m >> 10, source.predict(addr, m & 1023, m >> 10,
                     retained=retained)] for m in masks]
            require(len(rows) == 512 and all(type(row[2]) is int
                    and row[2] in (0,1) for row in rows), "SOURCE_WITNESSES")
            pin = view_pins[seed, slot]
            require(digest(canonical(rows)) == pin['view_rows_sha256']
                    and digest(raw) == pin['source_checkpoint_sha256'],
                    "CKAD12_WITNESS_BINDING")
            held = [m for m in range(2048) if not (seen & (1 << m))]
            require(len(held) == 1536, "UNWITNESSED_MASK_SET")
            fits = [fit_from_witnesses(rows, held, degree, budget)
                    for budget in BUDGETS for degree in DEGREES]
            proposals = proposed_inputs(masks)
            require(not set(proposals['masks']).intersection(masks)
                    and proposals['potential_rank_gain'] == len(proposals['masks'])
                    and not proposals['action_performed']
                    and not proposals['outcome_accessed'], "PROPOSAL_LEAK_OR_DRIFT")
            cases.append({'seed': seed, 'slot': slot,
                'source_checkpoint_sha256': digest(raw),
                'witness_rows_sha256': digest(canonical(rows)),
                'witnesses': 512, 'unobserved_input_masks': 1536,
                'fits': fits, 'proposed_inputs_only': proposals})
        require(source.checkpoint() == raw, "PARENT_MUTATED")
    require(len(cases) == 24 and sum(len(c['fits']) for c in cases) == 96,
            "TRIAL_COUNT")
    def sumfit(budget, degree, key, consistent_only=False):
        return sum(f[key] for c in cases for f in c['fits']
                   if f['budget'] == budget and f['degree'] == degree
                   and (not consistent_only or f['consistent']))
    result = {'schema': 'yggdrasil.nci-identifiability-a1.result.v1',
        'classification': 'STRUCTURAL_IDENTIFIABILITY_DIAGNOSTIC_ONLY',
        'scientific_pass': False, 'accepted_native': False,
        'new_original_source_actions': 0, 'new_worlds': 0,
        'original_source_generators_called': 0, 'held_outcome_reads': 0,
        'case_count': len(cases), 'fit_count': 96,
        'models': [{'budget': n, 'degree': d,
                    'consistent_cases': sum(f['consistent'] for c in cases for f in c['fits']
                                      if f['budget'] == n and f['degree'] == d),
                    'unseen_identified': sumfit(n, d, 'unseen_identified'),
                    'rank_deficit_sum': sumfit(n, d, 'rank_deficit')}
                   for n in BUDGETS for d in DEGREES],
        'proposal_count': sum(len(c['proposed_inputs_only']['masks']) for c in cases),
        'potential_rank_gain_sum': sum(c['proposed_inputs_only']['potential_rank_gain'] for c in cases),
        'cases': cases}
    return result

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--expected-sha256')
    args = ap.parse_args()
    result = run()
    stable = digest(canonical(result))
    if args.expected_sha256:
        require(stable == args.expected_sha256, "WINDOWS_STABLE_DRIFT")
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical({'result': result, 'stable_sha256': stable}))
    print("NCI_ID_A1_STABLE_SHA256=" + stable, flush=True)
    print("NCI_ID_A1_MODELS=" + canonical(result['models']).decode('ascii'), flush=True)
    print("NCI_ID_A1_PROPOSED_INPUTS_NO_ACTIONS=" + str(result['proposal_count']), flush=True)
    import os
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            fh.write('stable=' + stable + '\n')
