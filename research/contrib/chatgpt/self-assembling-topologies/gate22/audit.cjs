"use strict";
// Gate22 independently rechecks numeric receipts, frozen thresholds and source separation.
// This is NOT an independently implemented second causal learner or external-science reproduction.
const assert=require("assert").strict,fs=require("fs"),path=require("path");
const prereg=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
const result=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const source=fs.readFileSync(path.join(__dirname,"run.cjs"),"utf8");
assert.equal(prereg.experiment_id,"GATE22-CAUSAL-CHANGEPOINT-COLD-REACTIVATION-20261120");
assert.equal(result.prereg_commit,"a4ad408eb9e4032407962ac06e4b14bd3a8e290a");
assert.equal(result.parent_commit,"eb44df75612be0aaa6ee388a08f308eb8fc8dc39");
assert.equal(result.design.seeds,192);
assert.equal(result.design.saved_state_bytes,384);
assert.equal(result.design.oracle_info_advantaged,true);
assert.equal(result.verdict,"CHANGEPOINT_MIXED_OR_NEGATIVE_DEV");
const cohorts={xor_pair:121000,mux3:122000,essential3:123000,unary:124000,
 stationary_essential3:125000,independent_noise:126000};
const keys=["gated","frozen","growing","sliding","bayes","ungated","null","oracle"];
let cold=0,held=0,sourceReturn=0;
for(const [family,seed]of Object.entries(cohorts)){
 const g=result.groups[family];assert.deepEqual([g.seeds,g.seed_first,g.seed_last],[32,seed,seed+31]);
 for(const stage of ["held_B","held_R","prequential_B","prequential_R"]){
  assert.deepEqual(Object.keys(g[stage]),keys);
  for(const [arm,v]of Object.entries(g[stage]))assert(v>=0&&v<=1,stage+" "+arm);
 }
 assert(g.cold_exact===32 && g.held_disjoint===32 && g.source_immutable===32,
  family+" custody");
 assert(g.any_mode_switch>=0&&g.any_mode_switch<=32);
 assert(g.source_reactivated<=g.ever_entered_new);
 for(const v of Object.values(g.mean_work))assert(v>=0);
 const close=(x,y)=>assert(Math.abs(x-y)<2e-9,"rounded arithmetic");
 close(g.held_B.frozen-g.held_B.gated,g.B_gain_vs_frozen.mean);
 close(g.held_B.gated-g.held_B.sliding,g.B_gated_minus_sliding.mean);
 close(g.held_R.sliding-g.held_R.gated,g.return_gain_vs_sliding.mean);
 close(g.held_R.bayes-g.held_R.gated,g.return_gain_vs_bayes.mean);
 cold+=g.cold_exact;held+=g.held_disjoint;
 sourceReturn+=g.source_reactivated;
}
assert.equal(cold,192);assert.equal(held,192);
assert.equal(result.summary.source_reactivated_related,110);
assert.equal(result.summary.stationary_false_switch_trials,3);
assert.equal(result.summary.noise_false_switch_trials,26);
assert(result.summary.related_B_gain_vs_frozen_A.mean>=.045);
assert(result.summary.related_B_gated_minus_sliding.mean>.02);
assert(result.summary.related_B_gated_minus_bayes.mean>.025);
assert(result.summary.related_R_gain_vs_sliding.mean>=.012);
assert(result.summary.related_R_gain_vs_bayes.mean<.005);
assert(result.summary.related_R_gain_vs_bayes.ci95[0]<=0);
assert.equal(prereg.frozen_thresholds.related_return_gain_vs_hazard_bayes_min,.005);
assert.equal(prereg.frozen_thresholds.noise_false_mode_switch_trials_max_fraction,.2);
assert.deepEqual(Object.entries(result.conditions).filter(([,v])=>!v).map(([k])=>k).sort(),[
"related_B_regression_vs_sliding_max",
"related_B_regression_vs_hazard_bayes_max",
"related_return_gain_vs_hazard_bayes_min",
"related_return_gain_vs_hazard_bayes_ci_lower_positive",
"noise_false_mode_switch_trials_max_fraction",
"noise_holdout_Brier_regression_vs_null_max"].sort());
// Source fencing: independent fixed selector must not invoke local selector or feed mutations.
const selector=source.split("function fitStatic(rows){")[1]?.split("function fresh(")[0];
assert(selector&&selector.includes("for(let mask=1;mask<64;mask++)"));
assert(!selector.includes("neighbors(")&&!selector.includes("gatedUpdate(")&&
 !selector.includes("maskBest(")&&!selector.includes("loo("));
assert(source.includes("const last=s.rows.slice(-Math.min(n,32)),fit=last.slice(0,-8),val=last.slice(-8)"));
assert(source.includes("const [x,y]=stream[t]"));
assert(source.includes("gatedUpdate(s,[x,y]);controlUpdate(ctrl,[x,y],control)"));
console.log("GATE22_RECEIPT_AUDIT_PASS SCIENTIFIC_NO_GO_FALSE_NOISE_SWITCH_AND_B_CONTROL_LOSS");
