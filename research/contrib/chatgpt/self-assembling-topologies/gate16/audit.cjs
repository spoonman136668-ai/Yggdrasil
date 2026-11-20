"use strict";
// Independent mathematics and frozen-receipt audit; numerical replay separate.
// This does NOT independently reimplement the whole learner.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const r=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const p=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
assert.equal(p.id,"GATE16-THIRD-ORDER-WALSH-CAUSAL-INTERACTIONS-20261120");
assert.equal(r.prereg_commit,"860487bed0498cc22dc26f93b4b7ed157c799163");
assert.equal(r.predecessor_sha,"2271e6d641da350b3b10729fd52c49a9af0118a7");
assert.equal(r.verdict,"REPRESENTATIONAL_GAIN_ONLY_NOT_STRUCTURAL");
assert.equal(r.design.small_packed_bytes,388);
assert.equal(r.design.unmatched_bayes_posterior_bytes,816);
const sets={triple:[51000,51063,64],pair:[52000,52031,32],unary:[53000,53031,32],random:[54000,54031,32],majority:[55000,55031,32]};
for(const [name,[first,last,n]]of Object.entries(sets)){
 const z=r.families[name];
 assert.deepEqual([z.first_seed,z.last_seed,z.seeds,z.worlds],[first,last,n,2*n]);
 assert.equal(z.cold_prediction_passes,n);
 assert.equal(z.exact_fixed_tie_seeds,n);
 assert(Math.abs(z.scores.expanded_dynamic-z.scores.fixed_full)<1e-12);
 assert.deepEqual(z.gain_over_fixed,{mean:0,ci95:[0,0]});
 for(const val of Object.values(z.scores))assert(val>=0&&val<=1);
 const gain=z.scores.truncated-z.scores.expanded_dynamic;
 assert(Math.abs(gain-z.gain_over_truncated.mean)<1e-9);
 assert(z.gain_over_truncated.ci95[0]<=gain&&z.gain_over_truncated.ci95[1]>=gain);
 assert(z.feature_fit_comparisons.expanded_dynamic<=z.feature_fit_comparisons.fixed_full);
}
const {triple,pair,unary,random,majority}=r.families;
assert.equal(triple.triple_parent_recovered,128);
assert.equal(triple.high_order_candidate_expansions,128);
assert(triple.gain_over_truncated.mean>.1);
assert(triple.gain_over_truncated.ci95[0]>0);
assert.equal(random.false_parity_routes,0);
assert.equal(majority.false_parity_routes,0);
assert(random.scores.expanded_dynamic<=.27&&majority.scores.expanded_dynamic<=.27);
assert(pair.scores.expanded_dynamic-pair.scores.truncated<=.015);
assert(unary.scores.expanded_dynamic-unary.scores.truncated<=.015);
assert(majority.scores.flat+.10<majority.scores.expanded_dynamic);
assert(triple.scores.bayes<=triple.scores.expanded_dynamic);
const falseGates=Object.entries(r.gates).filter(([,v])=>!v).map(([k])=>k);
assert.deepEqual(falseGates,["structural_gain_vs_fixed_min_0_015","structural_gain_fixed_CI_lower_positive"]);
function parity(x){let n=0;for(;x;x>>>=1)n+=x&1;return n&1;}
let mismatchMinimum=8;
for(let mask=1;mask<8;mask++)if(mask===3||mask===5||mask===6){
 for(let table=0;table<16;table++){
  let mismatches=0;
  for(let x=0;x<8;x++){
   const included=[0,1,2].filter(i=>(mask>>i)&1);
   const idx=(((x>>included[0])&1)<<1)|((x>>included[1])&1);
   const pred=(table>>idx)&1;
   if(pred!==parity(x))mismatches++;
  }mismatchMinimum=Math.min(mismatchMinimum,mismatches);
 }
}
assert.equal(mismatchMinimum,4,"two-input Boolean function cannot encode triple parity");
let tripleWalsh=0;
for(let x=0;x<8;x++){
 const majority=(x.toString(2).split("1").length-1)>=2?1:0;
 tripleWalsh+=(2*majority-1)*(parity(x)?-1:1)/8;
}
assert(Math.abs(tripleWalsh-.5)<1e-12,"three-way majority interaction only 0.5");
assert.equal(5+10+10,25);
assert.equal(2*(96*2+2),388);
assert.equal(2*51*8,816);
process.stdout.write("GATE16_INDEPENDENT_BASIS_AND_RECEIPT_AUDIT_PASS REPRESENTATIONAL_ONLY\n");
