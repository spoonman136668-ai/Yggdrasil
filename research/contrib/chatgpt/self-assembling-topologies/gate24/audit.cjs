"use strict";
// Gate24 independent source/receipt audit: it is NOT independent scientific replication.
const fs=require("fs"),p=require("path"),assert=require("assert").strict;
const pre=JSON.parse(fs.readFileSync(p.join(__dirname,"prereg.json"),"utf8"));
const r=JSON.parse(fs.readFileSync(p.join(__dirname,"result.json"),"utf8"));
const src=fs.readFileSync(p.join(__dirname,"run.cjs"),"utf8");
assert.equal(pre.experiment_id,"GATE24-LOCAL-SOFT-CAUSAL-BRIDGE-20261120");
assert.equal(r.prereg_commit,"e966549d2e689842ea0dafcf4ebd03bce2d778eb");
assert.equal(r.parent_commit,"eb825ad1fb3b0722da398e9b92794c4ea0f28d7d");
assert.equal(r.schema,"yggdrasil.gate24.local-soft-bridge.v1");
assert.deepEqual([r.design.trials,r.design.soft_state_bytes,r.design.hard_state_bytes],[192,384,384]);
const fam={pair_xor:161000,mux3:162000,essential3:163000,unary:164000,stationary3:165000,noise_fair:166000};
const arms=["detector","local_soft","global_soft","frozen","rolling","growing","bayesian","null"];
const close=(a,b)=>assert(Math.abs(a-b)<3e-9,"paired summary arithmetic mismatch");
for(const [name,start]of Object.entries(fam)){
 const z=r.groups[name];
 assert.deepEqual([z.seed_first,z.seed_last,z.seeds],[start,start+31,32]);
 for(const metric of ["held_B","held_R","prequential_B","prequential_R"]){
  assert.deepEqual(Object.keys(z[metric]),arms);
  for(const val of Object.values(z[metric]))assert(val>=0&&val<=1,"Brier range");
 }
 assert.equal(z.cold_exact,32);assert.equal(z.soft_cold_exact,32);
 assert.equal(z.source_immutable,32);assert.equal(z.held_disjoint,32);
 assert(z.soft_local_edited_trials>=0&&z.soft_local_edited_trials<=32);
 assert(z.soft_global_refit_changed_trials>=0&&z.soft_global_refit_changed_trials<=32);
 for(const v of Object.values(z.mean_work))assert(Number.isFinite(v)&&v>=0,"work");
 assert.equal(z.mean_work.bayesianMasks,3936);
}
assert.equal(r.groups.noise_fair.soft_local_edited_trials,0);
assert.equal(r.groups.stationary3.soft_local_edited_trials,28);
assert(r.summary.B_gain_vs_hard.mean>.02&&r.summary.B_gain_vs_hard.ci95[0]>0);
assert(r.summary.B_loss_vs_rolling.mean>.015&&r.summary.B_loss_vs_bayes.mean>.015);
assert(r.summary.R_gain_vs_rolling.mean>.01&&r.summary.R_gain_vs_rolling.ci95[0]>0);
assert(r.summary.R_gain_vs_bayes.mean<.005&&r.summary.R_gain_vs_bayes.ci95[0]<=0);
assert(r.summary.R_gain_vs_global_soft.mean<.005);
assert(r.summary.B_loss_vs_global_soft.mean>.01);
assert.equal(r.verdict,"LOCAL_SOFT_BRIDGE_SCIENTIFIC_NO_GO");
const failures=Object.entries(r.conditions).filter(([,v])=>!v).map(([k])=>k).sort();
assert.deepEqual(failures,[
"related_B_prequential_regression_vs_rolling_max","related_B_prequential_regression_vs_Bayes_max",
"related_R_held_gain_vs_Bayes_min","related_R_held_gain_vs_Bayes_CI_lower_positive",
"related_R_held_gain_vs_global_soft_min","related_B_prequential_regression_vs_global_soft_max",
"stationary_false_local_graph_edit_trials_max_fraction"].sort());
assert.equal(Object.keys(r.conditions).length,18);
assert.deepEqual(Object.keys(pre.frozen_thresholds).sort(),Object.keys(r.conditions).sort());
assert.equal(pre.frozen_thresholds.related_R_held_gain_vs_Bayes_min,.005);
assert.equal(pre.frozen_thresholds.related_B_prequential_regression_vs_rolling_max,.015);
assert(src.includes('function softObserve(t,row){')&&src.includes('if(t.kind==="global")'));
assert(src.includes('const delta=Math.round(Math.log(pb/ps)*256)')); // unchanged original hard detector
assert(src.includes('Math.round(32*Math.log(p1/p0))')); // new prequential soft evidence
assert(src.includes('const preds={detector:model(t,x),local_soft:softForecast(local,x)'));
assert(src.includes('softLocal:local.work,softGlobal:global.work'));
assert(src.includes('const [x,y]=(j<48?d.B[j]:d.R[j-48])'));
const staticSelector=src.split('function fittedStatic(rows){')[1]?.split('const lf=')[0];
assert(staticSelector&&staticSelector.includes('for(let m=1;m<64;m++)'));
assert(!staticSelector.includes('softNeighbors(')&&!staticSelector.includes('softObserve('));
console.log("GATE24_RECEIPT_AUDIT_PASS SCIENTIFIC_NO_GO_ONLINE_REGRET_STATIONARY_EDIT");
