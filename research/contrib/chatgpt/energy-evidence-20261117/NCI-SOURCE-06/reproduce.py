#!/usr/bin/env python3
"""NCI-SOURCE-06: finite source-contract proof; no model imports/actions."""
from itertools import product
import json

def check():
    out = {}
    for projection in (0, 1):
        accepted = rejected = 0
        for context, other0, other1, x1, s2, x2, y in product((0, 1), repeat=7):
            views = ((context, other0), (context, other1)) if projection == 0 else ((other0, context), (other1, context))
            row = {'s1': context, 'x1': x1, 's2': s2, 'x2': x2, 'y': y}
            if not (views[0][projection] == views[1][projection] == row['s1']):
                raise ValueError('native source-projection invariant violated')
            first_coordinate_guard = row['s1'] == views[0][0] == views[1][0]
            accepted += first_coordinate_guard
            rejected += not first_coordinate_guard
        out[str(projection)] = {'valid_native_cases': accepted + rejected,
                                'proposed_guard_accepts': accepted,
                                'proposed_guard_rejects': rejected}
    if out != {'0': {'valid_native_cases': 128, 'proposed_guard_accepts': 128, 'proposed_guard_rejects': 0},
               '1': {'valid_native_cases': 128, 'proposed_guard_accepts': 32, 'proposed_guard_rejects': 96}}:
        raise ValueError('unexpected guard compatibility result')
    return out

if __name__ == '__main__':
    print(json.dumps({'schema': 'nci-source06.projection-contract.v1',
                      'status': 'ENGINEERING_ANALYTIC_ONLY',
                      'results': check(), 'new_source_actions': 0,
                      'real_model_restored': False, 'scientific_pass': False},
                     sort_keys=True, indent=2))
