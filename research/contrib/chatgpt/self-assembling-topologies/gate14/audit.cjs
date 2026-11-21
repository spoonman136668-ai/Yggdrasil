"use strict";
// Independent numerical receipt and mathematical negative-control audit.
// Does not independently reimplement the full Bayesian 113-hypothesis learner.
const fs=require("fs"),assert=require("assert").strict,path=require("path");
const result=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const prereg=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
assert.equal(prereg.id,"GATE14-MISSPECIFICATION-GUARDED-ACTIONS-20261120");
assert.equal(result.prereg_commit,"fdd63540c8ea475d253f592a80b7ecbc55fd8bf1");
assert.equal(result.predecessor_sha,"60538bf03ab8850dc0f70a9644d96e0c3e9da41a");
assert.equal(result.verdict,"GUARDED_DEVELOPMENT_NO_GO_OR_MIXED");
assert.equal(result.claims.checkpoint_bytes,1892);
const seedRanges={pair:[34000,34063,64],unary:[35000,35031,32],parity3:[36000,36031,32],random:[37000,37031,32]};
const methods=["guarded","active","balanced","random","damped_active"];
for(const [family,[start,end,num]] of Object.entries(seedRanges)){
 const z=result.families[family];
 assert.deepEqual([z.seed_first,z.seed_last,z.seeds,z.worlds],[start,end,num,2*num]);
 assert.equal(z.cold_restore_success,num);
 assert.equal(z.cold_continuation_success,num);
 assert.equal(z.context_A_preservation_success,num);
 assert.deepEqual(z.checkpoint_bytes,[1892]);
 assert(z.guarded_alarm_contexts>=0&&z.guarded_alarm_contexts<=2*num);
 for(const arm of methods){
  assert(z.means[arm]>=0&&z.means[arm]<=1);
  assert.equal(z.total_hypothesis_evaluations[arm],96728*num);
 }
 const comparisons=[["paired_balanced_minus_guarded","balanced","guarded"],
  ["paired_random_minus_guarded","random","guarded"],
  ["paired_active_minus_guarded","active","guarded"],
  ["paired_balanced_minus_active","balanced","active"],
  ["paired_random_minus_active","random","active"]];
 for(const [key,control,target] of comparisons){
  const score=z[key];
  assert(Math.abs(score.mean-(z.means[control]-z.means[target]))<1e-9);
  assert(score.ci95[0]<=score.mean&&score.mean<=score.ci95[1]);
 }
}
const {pair,unary,parity3,random}=result.families;
assert(pair.means.guarded<pair.means.balanced);
assert(pair.means.guarded>pair.means.active+.008);
assert(parity3.means.guarded<parity3.means.active-.015);
assert(random.means.guarded<random.means.active-.015);
assert(parity3.means.guarded-Math.min(parity3.means.balanced,parity3.means.random)>.015);
assert(random.means.guarded-Math.min(random.means.balanced,random.means.random)>.015);
assert(unary.means.guarded-Math.min(unary.means.balanced,unary.means.random)<=.015);
assert.equal(pair.guarded_alarm_contexts,17);
assert.equal(unary.guarded_alarm_contexts,2);
assert.equal(parity3.guarded_alarm_contexts,23);
assert.equal(random.guarded_alarm_contexts,20);
const expectedGates={
 pair_gain_balanced_min_0_010:true,pair_gain_balanced_CI_positive:true,
 pair_loss_vs_active_max_0_008:false,
 parity_worsening_vs_best_max_0_015:false,
 random_worsening_vs_best_max_0_015:false,
 parity_gain_vs_active_min_0_015:true,
 random_gain_vs_active_min_0_015:true,
 unary_worsening_vs_best_max_0_015:true,
 cold_complete:true,bytes_exact_1892:true,forced_candidate_work_equal:true
};
assert.deepEqual(result.gates,expectedGates);
function e(p){return -p*Math.log(p)-(1-p)*Math.log(1-p);}
assert(e(.5)>e(.05));
// Predictive entropy is not exactly mutual information: a known fair
// outcome with no model uncertainty still has maximum Bernoulli entropy.
assert.equal(3+5*2+10*10,113);
assert.equal(2*(113*8+32+1+6+1+1+1),1892);
process.stdout.write("GATE14_INDEPENDENT_MATH_AND_RECEIPT_AUDIT_PASS DEFENSIVE_TRADEOFF_NO_GO\n");
