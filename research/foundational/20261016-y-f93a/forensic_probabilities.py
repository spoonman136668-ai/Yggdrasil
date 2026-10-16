"""F93A: exact F92 frozen-score audit on consumed negative synthetic cases."""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parent
PREREG="09ccb02299d939f6337b5bbe9c1497a0a82ebf18"
F92_BLOB="7fdaf5d24866c347275c2ffa3aec7dfeaed6ac5b"
F92_WEIGHTS_BLOB="6a94f730baefe008a21f7286416f3163835ed93e"
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,digest):
 assert blob(path)==digest,("F93A_EXACT_SOURCE_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod
def analyze():
 assert blob(P/"prereg.json")==PREREG
 assert blob(R/"20261016-y-f92"/"frozen-policy.json")==F92_WEIGHTS_BLOB
 w=json.loads((R/"20261016-y-f92"/"frozen-policy.json").read_text())
 benefit=tuple(w["benefit_weights"]);harm=tuple(w["harm_weights"])
 assert hashlib.sha256(bytes(x%256 for x in benefit+harm)).hexdigest()==w["weights_sha256"]
 F92=load("f93a_f92",R/"20261016-y-f92"/"dense_path_credit.py",F92_BLOB)
 F91=F92.load("f93a_f91",R/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f93a_f90",R/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f93a_f89",R/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f93a_f88",R/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f93a_f87",R/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f93a_f86",R/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f93a_f85",R/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f93a_f84",R/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83();pack=F83.M.PACK;native=F83.M.F62
 rows=[]
 for name,seeds in (("validation",range(-5921,-5929,-1)),("guard",range(-5941,-5957,-1))):
  for seed in seeds:
   for family in (-2,-1):
    public,q,meta=F83.M.SOURCE.source(seed,family)
    assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
    state=();counts={k:0 for k in ("native_alts","overlap","benefit","harm","margin","all_three","all_four")}
    maximum_benefit=0.;minimum_harm=1.;maximum_margin=-1.
    for index,event in enumerate(public):
     baseline=native._f60_step(state,event,pack)
     if index>=24:
      proposals=native.actions(state,event,index,pack)
      matches=[z for z in proposals if z[3]==baseline]
      assert len(matches)==1
      for z in proposals:
       if z[3]==baseline:continue
       counts["native_alts"]+=1
       required=min(10,max(0,len(baseline)-1))
       overlap=sum(rec in baseline for rec in z[3])>=required
       if overlap:counts["overlap"]+=1
       vec=F91.vector(matches[0][4],z[4])
       good=F91.score(benefit,vec);bad=F91.score(harm,vec)
       b=good>=.68;h=bad<=.18;m=good-bad>=.50
       if b:counts["benefit"]+=1
       if h:counts["harm"]+=1
       if m:counts["margin"]+=1
       if b and h and m:counts["all_three"]+=1
       if b and h and m and overlap:counts["all_four"]+=1
       if overlap:
        maximum_benefit=max(maximum_benefit,good)
        minimum_harm=min(minimum_harm,bad)
        maximum_margin=max(maximum_margin,good-bad)
     state=baseline
    proposed,trace,stats=F92.online(public,benefit,harm,pack,native,F91,True)
    cert=F83.M.AUDITOR.verify(public,q,trace)
    assert cert["prefixes"]==72 and cert["max_payload_bytes"]<=144
    assert stats["interventions"]==0 and proposed==state
    assert counts["all_four"]==0
    rows.append(dict(cohort=name,seed=seed,family=family,regime=meta["arrival_regime"],
      kind=meta["question_type"],counts=counts,
      maximum_benefit_when_overlap=round(maximum_benefit,6),
      minimum_harm_when_overlap=round(minimum_harm,6),
      maximum_margin_when_overlap=round(maximum_margin,6)))
 assert len(rows)==48
 keys=tuple(rows[0]["counts"])
 totals={k:sum(r["counts"][k] for r in rows) for k in keys}
 by_cohort={name:{k:sum(r["counts"][k] for r in rows if r["cohort"]==name) for k in keys}
            for name in ("validation","guard")}
 return {"schema":"yggdrasil.f93a.frozen-f92-probability-forensics.v1",
 "stage":"CONSUMED_ONLY_RETROSPECTIVE_NOT_INDEPENDENT_SCIENCE",
 "cases":48,"validation_cases":16,"guard_cases":32,
 "totals":totals,"by_cohort":by_cohort,
 "max_benefit_overlap":max(r["maximum_benefit_when_overlap"] for r in rows),
 "min_harm_overlap":min(r["minimum_harm_when_overlap"] for r in rows),
 "max_margin_overlap":max(r["maximum_margin_when_overlap"] for r in rows),
 "exact_zero_F92_interventions":True,"retired_cohorts_not_reusable":True,
 "no_train":True,"no_protected_source":True,"no_optimizer_promotion":True,
 "rows":rows}
if __name__=="__main__":
 if sys.argv[1:]!=["--already-exposed-only"]:
  raise SystemExit("F93A refuses new source, fitting, protected or scientific originals")
 print(json.dumps(analyze(),sort_keys=True))
