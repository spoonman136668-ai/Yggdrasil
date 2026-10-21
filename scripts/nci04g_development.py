"""NCI-04G3 source-free *development* comparison; no scientific first-use.

Explicitly test unfamiliar outcome operators after frozen prelesion training.
This harness does not silently refresh weights on heldout cases.
Only --primary with a previously sealed source hash executes the comparison.
"""
import argparse
import hashlib
import json
import resource
import sys
import time
from pathlib import Path
from yggdrasil.nci04g_local_reconstruction import LocalReconstructor

TRAIN_SEEDS=tuple(range(1201,1209))
HELDOUT_SEEDS=tuple(range(2201,2217))
TARGET=0
NEIGHBORS=(7,1)

def pattern(n):
    # Pairwise independent within the train distribution, no hidden IDs.
    return [((n>>i)&1) for i in range(7)]+[n.bit_count()%2]

class TrainedConditionalControl:
    """Conventional fully trained per-neighbor conditional response counts.

    Given precisely the same immediate-neighbor target messages during
    prelesion learning. The two neighbor tables survive only on those cells.
    """
    def __init__(self):
        self.counts=[[[0,0],[0,0]] for _ in range(2)]
        self.messages=0
    def observe(self,bits,outcome):
        for q,j in enumerate(NEIGHBORS):
            self.counts[q][bits[j]][outcome]+=1
            self.messages+=2
    def predict(self,bits):
        candidates=[]
        for q,j in enumerate(NEIGHBORS):
            a0,b0=self.counts[q][0]
            a1,b1=self.counts[q][1]
            seen=a0+b0+a1+b1
            p0=(b0+1)/(a0+b0+2)
            p1=(b1+1)/(a1+b1+2)
            score=abs(p1-p0)*seen/(seen+4)
            a,b=self.counts[q][bits[j]]
            p=(b+1)/(a+b+2)
            candidates.append((score,p,seen))
            self.messages+=5
        candidates.sort(reverse=True)
        score,p,seen=candidates[0]
        if score<=.15 or seen<8 or abs(p-.5)<=.15:
            return None,False
        return int(p>.5),True

def model_bytes(m):
    return sum(len(c) for c in m.cells)

def run_development():
    results=[]
    candidate_cpu=0
    control_cpu=0
    total_message_bytes=0
    for seed in HELDOUT_SEEDS:
        # Mapping to one of eight *separately trained* source-free witnesses.
        train_seed=TRAIN_SEEDS[(seed-HELDOUT_SEEDS[0])%len(TRAIN_SEEDS)]
        model=LocalReconstructor()
        ctrl=TrainedConditionalControl()
        start=time.process_time_ns()
        for n in range(128):
            bits=pattern((n+(train_seed-1201)*7)%128)
            out=[bits[(i-1)%8] for i in range(8)]
            model.observe_prelesion(bits,out)
        candidate_cpu+=time.process_time_ns()-start
        start=time.process_time_ns()
        for n in range(128):
            bits=pattern((n+(train_seed-1201)*7)%128)
            ctrl.observe(bits,bits[NEIGHBORS[0]])
        control_cpu+=time.process_time_ns()-start
        model.lesion([TARGET])
        bits=pattern((seed*31)%128)
        # An unfamiliar *operator*: the informative neighbor switches on
        # even heldout seeds; unseen consequence is never fed back to model.
        ground=bits[NEIGHBORS[0 if seed%2 else 1]]
        start=time.process_time_ns()
        guess,known=model.reconstruct(bits,TARGET)
        candidate_cpu+=time.process_time_ns()-start
        start=time.process_time_ns()
        control_guess,control_known=ctrl.predict(bits)
        control_cpu+=time.process_time_ns()-start
        total_message_bytes+=model.message_bytes
        results.append({"seed":seed,"correct":bool(known and guess==ground),
                        "hard_false_positive":bool(known and guess!=ground),
                        "abstained":not known,
                        "control_correct":bool(control_known and control_guess==ground),
                        "control_hard_false_positive":bool(control_known and control_guess!=ground)})
    correct=sum(x["correct"] for x in results)
    wrong=sum(x["hard_false_positive"] for x in results)
    baseline=sum(x["control_correct"] for x in results)
    report={
      "experiment_id":"NCI04G-Y1","classification":"DEVELOPMENT_NEGATIVE" if (correct<12 or wrong or correct<=baseline) else "MIXED_PENDING_RESOURCE_PROOF",
      "source_free":True,"independent_scientific_first_use":False,
      "train_seeds":TRAIN_SEEDS,"development_seeds":HELDOUT_SEEDS,
      "heldout_correct":correct,"heldout_total":len(results),
      "hard_false_positives":wrong,"trained_conventional_correct":baseline,
      "trained_conventional_hard_false_positives":sum(x["control_hard_false_positive"] for x in results),
      "all_labels_post_lesion":0,"candidate_learned_counter_bytes":256,
      "candidate_total_message_bytes":total_message_bytes,
      "control_message_bytes_per_case":ctrl.messages,
      "candidate_cpu_ns":candidate_cpu,"control_cpu_ns":control_cpu,
      "process_peak_rss_kb":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "unseen_topology_qualified":False,
      "limitations":"Changing source-free functional operator without new labels is not identified by current local counts; no matched-RSS or broader native training proof.",
      "per_seed":results}
    print("NCI04G_YGGDRASIL_DEVELOPMENT_RESULT="+json.dumps(report,sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--primary",action="store_true")
    p.add_argument("--manifest",type=Path)
    args=p.parse_args()
    if not args.primary:
        print("NCI04G_DEVELOPMENT_NOT_RUN: --primary and sealed manifest required")
        return
    if not args.manifest or not args.manifest.exists():
        raise SystemExit("SEALED_SOURCE_MANIFEST_REQUIRED")
    m=json.loads(args.manifest.read_text("utf-8"))
    if m.get("experiment_id")!="NCI04G-Y1" or m.get("prereg_sha")!="90a0c4546d3cf5e7a82a1d762eafc76af2300549":
        raise SystemExit("SEALED_PREREG_IDENTITY_MISMATCH")
    real=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if m.get("generator_sha256")!=real or m.get("train_seeds")!=list(TRAIN_SEEDS) or m.get("development_seeds")!=list(HELDOUT_SEEDS):
        raise SystemExit("SEALED_GENERATOR_DRIFT")
    run_development()

if __name__=="__main__":
    main()
