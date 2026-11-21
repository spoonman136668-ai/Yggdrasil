"use strict";
// Independent receipt arithmetic/source-separation audit, NOT a second implementation of the learner.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const p=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
const r=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const code=fs.readFileSync(path.join(__dirname,"run.cjs"),"utf8");
assert.equal(p.experiment_id,"GATE25-DISJOINT-CAUSAL-INTERVENTION-TRANSFER-20261120");
assert.equal(r.parent_commit,"2a42430cecc25d4fea84034cf9a31d0bc1dc0715");
assert.equal(r.prereg_commit,"5f9cc9abeea1b9b339452e3229cd56fc0139d3cc");
assert.equal(r.schema,"yggdrasil.gate25.temporal-intervention-transfer.v1");
assert.deepEqual([r.worlds.trials,r.worlds.related,r.worlds.observable_bits,r.worlds.interventions,r.worlds.state_budget_bytes],[96,48,8,4,512]);
const cohorts={immediate:201000,delayed:202000,stationary:203000,pure_noise:204000};
const arms=["local","source","rolling","growing","hazard","null","no_retention"];
let controls=0;const close=(x,y)=>assert(Math.abs(x-y)<3e-9,"receipt arithmetic");
for(const [name,seed]of Object.entries(cohorts)){
 const x=r.groups[name];assert.deepEqual([x.trials,x.seed_first,x.seed_last],[24,seed,seed+23]);
 for(const metric of ["prequential_B","prequential_R","held_B","held_R"]){
  assert.deepEqual(Object.keys(x[metric]),arms);
  for(const val of Object.values(x[metric]))assert(val>=0&&val<=1,"Brier range");
 }
 assert.equal(x.cold_exact,24);assert.equal(x.source_immutable,24);assert.equal(x.held_excluded,24);assert.equal(x.world_independent_action_policy,24);
 assert(x.edited_trials>=0&&x.edited_trials<=24);assert(x.reliable_source_trials>=0&&x.reliable_source_trials<=24);
 assert(x.avg_work.local>0&&x.avg_work.global>0&&x.avg_work.hazard>0);
 controls+=x.cold_exact;
}
assert.equal(controls,96);
assert.equal(r.summary.stationary_edited_trials,7);assert.equal(r.summary.noise_edited_trials,0);
assert(r.summary.B_gain_vs_recent_global.mean<-.10);
assert(r.summary.B_gain_vs_hazard.mean<-.09);
assert(r.summary.R_held_gain_vs_recent_global.mean>.01);
assert(r.summary.R_held_gain_vs_hazard.mean<.005);
assert(r.summary.R_held_gain_vs_source_only.mean<.005);
assert(r.summary.B_gain_vs_no_retention.mean<0);
assert.equal(r.verdict,"SCIENTIFIC_NO_GO_TEMPORAL_INTERVENTION");
const failed=Object.entries(r.conditions).filter(([,yes])=>!yes).map(([k])=>k).sort();
assert.deepEqual(failed,[
"B_prequential_gain_vs_recent_global_min","B_prequential_gain_vs_recent_global_ci_lower_positive",
"B_prequential_gain_vs_hazard_min","B_prequential_gain_vs_hazard_ci_lower_positive",
"R_held_gain_vs_hazard_min","R_held_gain_vs_source_only_min",
"stationary_unnecessary_edit_trial_fraction_max",
"B_prequential_gain_vs_no_retention_ablation_min"].sort());
assert.equal(Object.keys(r.conditions).length,18);
assert.deepEqual(Object.keys(p.frozen_thresholds).sort(),Object.keys(r.conditions).sort());
assert.equal(p.frozen_thresholds.B_prequential_gain_vs_recent_global_min,.01);
assert.equal(p.frozen_thresholds.R_held_gain_vs_hazard_min,.005);
assert(code.includes('const action=(seed,t)')===false); // ensure action is a separately named function
assert(code.includes('function action(seed,t){'));
assert(code.includes('function step(seed,w,phase,st,a,prev,t,domain){'));
assert(code.includes('function localObserve(t,row){'));
assert(code.includes('function staticFit(rows){'));
assert(code.includes('const [feat,out]of rows')||code.includes('const [feat,out] of rows'));
assert(code.includes('t.stream.push(row.slice());'));
assert(code.includes('const preds=')===false); // direct prediction-before-update path
assert(code.indexOf('localObserve(local,row);controlObserve(ctrl,row);')>code.indexOf('const forecast={local:lp,...c,no_retention:no};'));
assert(code.includes('const train=')===false||code.includes('train=stage==="B"?d.B:d.R'));
console.log("GATE25_RECEIPT_AUDIT_PASS SCIENTIFIC_NO_GO_INTERVENTION_TRANSFER");
