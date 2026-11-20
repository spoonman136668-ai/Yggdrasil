"use strict";
// Gate23 independent frozen-receipt arithmetic/source-separation audit.
// A passing audit verifies a recorded synthetic negative, NOT independent scientific replication.
const fs=require("fs"),path=require("path"),a=require("assert").strict;
const p=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
const r=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const code=fs.readFileSync(path.join(__dirname,"run.cjs"),"utf8");
a.equal(p.experiment_id,"GATE23-SOURCE-RELIABILITY-SEQUENTIAL-CHANGE-DETECTOR-20261120");
a.equal(r.prereg_commit,"61e43959294aa9122f64cfcb595f09dbf2e6225f");
a.equal(r.parent_commit,"7f177f61508d8eeb37458c5c38f117cadf1e4271");
a.equal(r.design.trials,192);a.equal(r.design.state_bytes,384);
const families={pair_xor:141000,mux3:142000,essential3:143000,unary:144000,stationary3:145000,noise_fair:146000};
const arms=["detector","frozen","rolling","growing","bayesian","null"];
const close=(x,y)=>a(Math.abs(x-y)<2e-9,"score arithmetic mismatch");
for(const [name,start]of Object.entries(families)){
 const g=r.groups[name];a.deepEqual([g.seed_first,g.seed_last,g.seeds],[start,start+31,32]);
 for(const stage of ["held_B","held_R","prequential_B","prequential_R"]){
  a.deepEqual(Object.keys(g[stage]),arms);
  for(const val of Object.values(g[stage]))a(val>=0&&val<=1);
 }
 a.equal(g.cold_exact,32);a.equal(g.source_immutable,32);a.equal(g.held_disjoint,32);
 a(g.false_switch_trials>=0&&g.false_switch_trials<=32);
 a(g.returned_to_source<=g.entered_alternate);
 a(g.mean_work.detector>0&&g.mean_work.rolling>0&&g.mean_work.growing>0);
 a.equal(g.mean_work.bayesianMasks,3936);
}
a.equal(r.groups.noise_fair.false_switch_trials,1);
a.equal(r.groups.stationary3.false_switch_trials,0);
a.equal(r.groups.noise_fair.source_reliable,1);
a.equal(r.summary.related_returned_to_source,127);
close(r.groups.pair_xor.held_B.detector,r.groups.pair_xor.held_B.rolling);
a.equal(r.summary.B_loss_vs_rolling.mean,0);
a.equal(r.summary.B_loss_vs_bayesian.mean<0,true);
a(r.summary.R_gain_vs_rolling.mean>.01&&r.summary.R_gain_vs_rolling.ci95[0]>0);
a(r.summary.R_gain_vs_bayesian.mean<.005&&r.summary.R_gain_vs_bayesian.ci95[0]<=0);
a(r.summary.prequential_B_loss_vs_rolling.mean>.035);
a.equal(r.verdict,"SOURCE_RELIABILITY_CHANGEPOINT_SCIENTIFIC_NO_GO");
const fails=Object.entries(r.conditions).filter(([,v])=>!v).map(([k])=>k).sort();
a.deepEqual(fails,["related_R_gain_vs_bayes_ci_lower_positive","related_R_gain_vs_bayes_min",
"related_prequential_B_regression_vs_rolling_max"].sort());
a.equal(p.frozen_thresholds.noise_false_switch_trial_fraction_max,.2);
a.equal(p.frozen_thresholds.related_prequential_B_regression_vs_rolling_max,.035);
a.equal(p.frozen_thresholds.related_R_gain_vs_bayes_min,.005);
const staticBody=code.split("function fittedStatic(rows){")[1]?.split("const lf=")[0];
a(staticBody&&staticBody.includes("for(let m=1;m<64;m++)"));
a(!staticBody.includes("sourceFit(")&&!staticBody.includes("loo(")&&!staticBody.includes("observe("));
a(code.includes("const delta=Math.round(Math.log(pb/ps)*256)"));
a(code.includes("const total=t.evidence.reduce((a,b)=>a+b,0)"));
a(code.includes("const [x,y]=(j<48?d.B[j]:d.R[j-48])"));
a(code.includes("const preds={detector:model(t,x),...controls(c,x)}"));
console.log("GATE23_RECEIPT_AUDIT_PASS SCIENTIFIC_NO_GO_PREQUENTIAL_COST_AND_BAYES_TIE");
