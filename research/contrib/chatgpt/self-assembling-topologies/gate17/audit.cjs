"use strict";
// Gate17 independent math, bounds and receipt audit; NOT a second full learner.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const r=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const p=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
assert.equal(p.id,"GATE17-GENERIC-BOOLEAN-INTERACTION-INDUCTION-20261120");
assert.equal(r.prereg_commit,"47b2597c81ca990cf5947c59be145fbb972d0af4");
assert.equal(r.parent_sha,"beced851de76e4cfedf854d29c55cbbea2ec6eac");
assert.equal(r.verdict,"NONLINEAR_REPRESENTATION_DEV_ONLY");
assert.equal(r.design.small_state_bytes,388);
const expected={majority:[61000,61031,62],mux:[62000,62031,64],
 random3:[63000,63031,49],parity:[64000,64031,64],
 pair:[65000,65031,0],unary:[66000,66031,0],independent:[67000,67031,0]};
for(const [key,[a,b,parents]] of Object.entries(expected)){
 const f=r.families[key];
 assert.deepEqual([f.seed_first,f.seed_last,f.seeds,f.worlds],[a,b,32,64]);
 assert.equal(f.parents_exact,parents);
 assert.equal(f.cold_prediction_passes,32);
 assert.equal(f.exactly_matched_fixed_seeds,32);
 assert.equal(f.gain_vs_fixed.mean,0);
 assert.deepEqual(f.gain_vs_fixed.ci95,[0,0]);
 assert.equal(f.scores.adaptive,f.scores.fixed_full);
 assert.equal(f.false_third_order_routes,0);
 for(const score of Object.values(f.scores))assert(score>=0&&score<=1);
 assert(Math.abs(f.gain_vs_parity.mean-(f.scores.parity_only-f.scores.adaptive))<1e-9);
 assert(Math.abs(f.difference_vs_bayes.mean-(f.scores.adaptive-f.scores.bayes))<1e-9);
 assert(f.gain_vs_parity.ci95[0]<=f.gain_vs_parity.mean&&f.gain_vs_parity.ci95[1]>=f.gain_vs_parity.mean);
}
const {majority,mux,random3,parity,pair,unary,independent}=r.families;
assert(majority.scores.adaptive<.13&&mux.scores.adaptive<.13);
assert(random3.scores.adaptive<.16&&parity.scores.adaptive<.13);
assert(majority.gain_vs_parity.mean>.05&&mux.gain_vs_parity.mean>.05&&random3.gain_vs_parity.mean>.03);
assert(pair.scores.adaptive-pair.scores.truncated<=.01);
assert(unary.scores.adaptive-unary.scores.truncated<=.01);
assert(independent.scores.adaptive<=.27);
const saving=1-(pair.work.adaptive+unary.work.adaptive)/(pair.work.fixed_full+unary.work.fixed_full);
assert(Math.abs(saving-r.summary.lower_order_fit_work_saving)<1e-9);
assert(saving>=.20);
const maxBayes=Math.max(majority,mux,random3,parity);
assert(Math.abs(r.summary.max_bayes_deficit-
  Math.max(...[majority,mux,random3,parity].map(x=>x.scores.adaptive-x.scores.bayes)))<1e-9);
assert(r.summary.max_bayes_deficit<.015);
assert.equal(r.gates.structural_gain_fixed_0_015,false);
assert.equal(r.gates.structural_gain_fixed_CI_lower_positive,false);
assert(Object.entries(r.gates).filter(([,v])=>!v).length===2);
function bit(x,k){return(x>>k)&1;}
function essential(t){return [0,1,2].every(k=>(()=>{
 for(let x=0;x<8;x++)if(bit(t,x)!==bit(t,x^(1<<(2-k))))return true;
 return false;})());}
let e=0;
for(let table=0;table<256;table++)if(essential(table))e++;
assert(e>0&&e<256);
function mux(x){const a=bit(x,2),b=bit(x,1),c=bit(x,0);return a?c:b;}
function maj(x){return bit(x,2)+bit(x,1)+bit(x,0)>=2?1:0;}
for(const fn of [mux,maj]){
 const table=Array.from({length:8},(_,x)=>fn(x)).reduce((a,v,x)=>a|(v<<x),0);
 assert(essential(table),"all three Boolean source parents are essential");
}
assert.equal(2*(96*2+2),388);
assert.equal(7*32,224);
assert.equal(224*2*96,43008);
assert.equal(224*2*32,14336);
process.stdout.write("GATE17_INDEPENDENT_BOOLEAN_AUDIT_PASS NONLINEAR_REPRESENTATION_NOT_SELF_ASSEMBLY\n");
