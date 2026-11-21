"use strict";
// Independent Gate18 mathematics and sealed-receipt audit; not a second complete learner.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const r=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const p=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
assert.equal(p.id,"GATE18-STRICT-UNSEEN-INTERVENTIONS-20261120");
assert.equal(r.prereg_commit,"666a5ef577186e2ca94998f523c6b07de9c053cc");
assert.equal(r.parent_sha,"a0cd5ef90cf3a7b931a3414cda831674ec148c91");
assert.equal(r.verdict,"STRICTLY_UNSEEN_ACTION_DEVELOPMENT_ONLY");
assert.equal(r.design.small_model_persisted_bytes,388);
const seedMap={majority:71000,mux:72000,random3:73000,parity:74000,pair:75000,unary:76000,independent:77000};
const ordered=["majority","mux","random3","parity","pair","unary","independent"];
for(const k of ordered){
 const z=r.families[k],start=seedMap[k];
 assert.deepEqual([z.seed_first,z.seed_last,z.seeds,z.worlds],[start,start+47,48,96]);
 assert.equal(z.cold_prediction_passes,48);
 assert.equal(z.disjoint_action_split_passes,48);
 assert.equal(z.exactly_matched_fixed_seeds,48);
 assert.equal(z.scores.adaptive,z.scores.fixed_full);
 assert.deepEqual(z.gain_vs_fixed,{mean:0,ci95:[0,0]});
 assert.equal(z.scores.flat,.25);
 assert.equal(z.scores.null,.25);
 assert.equal(z.held_true_parent_bins_covered+z.held_true_parent_bins_uncovered,48*16);
 for(const score of Object.values(z.scores))assert(score>=0&&score<=1);
 assert(Math.abs(z.gain_vs_flat.mean-(z.scores.flat-z.scores.adaptive))<1e-9);
 assert(z.gain_vs_flat.ci95[0]<=z.gain_vs_flat.mean&&z.gain_vs_flat.mean<=z.gain_vs_flat.ci95[1]);
 assert(z.held_coverage_brier.covered!==null);
 if(z.held_true_parent_bins_uncovered===0)assert.equal(z.held_coverage_brier.uncovered,null);
 else assert(Math.abs(z.held_coverage_brier.uncovered.adaptive-.25)<1e-12);
}
const {majority,mux,random3,parity,pair,unary,independent}=r.families;
assert.deepEqual([majority.parents_exact,mux.parents_exact,random3.parents_exact,parity.parents_exact],[94,95,76,96]);
assert.deepEqual([majority.held_true_parent_bins_uncovered,mux.held_true_parent_bins_uncovered,random3.held_true_parent_bins_uncovered,parity.held_true_parent_bins_uncovered],[0,0,4,4]);
assert.equal(r.summary.true_parent_bins_unseen_total,8);
assert.equal(r.gates.structural_gain_vs_fixed_0_015,false);
assert.equal(r.gates.structural_fixed_CI_lower_positive,false);
const falseGates=Object.entries(r.gates).filter(([,v])=>!v).map(([k])=>k);
assert.deepEqual(falseGates,["structural_gain_vs_fixed_0_015","structural_fixed_CI_lower_positive"]);
for(const z of [majority,mux,random3,parity]){
 assert(z.gain_vs_flat.ci95[0]>0);
 assert(z.scores.adaptive<.14||(z===random3&&z.scores.adaptive<.17));
}
assert(independent.scores.adaptive<=.27&&independent.false_third_order_routes===0);
assert.equal(336*2*96,64512);
assert.equal(336*2*8,5376);
assert.equal(2*(96*2+2),388);
// Information-theoretic negative: if an entire true-parent input-pattern bin
// is unobserved, two essential 3-input truth tables that differ in that bin
// are observationally indistinguishable for all allowed actions.
const trueParents=7,hiddenParentBin=7,trainX=Array.from({length:32},(_,x)=>x).filter(x=>(x&trueParents)!==hiddenParentBin);
const heldX=Array.from({length:32},(_,x)=>x).filter(x=>(x&trueParents)===hiddenParentBin);
assert.equal(trainX.length,28);
assert.equal(heldX.length,4);
const t1=0b10010110,t2=t1^(1<<hiddenParentBin);
function observedLabel(t,x){return (t>>(x&trueParents))&1;}
function essential(t){
 return [0,1,2].every(k=>Array.from({length:8},(_,x)=>x).some(x=>((t>>x)&1)!==((t>>(x^(1<<k)))&1)));
}
assert(essential(t1)&&essential(t2),"counterexample preserves three essential parents");
for(const x of trainX)assert.equal(observedLabel(t1,x),observedLabel(t2,x));
for(const x of heldX)assert.notEqual(observedLabel(t1,x),observedLabel(t2,x));
process.stdout.write("GATE18_INDEPENDENT_AUDIT_PASS UNSEEN_ACTION_TRANSFER_FIXED_TIE_MISSING_PARENT_BIN_LIMIT\n");
