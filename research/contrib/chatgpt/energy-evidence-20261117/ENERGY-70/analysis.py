#!/usr/bin/env python3
"""ENERGY-70: exact capacity-bound proof and read-only ENERGY-69 receipt diagnosis.
Retrospective analytical evidence only; no seeds, fitting, or native training.
"""
import base64
import csv
import hashlib
import io
import itertools
import json
import tarfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'ENERGY-69'


def archive():
    manifest = json.loads((PARENT / 'archive_manifest.json').read_text('utf-8'))
    parts = []
    for p in manifest['parts']:
        raw = (PARENT / p['name']).read_bytes()
        assert len(raw) == p['bytes']
        assert hashlib.sha256(raw).hexdigest() == p['sha256']
        parts.append(raw)
    encoded = b''.join(parts)
    assert len(encoded) == manifest['base64_bytes']
    binary = base64.b64decode(encoded, validate=True)
    assert len(binary) == manifest['archive_bytes']
    assert hashlib.sha256(binary).hexdigest() == manifest['archive_sha256']
    return tarfile.open(fileobj=io.BytesIO(binary), mode='r:xz')


def character(x, indices):
    product = 1
    for i in indices:
        product *= x[i]
    return product


def proof():
    assignments = list(itertools.product((-1, 1), repeat=9))
    target = tuple(range(5))
    low_basis = [support for degree in range(5)
                 for support in itertools.combinations(range(9), degree)]
    assert len(assignments) == 512 and len(low_basis) == 256
    for support in low_basis:
        assert sum(character(x, target) * character(x, support)
                   for x in assignments) == 0
    residual = sum((Fraction(9, 20) * character(x, target)) ** 2
                   for x in assignments) / len(assignments)
    assert residual == Fraction(81, 400)
    noise_variance = Fraction(9, 100)
    return {'assignments': 512, 'low_order_basis_terms': 256,
            'all_inner_products_exact_zero': True,
            'irreducible_fifth_order_mse': str(residual),
            'observed_mse_floor_fourth_only': str(residual + noise_variance),
            'observed_mse_floor_fifth_available': str(noise_variance),
            'scope': 'linear Walsh span of order 0..4, uniform nine-bit interventions'}


def diagnose():
    with archive() as tar:
        original = json.loads(tar.extractfile('screen/result.json').read())
        rows = list(csv.DictReader(io.StringIO(
            tar.extractfile('screen/cases.csv').read().decode('utf-8'))))
    assert len(rows) == original['cases'] == 72
    assert original['screen_decision'] == 'DEVELOPMENT_NO_GO'
    families = original['families']
    by_family = {}
    for name in families:
        subset = [row for row in rows if row['family'] == name]
        assert len(subset) == 18
        diffs = [float(x['block4_mse']) - float(x['cv_path_mse']) for x in subset]
        by_family[name] = {'n': 18, 'delta_mean': sum(diffs) / 18,
                           'worse': sum(d > 1e-9 for d in diffs),
                           'better': sum(d < -1e-9 for d in diffs),
                           'ties': sum(abs(d) <= 1e-9 for d in diffs),
                           'block_selected_four': sum(x['k_block'] == '4' for x in subset)}
        assert abs(by_family[name]['delta_mean'] -
                   (original['by_family'][name]['block4'] -
                    original['by_family'][name]['cv_path'])) < 1e-12
    delta = original['mse']['block4'] - original['mse']['cv_path']
    assert delta > 0
    assert abs(sum(v['delta_mean'] for v in by_family.values()) / 4 - delta) < 1e-12
    contribution = by_family['four_plus_fifth']['delta_mean'] / (4 * delta)
    return {'rows': len(rows), 'mean_excess_mse': delta,
            'out_of_grammar_share_of_net_excess': contribution,
            'by_family': by_family, 'classification_unchanged': original['screen_decision']}


if __name__ == '__main__':
    print(json.dumps({'schema': 'energy70.retro-analysis.v1',
                      'proof': proof(), 'receipt_diagnostic': diagnose(),
                      'scientific_pass': False, 'native_training': False},
                     indent=2, sort_keys=True))
