"use strict";
// Independent Gate19 frozen receipt + Boolean identifiability audit.
// This is NOT an independent second implementation of the numerical learner.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const result=JSON.parse(fs.readFileSync(path.join(__dirname,"result.json"),"utf8"));
const protocol=JSON.parse(fs.readFileSync(path.join(__dirname,"prereg.json"),"utf8"));
assert.equal(protocol.id,"GATE19-RETAINED-MECHANISM-UNDER-PARENT-REMAP-20261120");
assert.equal(result.prereg_commit,"73e3e3ab872fe3a91f6d999ecbd3bb0146f77ba6");
assert.equal(result.parent_sha,"fb772d811ba3b7758c2bca13b52982fcfed6e297");
assert.equal(result.verdict,"A_TO_B_TRANSFER_MIXED_NO_GO");
assert.equal(result.design.saved_bytes,388);
const groups={majority:81000,mux:82000,essential:83000,parity:84000,unrelated:85000};
const arms=["transfer","fixed","scratch","shuffled_A","bayes_B","bayes_shared","oracle","flat","null"];
for(const [name,seed]of Object.entries(groups)){
 const x=result.groups[name];
 assert.deepEqual([x.seed_first,x.seed_last,x.seeds],[seed,seed+47,48]);
 assert.equal(x.exact_cold_restores,48);
 assert.equal(x.A_retention_exact,48);
 assert.equal(x.B_held_disjoint,48);
 assert.equal(x.A_subsets_order3,48);
 assert.equal(x.means.transfer,x.means.fixed);
 assert.deepEqual(x.gain_vs_fixed,{mean:0,ci95:[0,0]});
 assert.equal(x.means.flat,.25);
 assert.equal(x.means.null,.25);
 for(const arm of arms)assert(x.means[arm]>=0&&x.means[arm]<=1);
 assert(Math.abs(x.gain_vs_scratch.mean-(x.means.scratch-x.means.transfer))<1e-9);
 assert(Math.abs(x.gain_vs_shuffled_A.mean-(x.means.shuffled_A-x.means.transfer))<1e-9);
 assert(Math.abs(x.deficit_to_bayes_shared.mean-(x.means.transfer-x.means.bayes_shared))<1e-9);
 assert(x.transfer_accepted>=0&&x.transfer_accepted<=48);
 assert(x.shuffled_A_accepted>=0&&x.shuffled_A_accepted<=48);
 assert(x.gain_vs_scratch.ci95[0]<=x.gain_vs_scratch.mean&&x.gain_vs_scratch.mean<=x.gain_vs_scratch.ci95[1]);
}
const {majority,mux,essential,parity,unrelated}=result.groups;
assert.deepEqual([majority.transfer_accepted,mux.transfer_accepted,essential.transfer_accepted,parity.transfer_accepted,unrelated.transfer_accepted],[41,40,39,45,4]);
assert(majority.gain_vs_scratch.mean>=.025&&mux.gain_vs_scratch.mean>=.025&&parity.gain_vs_scratch.mean>=.025);
assert(essential.gain_vs_scratch.mean<.025);
assert.equal(essential.gain_vs_scratch.ci95[0]<0,true);
assert(majority.means.bayes_shared<majority.means.transfer);
assert(essential.means.bayes_shared<essential.means.transfer);
const related=[majority,mux,essential,parity];
const meanScratch=related.reduce((s,x)=>s+x.gain_vs_scratch.mean,0)/4;
const meanShuffled=related.reduce((s,x)=>s+x.gain_vs_shuffled_A.mean,0)/4;
const bayesDeficit=Math.max(...related.map(x=>x.means.transfer-x.means.bayes_shared));
assert(Math.abs(meanScratch-result.summary.mean_related_gain_vs_scratch)<1e-9);
assert(Math.abs(meanShuffled-result.summary.mean_related_gain_vs_shuffled_A)<1e-9);
assert(Math.abs(bayesDeficit-result.summary.worst_shared_bayes_deficit)<1e-9);
assert(bayesDeficit>.02);
assert.equal(unrelated.transfer_accepted/48,1/12);
assert(unrelated.means.transfer-unrelated.means.scratch<=.025);
assert.equal(result.gates.unrelated_false_share_fraction_max_0_2,true);
const failures=Object.entries(result.gates).filter(([,v])=>!v).map(([k])=>k);
assert.deepEqual(failures,[
 "essential_gain_vs_scratch_0_025",
 "worst_bayes_shared_deficit_max_0_02",
 "fixed_superiority_min_0_015",
 "fixed_superiority_ci_positive"
]);
assert.equal(240*96,23040);
assert.equal(240*24,5760);
assert.equal(240*8,1920);
assert.equal(96*2+24*2,240);
assert.equal(388-240,148);
assert.equal(5*4*3,60);
// Symmetry negative: majority and parity source functions are invariant to
// permutation of their 3 inputs. Hence physical input-map ORDER cannot be
// uniquely identified even with unlimited noiseless observations in these
// families (though its unordered parent SET may be identifiable).
function pop(x){let n=0;for(;x;x>>>=1)n+=x&1;return n;}
function source(x,kind){return kind==="majority"?(pop(x)>=2?1:0):pop(x)%2;}
const permutations=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
for(const type of ["majority","parity"])for(const perm of permutations)for(let x=0;x<8;x++){
 const y=perm.reduce((a,j)=>(a<<1)|((x>>(2-j))&1),0);
 assert.equal(source(x,type),source(y,type),"source symmetry");
}
process.stdout.write("GATE19_INDEPENDENT_AUDIT_PASS A_TO_B_TRANSFER_MIXED_FIXED_TIE\n");
