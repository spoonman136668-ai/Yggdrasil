"use strict";
// Independent mathematics and sealed-evidence audit. Not a second learner implementation.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const r=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const pre=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
assert.equal(pre.experiment_id,"GATE13-ACTION-SELECTION-COLD-CONTINUATION-20261120");
assert.equal(r.prereg_commit,"756b97735c9042fcd2d1d3534c37ae240151d9e0");
assert.equal(r.predecessor_sha,"d9353a780e4f9107002ce4dada4b48505c834bf9");
assert.equal(r.outcome,"ACTION_CHOICE_DEVELOPMENT_NO_GO_OR_MIXED");
assert.equal(r.claims.checkpoint_bytes,1874);
assert.equal(r.claims.native_yggdrasil_first_use,false);
assert.equal(r.claims.actual_compute_advantage,false);
const expected={pair:[23000,23063,64],unary:[24000,24031,32],
 parity3:[25000,25031,32],random:[26000,26031,32]};
const sample95=(z)=>{const n=z.length,mu=z.reduce((s,v)=>s+v,0)/n;
 const vari=z.reduce((s,v)=>s+(v-mu)**2,0)/(n-1);
 return [mu-1.96*Math.sqrt(vari/n),mu+1.96*Math.sqrt(vari/n)];};
for(const [key,[first,last,num]]of Object.entries(expected)){
 const x=r.families[key];
 assert.deepEqual([x.seed_first,x.seed_last,x.seeds,x.worlds],[first,last,num,2*num]);
 for(const k of ["active","balanced","random"]){
  assert(x.means[k]>=0&&x.means[k]<=1);
  assert.equal(x.total_hypothesis_evaluations[k],96728*num);
 }
 assert.equal(x.cold_restore_success,num);
 assert.equal(x.cold_continuation_success,num);
 assert.equal(x.context_A_preservation_success,num);
 assert.deepEqual(x.checkpoint_bytes,[1874]);
 for(const [name,arm]of [["paired_balanced_minus_active","balanced"],["paired_random_minus_active","random"]]){
   const v=x[name];
   assert(Math.abs(v.mean-(x.means[arm]-x.means.active))<1e-9);
   assert(v.ci95[0]<=v.mean&&v.ci95[1]>=v.mean);
 }
}
const pair=r.families.pair,unary=r.families.unary,parity=r.families.parity3,random=r.families.random;
assert(pair.paired_balanced_minus_active.mean>=0.010);
assert(pair.paired_random_minus_active.mean>=0.010);
assert(pair.paired_balanced_minus_active.ci95[0]>0);
assert(pair.paired_random_minus_active.ci95[0]>0);
assert(unary.means.active-Math.min(unary.means.balanced,unary.means.random)<=.01);
assert(parity.means.active-Math.min(parity.means.balanced,parity.means.random)>.02);
assert(random.means.active-Math.min(random.means.balanced,random.means.random)>.02);
assert.equal(r.gates.parity_worsening_at_most_0_020,false);
assert.equal(r.gates.random_worsening_at_most_0_020,false);
assert.equal(r.gates.exact_cold_continuation_all,true);
assert.equal(r.gates.state_bytes_1874,true);
function bit(t,i){return(t>>>i)&1;}
let twoParent=0,parityMin=8;
for(let t=0;t<16;t++){
 const v=(a,b)=>bit(t,(a<<1)|b);
 if((v(0,0)!==v(1,0)||v(0,1)!==v(1,1))&&
    (v(0,0)!==v(0,1)||v(1,0)!==v(1,1)))twoParent++;
 for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){
  let mismatch=0;
  for(let x=0;x<8;x++){
   const f=v(bit(x,i),bit(x,j));
   const y=bit(x,0)^bit(x,1)^bit(x,2);
   if(f!==y)mismatch++;
  }
  parityMin=Math.min(parityMin,mismatch);
 }
}
assert.equal(twoParent,10);
assert.equal(parityMin,4);
const normalEntropy=p=>-(p*Math.log(p)+(1-p)*Math.log(1-p));
assert(Math.abs(normalEntropy(.05)-normalEntropy(.95))<1e-12);
assert(normalEntropy(.5)>normalEntropy(.05));
assert.equal(3+5*2+10*10,113);
assert.equal(2*(113*8+32+1),1874);
process.stdout.write("GATE13_INDEPENDENT_MODEL_ORDER_AUDIT_PASS PAIR_GAIN_AND_OOD_FAILURE\n");
