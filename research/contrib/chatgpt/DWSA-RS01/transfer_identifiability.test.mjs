// RS04: deterministic source-free falsification of pairwise-coverage as a causal-transfer certificate.
// This is NOT a native Yggdrasil trial, an original-world first use, or a new science result.
import { gatePairwise, predictPairwise } from './feature_pairwise_gate.mjs';
const check=(ok,name)=>{ if(!ok) throw Error('RS04_FAIL:'+name); };
const close=(a,b)=>Math.abs(a-b)<1e-12;
const featureSchemaId='public-preaction-bit-triple-v1';
const row=(id,split,key,features,raw,donor,y)=>({id,split,key,features,raw,donor,y,featureSchemaId});
// The frozen observable records are identical across two possible causal worlds.
// All pairwise patterns of held [1,1,1] occur in the validation partition.
const args={
  fit:[row('f1','FIT','FITKEY',[0,0,0],.5,.5,0),row('f2','FIT','FITKEY',[0,0,0],.5,.5,1)],
  oldValid:[row('o1','VALID_OLD','OLDKEY',[0,0,0],.95,.95,1)],
  novelValid:[
    row('n1','VALID_NOVEL','N1',[0,1,1],.5,.9,1),
    row('n2','VALID_NOVEL','N2',[1,0,1],.5,.9,1),
    row('n3','VALID_NOVEL','N3',[1,1,0],.5,.9,1)
  ], featureSchemaId
};
const gate=gatePairwise(args);
check(gate.status==='DEV_PAIRWISE_ADMITTED' && gate.gamma===1,'admitted_on_identical_evidence');
check(!gate.trainedDonorVerified && !gate.scientificGainVerified,'no_donor_or_science_certificate');
// The novel-validation donor is merely the same constant .9. Nothing here demonstrates
// the presence of trained donor weights, causal structure, or intervention evidence.
check(new Set(args.novelValid.map(r=>r.donor)).size===1,'constant_donor_sham');
const held={key:'HELD_UNSEEN',features:[1,1,1],raw:.5,donor:.9,featureSchemaId};
for(let i=0;i<3;i++) {
  const pairFeatures=[...held.features];pairFeatures[i]=0;
  check(args.novelValid.some(r=>r.features.every((v,j)=>v===pairFeatures[j])),'pair_witness_'+i);
}
const prediction=predictPairwise(held,gate);
check(close(prediction,.6),'unseen_triple_receives_nonzero_donor');
const brier=(p,y)=>(p-y)**2;
const worlds=[0,1].map(y=>({heldOutcome:y,rawBrier:brier(held.raw,y),rs03Brier:brier(prediction,y),drift:brier(prediction,y)-brier(held.raw,y)}));
check(close(worlds[0].drift,.11),'opposite_world_harmed_by_011');
check(close(worlds[1].drift,-.09),'matching_world_helped_by_009');
// For an unknown binary outcome, a raw .5 minimizes the worst-case squared loss:
// any nonzero shift in either direction makes one indistinguishable world worse.
check(Math.max(...worlds.map(w=>w.rs03Brier))>Math.max(...worlds.map(w=>w.rawBrier)),'no_worst_case_advantage');
check(close((worlds[0].rs03Brier+worlds[1].rs03Brier)/2,.26) && close((worlds[0].rawBrier+worlds[1].rawBrier)/2,.25),'symmetric_risk_worse');
// The ambiguity is not cured by treating another arbitrary key as novel.
check(close(predictPairwise({...held,key:'ANOTHER_UNSEEN'},gate),prediction),'not_key_specific');
console.log('DWSA_RS04_IDENTIFIABILITY_FALSIFICATION_PASS',JSON.stringify({gamma:gate.gamma,prediction,worlds,worstCasePenalty:.11,heldEvidence:'identical',scientificGainVerified:false,protectedSourceActions:0}));
