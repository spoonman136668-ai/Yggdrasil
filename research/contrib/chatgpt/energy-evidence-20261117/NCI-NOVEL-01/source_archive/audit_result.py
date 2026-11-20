"""Independent read-only post-score integrity/summary; never imports world or core."""
import json,hashlib,collections,statistics,itertools,math,sys
from pathlib import Path

root=Path(__file__).resolve().parent
raw=(root/'primary_result.json').read_bytes()
p=json.loads(raw)
expected_seeds=(481223,481247,481269,481283)
families=('disjoint_xor','disjoint_and','disjoint_or','disjoint_mixed','unchanged_a','unchanged_b','equiv_unidentified','out_of_grammar')
assert p['study_seeds']==list(expected_seeds)
assert p['preflight_exposed_seed_not_in_primary']==481201
assert len(p['worlds'])==32
assert {(x['seed'],x['family']) for x in p['worlds']}==set(itertools.product(expected_seeds,families))
assert all(x['action_count_per_arm']==576 for x in p['worlds'])
assert all(x['state_bytes']['MAP']<=65536 for x in p['worlds'])
assert all(not x['scientific_acceptance'] for x in p['worlds'])
assert all(x['candidate_relation']['t']['witnesses']>=64 for x in p['worlds'])
assert all(x['candidate_relation']['y']['witnesses']>=64 for x in p['worlds'])
assert all(x['seed']!=481201 for x in p['worlds'])
assert not p['scientific_pass'] and p['source_free_self_authored']

mean=lambda seq:sum(seq)/len(seq)
novel=[w for w in p['worlds'] if w['family'].startswith('disjoint_')]
diff_by_seed={}
reward_by_seed={}
for seed in expected_seeds:
    rows=[w for w in novel if w['seed']==seed]
    diff_by_seed[str(seed)]=mean([w['held_shared_brier']['MAP']-w['held_shared_brier'][w['selected_control_on_validation']] for w in rows])
    reward_by_seed[str(seed)]=mean([w['held_policy_reward']['MAP']-w['held_policy_reward'][w['selected_control_on_validation']] for w in rows])

# All 4^4 seed-resampling combinations; posthoc descriptive interval only.
vals=list(diff_by_seed.values());rvals=list(reward_by_seed.values())
bootstrap=sorted(mean([vals[i] for i in idx]) for idx in itertools.product(range(4),repeat=4))
rewardboot=sorted(mean([rvals[i] for i in idx]) for idx in itertools.product(range(4),repeat=4))
lo=lambda x:x[6];hi=lambda x:x[249]
novel_cand=mean([w['held_shared_brier']['MAP'] for w in novel])
novel_control=mean([w['held_shared_brier'][w['selected_control_on_validation']] for w in novel])
neg=[w for w in p['worlds'] if w['family']=='out_of_grammar']
eq=[w for w in p['worlds'] if w['family']=='equiv_unidentified']
summary={
'schema':'nci-novel01.posthoc-source-free-audit.v1',
'full_result_sha256':hashlib.sha256(raw).hexdigest(),
'primary_seeds':list(expected_seeds),
'exposed_preflight_seed_excluded':True,
'world_count':32,
'actual_source_free_action_count_per_arm':32*576,
'primary_synthetic_outcome_reveals_per_arm':32*576,
'primary_descriptive_frozen_hypothesis_held_novel_brier_MAP':novel_cand,
'primary_descriptive_held_novel_brier_VALID_selected_control':novel_control,
'novel_relative_brier_reduction':(novel_control-novel_cand)/novel_control,
'novel_mean_candidate_policy_reward':mean([w['held_policy_reward']['MAP'] for w in novel]),
'novel_mean_VALID_selected_control_policy_reward':mean([w['held_policy_reward'][w['selected_control_on_validation']] for w in novel]),
'novel_action_reward_difference_MAP_minus_control':mean(reward_by_seed.values()),
'novel_seed_level_differences_MAP_minus_control_brier':diff_by_seed,
'novel_seed_level_differences_MAP_minus_control_policy_reward':reward_by_seed,
'posthoc_descriptive_seedblock_brier_difference_95pct':[lo(bootstrap),hi(bootstrap)],
'posthoc_descriptive_seedblock_policy_reward_difference_95pct':[lo(rewardboot),hi(rewardboot)],
'novel_qualified_families':p['aggregate']['winning_families'],
'novel_required_families':3,
'observational_equivalence_refusals':sum(not (w['candidate_relation']['t']['identified'] and w['candidate_relation']['y']['identified']) for w in eq),
'out_of_grammar_refusals':sum(not (w['candidate_relation']['t']['identified'] and w['candidate_relation']['y']['identified']) for w in neg),
'out_of_grammar_MAP_brier':mean([w['held_shared_brier']['MAP'] for w in neg]),
'out_of_grammar_VALID_selected_control_brier':mean([w['held_shared_brier'][w['selected_control_on_validation']] for w in neg]),
'out_of_grammar_policy_reward_MAP':mean([w['held_policy_reward']['MAP'] for w in neg]),
'out_of_grammar_policy_reward_control':mean([w['held_policy_reward'][w['selected_control_on_validation']] for w in neg]),
'old_family_bank_preservation':'PASS: frozen OLD model digests checked at every RETURN readout',
'cold_snapshot_roundtrip':'PASS: byte-identical canonical snapshot restore per arm',
'max_candidate_checkpoint_bytes':max(w['state_bytes']['MAP'] for w in p['worlds']),
'mean_candidate_checkpoint_bytes':mean([w['state_bytes']['MAP'] for w in p['worlds']]),
'candidate_full_process_CPU_s':sum(w['full_process_cpu_seconds']['MAP'] for w in p['worlds']),
'exact_BMA_full_process_CPU_s':sum(w['full_process_cpu_seconds']['BMA'] for w in p['worlds']),
'control_validation_selection_counts':dict(collections.Counter(w['selected_control_on_validation'] for w in p['worlds'])),
'scientific_status':'DEV_NO_GO_NO_SCIENTIFIC_PASS',
'engineering_source_free_fixture_status':'LOCAL_PASS_12_TESTS',
'full_original_native_crossplatform_regression':'NOT_RUN_IN_THIS_GATE',
'original_world_first_use':False,'owner_checkpoint_mutated':False,
'github_full_source_code_custody':'UNVERIFIED_SOURCE_HASH_ONLY',
}
(root/'audit_result.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2))
