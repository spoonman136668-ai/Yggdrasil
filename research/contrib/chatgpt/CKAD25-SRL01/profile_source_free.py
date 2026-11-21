"""POST-RESULT, source-only CPU microprofile. Not native CPU acceptance.

Reuses the consumed deterministic public history; generates no new target labels,
source actions, learner experiments, original-world first-use or policies.
"""
import json
import platform
import sys
from time import process_time
from yggdrasil.native_shared_fault_risk import (NativeSharedFaultRisk,
                                                 independent_beta_risks)
from dev_trial import STATIONARY_SEEDS,NEGATIVE_SEEDS,training_history,MASKS


def run(repetitions=80):
    histories = [training_history(s,negative=False) for s in STATIONARY_SEEDS]
    histories += [training_history(s,negative=True) for s in NEGATIVE_SEEDS]
    for _ in range(3):
        for history in histories:
            independent_beta_risks(MASKS, history)
            NativeSharedFaultRisk(MASKS, history)
    timings={}
    for arm in ('native_beta_formula','shared_fraction_joint'):
        started=process_time()
        for _ in range(repetitions):
            for history in histories:
                if arm == 'native_beta_formula':
                    independent_beta_risks(MASKS,history)
                else:
                    NativeSharedFaultRisk(MASKS,history)
        timings[arm]=process_time()-started
    return {'schema':'yggdrasil.ckad25.srl01.postresult_cpu_microprofile.v1',
        'source_free':True,'post_result':True,'actual_new_source_actions':0,
        'new_science_trials':0,'fits_per_arm':len(histories)*repetitions,
        'times_cpu_seconds':timings,
        'ratio_shared_over_beta':timings['shared_fraction_joint']/timings['native_beta_formula'],
        'native_end_to_end_cpu_ratio':'UNVERIFIED',
        'scientific_gain_verified':False,
        'runtime':{'python':sys.version.split()[0], 'platform':platform.platform()}}

if __name__=='__main__': print(json.dumps(run(),sort_keys=True,indent=2))
