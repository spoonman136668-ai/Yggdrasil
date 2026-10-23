"""NLD-06: online surprise detection, continuous public clock, no phase reset."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/"nld05"))
from context_formation import (CueNative,CuePerceptron,CueEpisodic,
    FIT,SEED,DELAY,PROBES,SCORED,PATTERNS,PUBLIC_CODES,
    source_fit_phase_private,source_eval_private,public_correct,digest,canonical)

WINDOW,WARMUP,THRESHOLD,CAPACITY=16,64,6,2
TOTAL=2*FIT

class Detector:
    def __init__(self,allow=True):
        self.allow=allow
        self.codes=[-1]
        self.active=-1
        self.pending={}
        self.errors=[]
        self.feedback_count=0
        self.transitions=[]
    def observe(self,token,sensors,action,tick,model):
        if token in self.pending or not token.startswith("PUB-"):
            raise ValueError("NLD06_DUPLICATE_OR_INVALID_TOKEN")
        self.pending[token]=(tick,model.choose(sensors,self.active))
    def feedback(self,item):
        token=item["token"]
        if token not in self.pending:
            raise ValueError("NLD06_UNMATCHED_OR_DUPLICATE_FEEDBACK")
        born,predicted=self.pending[token]
        if born!=item["tick"] or item["feedback_tick"]!=born+DELAY:
            raise ValueError("NLD06_DELAY_VIOLATION")
        error=int(predicted!=public_correct(item))
        self.errors=(self.errors+[error])[-WINDOW:]
        self.feedback_count+=1
        del self.pending[token]
        if (self.allow and len(self.codes)<CAPACITY and
            self.feedback_count>=WARMUP and len(self.errors)==WINDOW and
            sum(self.errors)>=THRESHOLD):
            self.codes.append(1)
            self.active=1
            self.transitions.append({"feedback_tick":item["feedback_tick"],
                "observation_tick":born,"feedback_count":self.feedback_count,
                "rolling_prediction_errors":sum(self.errors)})
    def route(self,model,probes):
        if len(probes)!=PROBES or len({r["token"] for r in probes})!=PROBES:
            raise ValueError("NLD06_EVAL_PROBE_COUNT_OR_TOKEN")
        truth=[public_correct(r) for r in probes]
        errors=[sum(model.choose(tuple(p["sensors"]),code)!=correct
                    for p,correct in zip(probes,truth)) for code in self.codes]
        index=min(range(len(errors)),key=lambda i:(errors[i],i))
        return {"slot":self.codes[index],"public_errors":errors,
                "ambiguous":errors.count(min(errors))>1}
    def save(self):
        if self.pending:raise ValueError("NLD06_PENDING_FEEDBACK")
        state={"schema":"nld06.router.v1","allow":self.allow,"codes":self.codes,
               "active":self.active,"errors":self.errors,
               "count":self.feedback_count,"transitions":self.transitions,
               "window":WINDOW,"warmup":WARMUP,"threshold":THRESHOLD}
        return canonical({"state":state,"hash":digest(state)})
    @staticmethod
    def restore(raw):
        if type(raw) is not bytes or not 0<len(raw)<16384:
            raise ValueError("NLD06_CHECKPOINT_SIZE")
        try:
            data=json.loads(raw)
            st=data["state"]
            if digest(st)!=data["hash"] or st["schema"]!="nld06.router.v1":
                raise ValueError("hash")
            if (st["window"],st["warmup"],st["threshold"])!=(WINDOW,WARMUP,THRESHOLD):
                raise ValueError("config")
            if st["codes"] not in ([-1],[-1,1]) or st["active"] not in st["codes"]:
                raise ValueError("slots")
            if type(st["count"]) is not int or not 0<=st["count"]<=TOTAL:
                raise ValueError("count")
            if type(st["errors"]) is not list or len(st["errors"])>WINDOW or any(type(v) is not int or v not in (0,1) for v in st["errors"]):
                raise ValueError("errors")
            if type(st["transitions"]) is not list or len(st["transitions"])>1:
                raise ValueError("transitions")
            if type(st["allow"]) is not bool or not st["allow"] and len(st["codes"])>1:
                raise ValueError("disabled")
            out=Detector(st["allow"])
            out.codes=st["codes"]
            out.active=st["active"]
            out.feedback_count=st["count"]
            out.errors=st["errors"]
            out.transitions=st["transitions"]
            if out.save()!=raw:raise ValueError("noncanonical")
            return out
        except (ValueError,TypeError,KeyError):
            raise ValueError("NLD06_CHECKPOINT_INVALID")

def original_public_stream():
    """Private source custody boundary: ONLY neutral public event tokens leave."""
    a,aa=source_fit_phase_private(0)
    b,bb=source_fit_phase_private(1)
    events=[]
    for tick,x in enumerate(a+b):
        if x["action"]!=(sum(x["sensors"])+tick)%2:
            raise AssertionError("NLD06_INTERVENTION_DRIFT")
        events.append({"token":"PUB-%03d"%tick,"tick":tick,
            "feedback_tick":tick+DELAY,"sensors":tuple(x["sensors"]),
            "action":x["action"],"success":x["success"]})
    if len(events)!=TOTAL:raise AssertionError("NLD06_SOURCE_COUNT")
    return events,[aa,bb]

def run(seed=SEED):
    if type(seed) is not int or seed!=SEED:
        raise ValueError("NLD06_PUBLIC_SEED3_ONLY")
    events,receipts=original_public_stream()
    arms=[("native_detect",CueNative(True),Detector()),
          ("perceptron_detect",CuePerceptron(True),Detector()),
          ("episodic_detect",CueEpisodic(True),Detector()),
          ("native_never_switch",CueNative(True),Detector(False)),
          ("perceptron_never_switch",CuePerceptron(True),Detector(False)),
          ("episodic_never_switch",CueEpisodic(True),Detector(False))]
    oracle=CueNative(True)
    due={}
    for t in range(TOTAL+DELAY):
        for x in due.pop(t,[]):
            for _,model,router in arms:
                model.learn_delayed(x["token"],x["success"],t)
                router.feedback(x)
            oracle.learn_delayed(x["token"],x["success"],t)
        if t>=TOTAL:continue
        x=events[t]
        for _,model,router in arms:
            router.observe(x["token"],x["sensors"],x["action"],t,model)
            model.observe_public_action(x["token"],x["sensors"],router.active,x["action"],t)
        oracle.observe_public_action(x["token"],x["sensors"],PUBLIC_CODES[t//FIT],x["action"],t)
        due.setdefault(t+DELAY,[]).append(x)
    if due or oracle.pending or oracle.feedback_updates!=TOTAL:raise AssertionError("NLD06_STREAM_DRAIN")
    if any(m.pending or r.pending or m.feedback_updates!=TOTAL or r.feedback_count!=TOTAL
           for _,m,r in arms):raise AssertionError("NLD06_PUBLIC_INFORMATION_PARITY")
    policy=arms[0][1]
    controller=arms[0][2]
    ps=policy.save()
    rs=controller.save()
    restored=CueNative.restore(ps)
    if Detector.restore(rs).save()!=rs or any(
       policy.choose(p,c)!=restored.choose(p,c)
       for c in PUBLIC_CODES for p in PATTERNS):
        raise AssertionError("NLD06_COLD_RESTART")
    scoring={}
    for stage in (0,1):
        probes,public_sensors,private_truth=source_eval_private(stage)
        probes=[{**r,"token":"PUB-EVAL-%03d"%i} for i,r in enumerate(probes)]
        before={name:(m.save(),r.save()) for name,m,r in arms}
        predictions={}
        inferred={}
        for name,model,router in arms:
            picked=router.route(model,probes)
            predictions[name]=sum(model.choose(s,picked["slot"])==y
                     for s,y in zip(public_sensors,private_truth))
            inferred[name]=picked
        predictions["privileged_source_phase_oracle"]=sum(
            oracle.choose(s,PUBLIC_CODES[stage])==y
            for s,y in zip(public_sensors,private_truth))
        if any(before[name]!=(m.save(),r.save()) for name,m,r in arms):
            raise AssertionError("NLD06_READONLY_EVALUATION")
        scoring["source_role_%d"%stage]={
            "private_source_family_for_audit_only":("A","B")[stage],
            "diagnostic_probes":PROBES,"scored":SCORED,
            "correct_of_56":predictions,"inferred_slots":inferred,
            "probe_history_sha256":digest(probes)}
    return {"schema":"itd01.nld06.continuous_public_dev.v1",
      "original_nld05_sha":"fafe088ea6c065123b88e83532bde06a9998a72f",
      "source_seed":SEED,"protected_first_use":False,
      "original_R9_science_seeds_reused":False,
      "source_custody_private_receipts":receipts,
      "public_monotonic_stream_sha256":digest(events),
      "public_source_count":TOTAL,"all_models_delayed_updates":TOTAL,
      "public_feedback_delay":DELAY,"source_reset_visible_to_models":False,
      "offline_replay_or_phase_buffering":False,
      "window":WINDOW,"warmup":WARMUP,"threshold":THRESHOLD,
      "detected_context_transitions":{name:router.transitions for name,m,router in arms},
      "slots":{name:router.codes for name,m,router in arms},
      "model_plus_router_bytes":{name:len(m.save())+len(r.save()) for name,m,r in arms},
      "native_cold_restart":{"policy_sha256":hashlib.sha256(ps).hexdigest(),
                             "router_sha256":hashlib.sha256(rs).hexdigest(),
                             "prediction_comparisons":32},
      "scoring":scoring,
      "true_change_tick_exclusively_private_audit":FIT,
      "causal_composition":"NOT_TESTED",
      "unfamiliar_transfer":"NOT_TESTED_R9_NO_GO_PRESERVED",
      "model_resource_cpu_rss_parity":False,
      "ckb_admission":"NOT_OBSERVED",
      "disposition":"NLD06_REUSED_DEV_CONTINUOUS_SURPRISE_RETAIN_ALL_NEGATIVES"}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke",action="store_true",required=True)
    parser.parse_args()
    print(json.dumps(run(),sort_keys=True,separators=(",",":"),allow_nan=False))
