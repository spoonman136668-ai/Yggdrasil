"""Sealed source for EXP-DGR5-CROSS-DOMAIN-GRANULARITY-REORGANIZATION-002."""
import argparse
import json
import math

EXPERIMENT = "EXP-DGR5-CROSS-DOMAIN-GRANULARITY-REORGANIZATION-002"
SEEDS = (140009, 141011, 142019, 143021, 144037, 145043)
CELL_COUNT = 16
LOCAL_RADIUS = 2
TRAIN_RECORDS = 2048
EVAL_RECORDS = 1024
CUE_RECORDS = 16
MASK64 = (1 << 64) - 1

SHARED = (
    ((128, 64, 170, 85), 16),
    ((129, 71, 170, 85), 29),
    ((130, 78, 170, 85), 42),
    ((131, 85, 170, 85), 55),
)
UNIQUE = {
    0: (((41, 96, 204, 51), 128), ((42, 99, 204, 51), 131)),
    1: (((34, 101, 204, 51), 136), ((35, 104, 204, 51), 139)),
    2: (((43, 106, 204, 51), 144), ((44, 109, 204, 51), 147)),
    3: (((36, 111, 204, 51), 152), ((37, 114, 204, 51), 155)),
}
EXPECTED_HOMES = {
    (128,64,170,85):13, (129,71,170,85):3, (130,78,170,85):9, (131,85,170,85):15,
    (41,96,204,51):0, (42,99,204,51):2,
    (34,101,204,51):4, (35,104,204,51):6,
    (43,106,204,51):8, (44,109,204,51):10,
    (36,111,204,51):12, (37,114,204,51):14,
}

def splitmix64(seed, counter):
    x = (seed + 0x9E3779B97F4A7C15 * (counter + 1)) & MASK64
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & MASK64
    return x ^ (x >> 31)

def home_cell(key):
    b0,b1,b2,b3=key
    return (3*b0+5*b1+7*b2+11*b3)%CELL_COUNT

def ring_distance(a,b):
    d=abs(a-b)
    return min(d,CELL_COUNT-d)

def local_cells(home):
    return [idx for _,idx in sorted((ring_distance(home,idx),idx) for idx in range(CELL_COUNT) if ring_distance(home,idx)<=LOCAL_RADIUS)]

def domain_items(domain):
    return list(SHARED)+list(UNIQUE[domain])

def filler_byte(seed, domain, record, filler_index, phase):
    counter = phase*10_000_000 + domain*1_000_000 + record*3 + filler_index
    return 192 + (splitmix64(seed ^ (domain*0x1F123BB5), counter) % 64)

def corpus(seed, domain, records, phase):
    stream=[]
    targets=[]
    items=domain_items(domain)
    offset=(seed+domain+phase)%6
    for record in range(records):
        item=(5*record+offset)%6
        key, successor = items[item]
        stream.extend(key)
        targets.append((len(stream), key, successor))
        stream.append(successor)
        for filler in range(3):
            stream.append(filler_byte(seed,domain,record,filler,phase))
    return stream,targets

def empty_cells():
    return [{"index":i,"role":"generic","key":None,"successor":None,"home":None} for i in range(CELL_COUNT)]

def cell_signature(cell):
    return (cell["index"],cell["role"],cell.get("key"),cell.get("successor"),cell.get("home"))

def active_key_map(cells):
    return {tuple(c["key"]):c["index"] for c in cells if c["role"]=="specialized" and c.get("key") is not None}

def best_successor(stats):
    best=None
    best_count=-1
    for value,count in stats["successors"].items():
        if count>best_count or (count==best_count and (best is None or value<best)):
            best=value; best_count=count
    return best,best_count

def develop_domain(cells, retained, stream):
    tables=[{} for _ in range(CELL_COUNT)]
    known=set(active_key_map(cells)) | set(retained)
    newly=[]
    radius_violations=0
    invalid=0
    for start in range(0,len(stream)-4):
        key=tuple(stream[start:start+4])
        nxt=stream[start+4]
        if len(key)!=4:
            invalid+=1; continue
        if key in known:
            continue
        home=home_cell(key)
        stats=tables[home].get(key)
        if stats is None:
            stats={"total":0,"successors":{}}
            tables[home][key]=stats
        stats["total"]+=1
        stats["successors"][nxt]=stats["successors"].get(nxt,0)+1
        if stats["total"]<64:
            continue
        succ,best=best_successor(stats)
        if best/stats["total"]<0.90:
            continue
        if key in known:
            continue
        target=None
        for idx in local_cells(home):
            if cells[idx]["role"]=="generic":
                target=idx; break
        if target is None:
            continue
        if ring_distance(home,target)>LOCAL_RADIUS:
            radius_violations+=1; continue
        cells[target]={"index":target,"role":"specialized","key":key,"successor":succ,"home":home}
        known.add(key)
        newly.append(key)
    return newly,radius_violations,invalid

def predict(cells,key):
    home=home_cell(key)
    matches=[]
    for idx in local_cells(home):
        cell=cells[idx]
        if cell["role"]=="specialized" and tuple(cell["key"])==tuple(key):
            matches.append((ring_distance(home,idx),idx,cell["successor"]))
    if not matches:
        return 0
    matches.sort()
    return matches[0][2]

def evaluate(cells,seed,domain,phase):
    _,targets=corpus(seed,domain,EVAL_RECORDS,phase)
    correct=0
    for _,key,target in targets:
        correct += int(predict(cells,key)==target)
    return correct/len(targets)

def hibernate_unique(cells, retained, domain):
    records=0
    unique_keys={tuple(key) for key,_ in UNIQUE[domain]}
    for idx,cell in enumerate(cells):
        if cell["role"]!="specialized" or tuple(cell["key"]) not in unique_keys:
            continue
        key=tuple(cell["key"])
        retained[key]=bytes([idx,*key,cell["successor"]])
        cells[idx]={"index":idx,"role":"generic","key":None,"successor":None,"home":None}
        records+=1
    return records

def cue_keys(seed,domain):
    _,targets=corpus(seed,domain,CUE_RECORDS,2)
    return {tuple(key) for _,key,_ in targets}

def wake_from_cue(cells,retained,cues):
    matches=[key for key in sorted(retained) if key in cues]
    woke=0
    invalid=0
    for key in matches:
        record=retained[key]
        if len(record)!=6:
            invalid+=1; continue
        idx=record[0]
        record_key=tuple(record[1:5])
        succ=record[5]
        if record_key!=key or idx>=CELL_COUNT or cells[idx]["role"]!="generic":
            invalid+=1; continue
        cells[idx]={"index":idx,"role":"specialized","key":key,"successor":succ,"home":home_cell(key)}
        del retained[key]
        woke+=1
    return woke,len(matches),invalid

def known_motif_count(cells,retained):
    return len(active_key_map(cells))+len(retained)

def active_count(cells):
    return sum(1 for c in cells if c["role"]=="specialized")

def run():
    for key,expected in EXPECTED_HOMES.items():
        assert home_cell(key)==expected
    assert len(set(EXPECTED_HOMES.values()))==12

    metrics={
        "valid_seed_count":0.0,
        "minimum_shared_motif_reuse_count":4.0,
        "maximum_shared_structure_mutation_count":0.0,
        "minimum_first_exposure_unique_specialization_count_per_domain":2.0,
        "maximum_first_exposure_unique_specialization_count_per_domain":0.0,
        "minimum_first_exposure_domain_accuracy":1.0,
        "minimum_revisit_domain_accuracy":1.0,
        "minimum_prior_domain_retained_accuracy":1.0,
        "maximum_active_specialized_structure_count":0.0,
        "maximum_total_hibernated_unique_bytes":0.0,
        "minimum_revisit_wake_count":2.0,
        "maximum_revisit_wake_count":0.0,
        "minimum_revisit_cue_precision":1.0,
        "minimum_revisit_cue_recall":1.0,
        "maximum_wake_to_first_exposure_operation_ratio":0.0,
        "minimum_final_known_motif_count":12.0,
        "maximum_final_known_motif_count":0.0,
        "maximum_final_physical_cell_count":16.0,
        "minimum_final_physical_cell_count":16.0,
        "capacity_growth_event_count":0.0,
        "local_radius_violation_count":0.0,
        "invalid_transition_rows":0.0,
    }

    for seed in SEEDS:
        cells=empty_cells()
        retained={}
        shared_snapshot=None
        first_exposure_ops={}
        seen_domains=[]

        for domain in range(4):
            if domain>0:
                hcount=hibernate_unique(cells,retained,domain-1)
                if hcount!=2:
                    metrics["invalid_transition_rows"]+=1
            metrics["maximum_total_hibernated_unique_bytes"]=max(
                metrics["maximum_total_hibernated_unique_bytes"],float(len(retained)*6)
            )

            train_stream,_=corpus(seed,domain,TRAIN_RECORDS,0)
            newly,radius_bad,invalid=develop_domain(cells,retained,train_stream)
            metrics["local_radius_violation_count"]+=float(radius_bad)
            metrics["invalid_transition_rows"]+=float(invalid)

            unique_keys={tuple(key) for key,_ in UNIQUE[domain]}
            unique_new=sum(1 for key in newly if tuple(key) in unique_keys)
            metrics["minimum_first_exposure_unique_specialization_count_per_domain"]=min(
                metrics["minimum_first_exposure_unique_specialization_count_per_domain"],float(unique_new)
            )
            metrics["maximum_first_exposure_unique_specialization_count_per_domain"]=max(
                metrics["maximum_first_exposure_unique_specialization_count_per_domain"],float(unique_new)
            )
            first_exposure_ops[domain]=max(1,len(train_stream)-4)

            acc=evaluate(cells,seed,domain,1)
            metrics["minimum_first_exposure_domain_accuracy"]=min(
                metrics["minimum_first_exposure_domain_accuracy"],acc
            )
            metrics["maximum_active_specialized_structure_count"]=max(
                metrics["maximum_active_specialized_structure_count"],float(active_count(cells))
            )

            shared_cells=[]
            for key,_ in SHARED:
                found=[c for c in cells if c["role"]=="specialized" and tuple(c["key"])==tuple(key)]
                if len(found)!=1:
                    metrics["invalid_transition_rows"]+=1
                else:
                    shared_cells.append(cell_signature(found[0]))
            if domain==0:
                shared_snapshot=tuple(sorted(shared_cells))
            else:
                if tuple(sorted(shared_cells))!=shared_snapshot:
                    metrics["maximum_shared_structure_mutation_count"]=max(
                        metrics["maximum_shared_structure_mutation_count"],1.0
                    )
            metrics["minimum_shared_motif_reuse_count"]=min(
                metrics["minimum_shared_motif_reuse_count"],float(len(shared_cells))
            )
            seen_domains.append(domain)

        hcount=hibernate_unique(cells,retained,3)
        if hcount!=2:
            metrics["invalid_transition_rows"]+=1
        metrics["maximum_total_hibernated_unique_bytes"]=max(
            metrics["maximum_total_hibernated_unique_bytes"],float(len(retained)*6)
        )

        for domain in range(4):
            cues=cue_keys(seed,domain)
            target_unique={tuple(key) for key,_ in UNIQUE[domain]}
            expected_matches=sum(1 for key in retained if key in target_unique)
            woke,matched,invalid=wake_from_cue(cells,retained,cues)
            metrics["invalid_transition_rows"]+=float(invalid)
            metrics["minimum_revisit_wake_count"]=min(metrics["minimum_revisit_wake_count"],float(woke))
            metrics["maximum_revisit_wake_count"]=max(metrics["maximum_revisit_wake_count"],float(woke))
            precision = 1.0 if matched==0 else woke/matched
            recall = 0.0 if expected_matches==0 else woke/expected_matches
            metrics["minimum_revisit_cue_precision"]=min(metrics["minimum_revisit_cue_precision"],precision)
            metrics["minimum_revisit_cue_recall"]=min(metrics["minimum_revisit_cue_recall"],recall)
            ratio=woke/first_exposure_ops[domain]
            metrics["maximum_wake_to_first_exposure_operation_ratio"]=max(
                metrics["maximum_wake_to_first_exposure_operation_ratio"],ratio
            )
            acc=evaluate(cells,seed,domain,3)
            metrics["minimum_revisit_domain_accuracy"]=min(metrics["minimum_revisit_domain_accuracy"],acc)
            metrics["minimum_prior_domain_retained_accuracy"]=min(metrics["minimum_prior_domain_retained_accuracy"],acc)
            metrics["maximum_active_specialized_structure_count"]=max(
                metrics["maximum_active_specialized_structure_count"],float(active_count(cells))
            )

            shared_cells=[]
            for key,_ in SHARED:
                found=[c for c in cells if c["role"]=="specialized" and tuple(c["key"])==tuple(key)]
                if len(found)==1:
                    shared_cells.append(cell_signature(found[0]))
            if tuple(sorted(shared_cells))!=shared_snapshot:
                metrics["maximum_shared_structure_mutation_count"]=max(
                    metrics["maximum_shared_structure_mutation_count"],1.0
                )

            if domain<3:
                hcount=hibernate_unique(cells,retained,domain)
                if hcount!=2:
                    metrics["invalid_transition_rows"]+=1
                metrics["maximum_total_hibernated_unique_bytes"]=max(
                    metrics["maximum_total_hibernated_unique_bytes"],float(len(retained)*6)
                )

        final_known=known_motif_count(cells,retained)
        metrics["minimum_final_known_motif_count"]=min(metrics["minimum_final_known_motif_count"],float(final_known))
        metrics["maximum_final_known_motif_count"]=max(metrics["maximum_final_known_motif_count"],float(final_known))
        metrics["maximum_final_physical_cell_count"]=max(metrics["maximum_final_physical_cell_count"],float(len(cells)))
        metrics["minimum_final_physical_cell_count"]=min(metrics["minimum_final_physical_cell_count"],float(len(cells)))
        metrics["valid_seed_count"]+=1

    assert all(math.isfinite(v) for v in metrics.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle:
        json.dump(run(),handle,allow_nan=False,separators=(",",":"))

if __name__=="__main__":
    main()
