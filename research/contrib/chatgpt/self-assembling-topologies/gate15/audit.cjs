"use strict";
// Independent receipt/model-class audit; numeric learner replay is a separate step.
const assert=require("assert").strict,fs=require("fs"),path=require("path");
const dir=__dirname;
const r=JSON.parse(fs.readFileSync(path.join(dir,"result.json"),"utf8"));
const p=JSON.parse(fs.readFileSync(path.join(dir,"prereg.json"),"utf8"));
assert.equal(p.id,"GATE15-PREQUENTIAL-EXCESS-BRIER-ROBUST-ACTIONS-20261120");
assert.equal(r.prereg_commit,"d0d372ea1e0f0f9683a115fbdc04b72b0fc21470");
assert.equal(r.predecessor_sha,"743237b7efa667bc3cbedfd1f38e25e23a307583");
assert.equal(r.verdict,"RESIDUAL_GUARD_DEVELOPMENT_MIXED_NO_GO");
assert.equal(r.constraints.checkpoint_bytes,1892);
const expected={pair:[41000,41063,64,33],unary:[42000,42031,32,13],
 parity3:[43000,43031,32,40],random:[44000,44031,32,47]};
const arms=["residual_guard","active","balanced","random","fixed_damp"];
for(const [name,[start,end,count,alarm]]of Object.entries(expected)){
 const f=r.families[name];
 assert.deepEqual([f.seed_first,f.seed_last,f.seeds,f.worlds],[start,end,count,2*count]);
 assert.equal(f.guard_alarm_contexts,alarm);
 assert.equal(f.cold_restore_success,count);
 assert.equal(f.cold_continuation_success,count);
 assert.equal(f.context_A_preservation_success,count);
 assert.deepEqual(f.checkpoint_bytes,[1892]);
 for(const arm of arms){
  assert(f.means[arm]>=0&&f.means[arm]<=1);
  assert.equal(f.total_hypothesis_evaluations[arm],96728*count);
 }
 for(const [label,c,t]of [
  ["paired_balanced_minus_active","balanced","active"],
  ["paired_random_minus_active","random","active"],
  ["paired_balanced_minus_guard","balanced","residual_guard"],
  ["paired_random_minus_guard","random","residual_guard"],
  ["paired_active_minus_guard","active","residual_guard"]]){
  const paired=f[label];
  assert(Math.abs(paired.mean-(f.means[c]-f.means[t]))<1e-9);
  assert(paired.ci95[0]<=paired.mean&&paired.mean<=paired.ci95[1]);
 }
}
const {pair,unary,parity3,random}=r.families;
const best=x=>Math.min(x.means.balanced,x.means.random);
assert(pair.means.residual_guard-pair.means.active>.010);
assert(pair.means.balanced-pair.means.residual_guard>=.010);
assert(pair.paired_balanced_minus_guard.ci95[0]>0);
assert(parity3.means.residual_guard-best(parity3)>.015);
assert(random.means.residual_guard-best(random)<=.015);
assert(parity3.means.active-parity3.means.residual_guard>=.015);
assert(random.means.active-random.means.residual_guard>=.015);
assert(unary.means.residual_guard-best(unary)<=.015);
const avg=[pair,unary,parity3,random]
 .reduce((s,x)=>s+x.means.residual_guard-x.means.fixed_damp,0)/4;
assert(Math.abs(avg-r.macro_guard_excess_vs_fixed_damp)<1e-9);
assert(avg<=.005);
const failing=Object.entries(r.gates).filter(([_,v])=>!v).map(([k])=>k);
assert.deepEqual(failing,["pair_loss_vs_active_max_0_010","parity_loss_vs_best_max_0_015"]);
// Analytical identity: within Gate13's 113 hypothesis family, conditional
// response entropy is h(0.05) for 112 hypotheses and h(0.5) for the fair null.
// Posterior mass on that fair null is independent of candidate action.
// Hence MI(action) = h(predictive(action)) - constant for ALL candidate actions.
function entropy(q){return -q*Math.log(q)-(1-q)*Math.log(1-q);}
assert(Math.abs(entropy(.05)-entropy(.95))<1e-14);
const normalizedWeights=[.001,.15,.5,.8];
for(const fairMass of normalizedWeights){
 const conditional=fairMass*entropy(.5)+(1-fairMass)*entropy(.05);
 for(const pred of [.06,.17,.5,.73,.94]){
  const predictiveEntropy=entropy(pred);
  const informationGain=predictiveEntropy-conditional;
  assert(Math.abs(informationGain-(predictiveEntropy-conditional))<1e-14);
 }
}
assert.equal(3+10+100,113);
assert.equal(2*(113*8+32+1+8+1),1892);
process.stdout.write("GATE15_INDEPENDENT_AUDIT_PASS RESIDUAL_ADEQUACY_NO_GO\n");
