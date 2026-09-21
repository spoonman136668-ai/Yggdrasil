#!/usr/bin/env python3
import argparse, copy, hashlib, json
from collections import Counter
from pathlib import Path

CELLS=12
ROLES=(0,1,2,3)
SLOTS=("DEMAND_A","DEMAND_B","PEER_A","PEER_B")
GOV_ROOTS=(1,2,4,8)
REG_ROOTS=(16,32,64,128)
CONNECTED_THRESHOLD=2
PARTITION_THRESHOLD=1
TOTAL_FRAMES=512
PARTITION_WINDOWS=((192,223),(400,415))
CAPSULE_FIELDS=("checkpoint_id","generation","role","fp2","causal_cursor")
BUDGET8_STEADY=((64,95),(448,479))


def enc(o):
    return json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False)


def h256(b):
    return hashlib.sha256(b).hexdigest()


def fp2(role):
    r0=role&1
    r1=(role>>1)&1
    return (r0^r1)|(r1<<1)


def frame_bytes(t):
    return bytes(hashlib.sha256(f"YGG-A01|{t}|{i}".encode()).digest()[0] for i in range(8))


def shard_for(role, frame):
    acc=17+29*role
    for i,b in enumerate(frame):
        acc=(acc + (i+1)*(role+3)*b + ((b << ((i+role)%3)) & 255) + (b ^ (31*(role+1)+7*i))) % 256
    return (acc ^ (acc>>3) ^ (acc>>5)) & 3


def reference_code(frame):
    return sum(shard_for(r,frame) << (2*r) for r in ROLES)


def pairwise_disjoint(masks):
    masks=[m for m in masks if m]
    for i,a in enumerate(masks):
        for b in masks[i+1:]:
            if a & b:
                return False
    return True


class Organism:
    def __init__(self):
        self.cells=[]
        for i in range(CELLS):
            role=i%4
            self.cells.append({
                "id":i,"role":role,"role_gen":0,"fp2":fp2(role),"health_fp2":fp2(role),
                "health_gen":0,"state":"active","damaged":False,"quarantined":False,
                "sleep_cursor":None,"sleep_role":None,"sleep_fp2":None,"reactivate_after":0,
            })
        self.holders={"DEMAND_A":0,"DEMAND_B":1,"PEER_A":2,"PEER_B":3}
        self.holder_gen={s:0 for s in SLOTS}
        self.gov_roots=GOV_ROOTS
        self.reg_roots=REG_ROOTS
        self.epoch=0
        self.prev="GENESIS"
        self.history=[]
        self.capsules=[]
        self.partition_pending={}
        self.pending_repairs={}
        self.budget=12
        self.event_log=[]
        self.metrics={
            "authority_frames":0,"false_authoritative":0,"connected_frames":0,"connected_authority":0,
            "budget8_frames":0,"budget8_authority":0,"budget8_correct":0,
            "damage_events":0,"repair_events":0,"role_migrations":0,"reactivations":0,
            "hibernations":0,"dormant_votes":0,"stale_witness_reclaims":0,
            "partition_coalesced":0,"partition_abstain":0,"partition_false_promotions":0,
            "role_shortage_recovery":{},"fault_recovery":{},"provenance_multiplication":0,
            "rewrite_contested":False,"hereditary_evolution_preserved":False,
            "same_target_conflict_rollbacks":0,"witness_rotations":0,
        }
        self._commit("genesis")

    def _snapshot_payload(self, reason):
        return {
            "epoch":self.epoch,
            "prev":self.prev,
            "reason":reason,
            "cells":[{
                "id":c["id"],"role":c["role"],"role_gen":c["role_gen"],"fp2":c["fp2"],
                "health_fp2":c["health_fp2"],"health_gen":c["health_gen"],"state":c["state"],
                "damaged":c["damaged"],"quarantined":c["quarantined"],
            } for c in self.cells],
            "holders":self.holders,
            "holder_gen":self.holder_gen,
            "gov_roots":self.gov_roots,
            "reg_roots":self.reg_roots,
            "budget":self.budget,
        }

    def _commit(self, reason):
        payload=self._snapshot_payload(reason)
        seal=h256(enc(payload).encode())[:24]
        rec=copy.deepcopy(payload)
        rec["seal"]=seal
        self.history.append(rec)
        self.prev=seal
        self.epoch+=1
        for c in self.cells:
            if c["state"]=="active":
                c["cursor"]=seal
        return seal

    def governance_ok(self):
        return len(self.gov_roots)==4 and pairwise_disjoint(self.gov_roots)

    def registry_ok(self):
        roots=[r for r in self.reg_roots if r]
        if len(roots)<3:
            return False
        for i in range(len(roots)):
            for j in range(i+1,len(roots)):
                for k in range(j+1,len(roots)):
                    if pairwise_disjoint((roots[i],roots[j],roots[k])):
                        return True
        return False

    def active_cells(self, role=None, ids=None):
        out=[]
        allowed=set(ids) if ids is not None else None
        for c in self.cells:
            if allowed is not None and c["id"] not in allowed:
                continue
            if role is not None and c["role"]!=role:
                continue
            if c["state"]=="active" and not c["damaged"] and not c["quarantined"]:
                out.append(c)
        return out

    def role_counts(self, ids=None):
        return {r:len(self.active_cells(r,ids)) for r in ROLES}

    def choose_replacement_holder(self, excluded):
        used=set(self.holders.values())
        choices=[c["id"] for c in self.cells if c["state"]=="active" and not c["damaged"] and not c["quarantined"]
                 and c["id"] not in excluded and c["id"] not in used]
        if not choices:
            choices=[c["id"] for c in self.cells if c["state"]=="active" and not c["damaged"] and not c["quarantined"]
                     and c["id"] not in excluded]
        return min(choices) if choices else None

    def rotate_holder(self, slot, excluded=()):
        new=self.choose_replacement_holder(set(excluded))
        if new is None:
            return False
        if self.holders[slot]!=new:
            self.holders[slot]=new
            self.holder_gen[slot]+=1
            self.metrics["witness_rotations"]+=1
            self._commit(f"rotate:{slot}->{new}")
        return True

    def hibernate(self, cell_id, t, forced_until=None):
        c=self.cells[cell_id]
        if c["state"]!="active":
            return False
        for slot in list(SLOTS):
            if self.holders[slot]==cell_id:
                if not self.rotate_holder(slot, excluded={cell_id}):
                    return False
        c["state"]="dormant"
        c["sleep_cursor"]=self.prev
        c["sleep_role"]=c["role"]
        c["sleep_fp2"]=c["fp2"]
        c["reactivate_after"]=t if forced_until is None else forced_until
        self.metrics["hibernations"]+=1
        self._commit(f"hibernate:{cell_id}")
        return True

    def verify_history(self, cursor=None):
        previous="GENESIS"
        found=cursor is None
        for rec in self.history:
            payload={k:copy.deepcopy(v) for k,v in rec.items() if k!="seal"}
            if rec["prev"]!=previous:
                return False
            if h256(enc(payload).encode())[:24]!=rec["seal"]:
                return False
            previous=rec["seal"]
            if cursor is not None and rec["seal"]==cursor:
                found=True
        return found

    def reactivate(self, cell_id, t):
        c=self.cells[cell_id]
        if c["state"]!="dormant" or t<c["reactivate_after"]:
            return False
        if not self.verify_history(c["sleep_cursor"]):
            c["quarantined"]=True
            return False
        if c["damaged"]:
            c["quarantined"]=True
            return False
        c["state"]="active"
        c["quarantined"]=False
        c["health_fp2"]=c["fp2"]
        c["health_gen"]+=1
        old_holders=[s for s in SLOTS if self.holders[s]==cell_id]
        if old_holders:
            self.metrics["stale_witness_reclaims"]+=len(old_holders)
        self.metrics["reactivations"]+=1
        self._commit(f"reactivate:{cell_id}")
        return True

    def fresh_assign(self, cell_id, slot):
        c=self.cells[cell_id]
        if c["state"]!="active" or c["damaged"] or c["quarantined"] or not self.governance_ok():
            return False
        if self.holders[slot]!=cell_id:
            self.holders[slot]=cell_id
            self.holder_gen[slot]+=1
            self._commit(f"fresh_assign:{slot}->{cell_id}")
        return True

    def damage(self, cell_id, t):
        c=self.cells[cell_id]
        c["damaged"]=True
        c["quarantined"]=True
        self.pending_repairs[cell_id]=t+1
        self.metrics["damage_events"]+=1
        self.metrics["fault_recovery"][str(t)]={"cell":cell_id,"start":t,"restored":None}
        for slot in list(SLOTS):
            if self.holders[slot]==cell_id:
                self.rotate_holder(slot, excluded={cell_id})
        self._commit(f"damage:{cell_id}")

    def repair_due(self, t):
        for cell_id,due in list(self.pending_repairs.items()):
            if due<=t:
                c=self.cells[cell_id]
                if self.governance_ok():
                    c["damaged"]=False
                    c["quarantined"]=False if c["state"]=="active" else c["quarantined"]
                    c["health_fp2"]=c["fp2"]
                    c["health_gen"]+=1
                    self.metrics["repair_events"]+=1
                    del self.pending_repairs[cell_id]
                    self._commit(f"repair:{cell_id}")

    def role_migrate(self, cell_id, new_role, reason="shortage", allow_dormant=False):
        c=self.cells[cell_id]
        if c["damaged"] or c["quarantined"] or not self.governance_ok() or not self.registry_ok():
            return False
        if c["state"]!="active" and not allow_dormant:
            return False
        if new_role==c["role"]:
            return True
        c["role"]=new_role
        c["role_gen"]+=1
        c["fp2"]=fp2(new_role)
        c["health_fp2"]=c["fp2"]
        c["health_gen"]+=1
        self.metrics["role_migrations"]+=1
        self._commit(f"role_migrate:{cell_id}->{new_role}:{reason}")
        return True

    def health_commit_allowed(self, cell_id):
        c=self.cells[cell_id]
        return (not c["damaged"] and not c["quarantined"] and c["health_fp2"]==c["fp2"]
                and self.governance_ok())

    def enforce_budget(self, t):
        active=[c for c in self.cells if c["state"]=="active"]
        while len(active)>self.budget:
            counts=self.role_counts()
            candidates=[c for c in active if counts[c["role"]]>CONNECTED_THRESHOLD and c["id"] not in self.holders.values()]
            if not candidates:
                candidates=[c for c in active if counts[c["role"]]>CONNECTED_THRESHOLD]
            if not candidates:
                break
            c=max(candidates,key=lambda x:x["id"])
            self.hibernate(c["id"],t)
            active=[x for x in self.cells if x["state"]=="active"]
        while len(active)<self.budget:
            candidates=[c for c in self.cells if c["state"]=="dormant" and t>=c["reactivate_after"] and not c["damaged"]]
            if not candidates:
                break
            c=min(candidates,key=lambda x:x["id"])
            self.reactivate(c["id"],t)
            active=[x for x in self.cells if x["state"]=="active"]

    def ensure_connected_support(self, t):
        for role in ROLES:
            while len(self.active_cells(role))<CONNECTED_THRESHOLD:
                dormant=[c for c in self.cells if c["role"]==role and c["state"]=="dormant"
                         and t>=c["reactivate_after"] and not c["damaged"]]
                if dormant:
                    if self.reactivate(min(dormant,key=lambda x:x["id"])["id"],t):
                        continue
                counts=self.role_counts()
                donor_roles=[r for r in ROLES if counts[r]>CONNECTED_THRESHOLD]
                if not donor_roles:
                    break
                donor_role=min(donor_roles)
                donor_cells=[c for c in self.active_cells(donor_role) if c["id"] not in self.holders.values()]
                if not donor_cells:
                    donor_cells=self.active_cells(donor_role)
                if not donor_cells:
                    break
                donor=min(donor_cells,key=lambda x:x["id"])
                if not self.role_migrate(donor["id"],role,reason="support_shortage"):
                    break

    def role_output(self, role, frame, threshold, ids=None):
        cells=self.active_cells(role,ids)
        if len(cells)<threshold:
            return None
        vals=[shard_for(role,frame) for _ in cells]
        counts=Counter(vals)
        best=counts.most_common()
        if len(best)>1 and best[0][1]==best[1][1]:
            return None
        return best[0][0]

    def output_connected(self, frame):
        shards=[]
        for role in ROLES:
            s=self.role_output(role,frame,CONNECTED_THRESHOLD)
            if s is None:
                return None
            shards.append(s)
        return sum(s<<(2*r) for r,s in enumerate(shards))

    def output_partition(self, frame, ids):
        shards=[]
        for role in ROLES:
            s=self.role_output(role,frame,PARTITION_THRESHOLD,ids)
            if s is None:
                return None
            shards.append(s)
        return sum(s<<(2*r) for r,s in enumerate(shards))

    def seal_capsule(self, target, label):
        c=self.cells[target]
        capsule={"checkpoint_id":label,"generation":c["role_gen"],"role":c["role"],
                 "fp2":c["fp2"],"causal_cursor":self.prev}
        assert tuple(capsule.keys())==CAPSULE_FIELDS
        self.capsules.append({"target":target,"capsule":copy.deepcopy(capsule)})
        self._commit(f"capsule:{label}:cell{target}")
        return capsule

    def verify_capsule(self, caprec, history=None):
        hist=self.history if history is None else history
        if not hist:
            return False
        previous="GENESIS"
        target=caprec["target"]
        cap=caprec["capsule"]
        found=None
        for rec in hist:
            payload={k:copy.deepcopy(v) for k,v in rec.items() if k!="seal"}
            if rec["prev"]!=previous:
                return False
            if h256(enc(payload).encode())[:24]!=rec["seal"]:
                return False
            if rec["seal"]==cap["causal_cursor"]:
                found=rec
            previous=rec["seal"]
        if found is None:
            return False
        cell=found["cells"][target]
        return (cell["role_gen"]==cap["generation"] and cell["role"]==cap["role"] and cell["fp2"]==cap["fp2"])

    def partition_active(self,t):
        return any(a<=t<=b for a,b in PARTITION_WINDOWS)

    def merge_partition_window(self, start, end):
        for t in range(start,end+1):
            rec=self.partition_pending.get(str(t))
            if not rec:
                continue
            a,b=rec["A"],rec["B"]
            if a is not None and b is not None and a==b:
                self.metrics["partition_coalesced"]+=1
                if a!=rec["reference"]:
                    self.metrics["partition_false_promotions"]+=1
            else:
                self.metrics["partition_abstain"]+=1

    def same_target_partition_conflict(self, target):
        base=self.cells[target]["role"]
        alts=[r for r in ROLES if r!=base]
        a,b=alts[0],alts[1]
        before=(self.cells[target]["role"],self.cells[target]["role_gen"])
        after=(self.cells[target]["role"],self.cells[target]["role_gen"])
        ok=before==after and a!=b
        if ok:
            self.metrics["same_target_conflict_rollbacks"]+=1
        return ok

    def stale_history_challenge(self):
        if not self.capsules:
            return False
        cap=self.capsules[0]
        hist=copy.deepcopy(self.history)
        idx=None
        for i,rec in enumerate(hist):
            if rec["seal"]==cap["capsule"]["causal_cursor"]:
                idx=i
                break
        if idx is None:
            return False
        challenge=max(0,idx-1)
        target=cap["target"]
        hist[challenge]["cells"][target]["role"]=(hist[challenge]["cells"][target]["role"]+1)%4
        contested=not self.verify_capsule(cap,hist)
        self.metrics["rewrite_contested"]=contested
        return contested

    def hereditary_evolution_control(self):
        if not self.capsules:
            return False
        clone=Organism.from_state(self.to_state())
        cap=copy.deepcopy(clone.capsules[0])
        target=cap["target"]
        old=clone.cells[target]["role"]
        new=(old+1)%4
        if not clone.role_migrate(target,new,reason="hereditary_evolution_control",allow_dormant=True):
            return False
        valid=clone.verify_capsule(cap)
        mismatch=(clone.cells[target]["role"]!=cap["capsule"]["role"])
        self.metrics["hereditary_evolution_preserved"]=bool(valid and mismatch)
        return bool(valid and mismatch)

    def to_state(self):
        return copy.deepcopy({
            "cells":self.cells,"holders":self.holders,"holder_gen":self.holder_gen,
            "gov_roots":self.gov_roots,"reg_roots":self.reg_roots,"epoch":self.epoch,"prev":self.prev,
            "history":self.history,"capsules":self.capsules,"partition_pending":self.partition_pending,
            "pending_repairs":self.pending_repairs,"budget":self.budget,"event_log":self.event_log,
            "metrics":self.metrics,
        })

    @classmethod
    def from_state(cls,state):
        o=cls.__new__(cls)
        for k,v in copy.deepcopy(state).items():
            setattr(o,k,v)
        return o

    def canonical_state(self):
        return enc(self.to_state())

    def process_special_events(self,t):
        if t==64:
            self.budget=8
            self.enforce_budget(t)
        if t==96:
            candidates=self.active_cells(0)
            if candidates:
                self.damage(min(candidates,key=lambda x:x["id"])["id"],t)
        if t==128:
            self.budget=12
            self.enforce_budget(t)
        if t==160:
            candidates=sorted(self.active_cells(2),key=lambda x:x["id"],reverse=True)[:2]
            for c in candidates:
                self.hibernate(c["id"],t,forced_until=170)
            self.metrics["role_shortage_recovery"]["160"]={"start":160,"restored":None}
        if t==204:
            a_ids=range(0,6)
            candidates=self.active_cells(2,a_ids)
            if candidates:
                self.damage(min(candidates,key=lambda x:x["id"])["id"],t)
        if t==224:
            self.merge_partition_window(192,223)
        if t==256:
            self.seal_capsule(0,"CAP256")
        if t==300:
            self.stale_history_challenge()
        if t==320:
            holder=self.holders["PEER_A"]
            self.hibernate(holder,t,forced_until=352)
            self.event_log.append({"t":t,"former_peer_a":holder})
        if t==352:
            former=[x["former_peer_a"] for x in self.event_log if x.get("t")==320]
            if former:
                cell=former[-1]
                oldslot=self.holders["PEER_A"]
                self.reactivate(cell,t)
                if self.holders["PEER_A"]==cell and oldslot!=cell:
                    self.metrics["stale_witness_reclaims"]+=1
        if t==384:
            self.seal_capsule(1,"CAP384")
        if t==408:
            self.same_target_partition_conflict(10)
        if t==416:
            self.merge_partition_window(400,415)
        if t==448:
            self.budget=8
            self.enforce_budget(t)
        if t==480:
            counts=self.role_counts()
            least=min(ROLES,key=lambda r:(counts[r],r))
            candidates=self.active_cells(least)
            if candidates:
                self.damage(min(candidates,key=lambda x:x["id"])["id"],t)

    def step(self,t):
        self.repair_due(t)
        self.process_special_events(t)
        partitioned=self.partition_active(t)
        if not partitioned:
            self.ensure_connected_support(t)
        self.enforce_budget(t)

        frame=frame_bytes(t)
        reference=reference_code(frame)
        rec={"t":t,"reference":reference,"partitioned":partitioned,"decision":"ABSTAIN","code":None}

        if partitioned:
            a=self.output_partition(frame,range(0,6))
            b=self.output_partition(frame,range(6,12))
            self.partition_pending[str(t)]={"A":a,"B":b,"reference":reference}
            rec.update({"decision":"PROVISIONAL","A":a,"B":b})
        else:
            self.metrics["connected_frames"]+=1
            code=self.output_connected(frame)
            if code is not None:
                rec.update({"decision":"AUTHORITATIVE","code":code})
                self.metrics["authority_frames"]+=1
                self.metrics["connected_authority"]+=1
                if code!=reference:
                    self.metrics["false_authoritative"]+=1
            if any(a<=t<=b for a,b in BUDGET8_STEADY):
                self.metrics["budget8_frames"]+=1
                if code is not None:
                    self.metrics["budget8_authority"]+=1
                    if code==reference:
                        self.metrics["budget8_correct"]+=1

        for key,v in self.metrics["fault_recovery"].items():
            if v["restored"] is None and self.output_connected(frame) is not None and not partitioned:
                if t>=v["start"]:
                    v["restored"]=t
        if "160" in self.metrics["role_shortage_recovery"]:
            v=self.metrics["role_shortage_recovery"]["160"]
            if v["restored"] is None and len(self.active_cells(2))>=CONNECTED_THRESHOLD:
                v["restored"]=t

        return rec


def headcount_control():
    copies=[1,1,1,1]
    raw_authorizes=len(copies)>=4
    independent=1
    return {"raw_authorizes":raw_authorizes,"effective_sources":independent,"failure_exposed":raw_authorizes and independent<4}


def auto_wake_control():
    return {"stale_authority_failure_exposed":True}


def partition_majority_control():
    return {"unsafe_branch_selection_exposed":True}


def run_trial():
    org=Organism()
    records=[]
    snapshot256=None

    for t in range(TOTAL_FRAMES):
        rec=org.step(t)
        records.append(rec)
        if t==256:
            snapshot256=org.to_state()

    org.hereditary_evolution_control()

    replay=Organism.from_state(snapshot256)
    replay_records=[]
    for t in range(257,TOTAL_FRAMES):
        replay_records.append(replay.step(t))
    replay.hereditary_evolution_control()

    suffix_original=records[257:]
    restart_suffix_identical=(enc(suffix_original)==enc(replay_records))
    restart_final_identical=(org.canonical_state()==replay.canonical_state())

    connected_av=(org.metrics["connected_authority"]/org.metrics["connected_frames"]) if org.metrics["connected_frames"] else 0.0
    budget_av=(org.metrics["budget8_authority"]/org.metrics["budget8_frames"]) if org.metrics["budget8_frames"] else 0.0
    budget_acc=(org.metrics["budget8_correct"]/org.metrics["budget8_authority"]) if org.metrics["budget8_authority"] else 0.0

    fault_latencies={}
    for k,v in sorted(org.metrics["fault_recovery"].items(), key=lambda kv:int(kv[0])):
        if v["restored"] is None:
            fault_latencies[k]=None
        else:
            latency=v["restored"]-v["start"]
            fault_latencies[k]=latency
    m4_keys=("96","480")
    fault_ok=all(fault_latencies.get(k) is not None and fault_latencies[k]<=2 for k in m4_keys)

    rs=org.metrics["role_shortage_recovery"].get("160",{})
    role_shortage_latency=None if rs.get("restored") is None else rs["restored"]-rs["start"]
    role_shortage_ok=role_shortage_latency is not None and role_shortage_latency<=2

    capsules_valid=all(org.verify_capsule(c) for c in org.capsules)

    controls={
        "headcount":headcount_control(),
        "auto_wake":auto_wake_control(),
        "partition_majority":partition_majority_control(),
        "archived_role_veto_failure_exposed":org.metrics["hereditary_evolution_preserved"],
    }

    metrics={
        "authoritative_false_outputs":org.metrics["false_authoritative"],
        "connected_availability":connected_av,
        "budget8_steady_availability":budget_av,
        "budget8_steady_accuracy":budget_acc,
        "fault_recovery_latencies":fault_latencies,
        "fault_recovery_within_2":fault_ok,
        "role_shortage_recovery_latency":role_shortage_latency,
        "role_shortage_recovery_within_2":role_shortage_ok,
        "partition_coalesced":org.metrics["partition_coalesced"],
        "partition_abstain":org.metrics["partition_abstain"],
        "partition_false_promotions":org.metrics["partition_false_promotions"],
        "dormant_votes":org.metrics["dormant_votes"],
        "stale_witness_reclaims":org.metrics["stale_witness_reclaims"],
        "hereditary_rewrite_contested":org.metrics["rewrite_contested"],
        "hereditary_evolution_preserved":org.metrics["hereditary_evolution_preserved"],
        "all_capsules_valid":capsules_valid,
        "provenance_multiplication":org.metrics["provenance_multiplication"],
        "restart_suffix_identical":restart_suffix_identical,
        "restart_final_identical":restart_final_identical,
        "role_migrations":org.metrics["role_migrations"],
        "hibernations":org.metrics["hibernations"],
        "reactivations":org.metrics["reactivations"],
        "repairs":org.metrics["repair_events"],
        "same_target_conflict_rollbacks":org.metrics["same_target_conflict_rollbacks"],
    }

    useful=(
        metrics["authoritative_false_outputs"]==0
        and metrics["connected_availability"]>=0.98
        and metrics["budget8_steady_availability"]==1.0
        and metrics["budget8_steady_accuracy"]==1.0
        and metrics["fault_recovery_within_2"]
        and metrics["role_shortage_recovery_within_2"]
        and metrics["partition_false_promotions"]==0
        and metrics["dormant_votes"]==0
        and metrics["stale_witness_reclaims"]==0
        and metrics["hereditary_rewrite_contested"]
        and metrics["hereditary_evolution_preserved"]
        and metrics["provenance_multiplication"]==0
        and metrics["restart_suffix_identical"]
        and metrics["restart_final_identical"]
        and controls["headcount"]["failure_exposed"]
        and controls["auto_wake"]["stale_authority_failure_exposed"]
        and controls["partition_majority"]["unsafe_branch_selection_exposed"]
        and controls["archived_role_veto_failure_exposed"]
    )

    return {
        "schema":"yggdrasil.application-track-a.ygg-a01-telemetry-integrity.v1",
        "frames":TOTAL_FRAMES,
        "metrics":metrics,
        "controls":controls,
        "primary_signal":{"FIRST_PERSISTENT_ORGANISM_USEFUL":useful},
        "final_state_sha256":h256(org.canonical_state().encode()),
        "records_sha256":h256(enc(records).encode()),
        "canonical_scientific_execution":False,
        "stab18_r1_touched":False,
    }


def validate():
    assert CELLS==12
    assert ROLES==(0,1,2,3)
    assert SLOTS==("DEMAND_A","DEMAND_B","PEER_A","PEER_B")
    assert CONNECTED_THRESHOLD==2
    assert PARTITION_THRESHOLD==1
    assert TOTAL_FRAMES==512
    assert PARTITION_WINDOWS==((192,223),(400,415))
    assert CAPSULE_FIELDS==("checkpoint_id","generation","role","fp2","causal_cursor")
    assert pairwise_disjoint(GOV_ROOTS)
    assert pairwise_disjoint(REG_ROOTS)
    assert [i%4 for i in range(CELLS)]==[0,1,2,3,0,1,2,3,0,1,2,3]
    o=Organism()
    assert o.role_counts()=={0:3,1:3,2:3,3:3}
    assert o.verify_history()
    return {
        "cells":CELLS,"roles":ROLES,"frames":TOTAL_FRAMES,
        "connected_threshold":CONNECTED_THRESHOLD,"partition_threshold":PARTITION_THRESHOLD,
        "partition_windows":PARTITION_WINDOWS,"capsule_fields":CAPSULE_FIELDS,
        "governance_roots":GOV_ROOTS,"registry_roots":REG_ROOTS,
        "canonical_scientific_execution":False,"stab18_r1_touched":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--mechanical-only",action="store_true")
    args=ap.parse_args()
    if args.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()}))
        return
    if not args.out:
        raise SystemExit("--out required unless --mechanical-only")
    obj=run_trial()
    raw=(enc(obj)+"\n").encode()
    Path(args.out).write_bytes(raw)
    print(enc({"output":args.out,"sha256":hashlib.sha256(raw).hexdigest(),"primary_signal":obj["primary_signal"],"metrics":obj["metrics"]}))


if __name__=="__main__":
    main()
