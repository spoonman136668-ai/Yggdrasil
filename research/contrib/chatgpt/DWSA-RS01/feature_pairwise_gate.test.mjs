import {gatePairwise,predictPairwise,RS03_SCHEMA} from './feature_pairwise_gate.mjs';
import {gateTransfer,predictTransfer} from './feature_transfer_gate.mjs';
function check(x,s){if(!x)throw Error('FAIL:'+s);}
function rejects(fn,msg){try{fn();throw Error('NO_REJECTION');}catch(e){if(e.message!==msg)throw e;}}
const featureSchemaId='public-preaction-bit-triple-v1';
const row=(id,split,key,features,raw,donor,y)=>({id,split,key,features,raw,donor,y,featureSchemaId});
const fit=[row('f1','FIT','FITKEY',[0,0,0],.5,.5,1),row('f2','FIT','FITKEY',[0,0,0],.5,.5,0)];
const oldValid=[row('o1','VALID_OLD','OLDKEY',[0,0,0],.95,.95,1)];
const novelValid=[row('n1','VALID_NOVEL','N1',[0,1,1],.5,.9,1),row('n2','VALID_NOVEL','N2',[1,0,1],.5,.9,1),row('n3','VALID_NOVEL','N3',[1,1,0],.5,.9,1)];
const args={fit,oldValid,novelValid,featureSchemaId};
const admitted=gatePairwise(args);
check(admitted.schema===RS03_SCHEMA && admitted.status==='DEV_PAIRWISE_ADMITTED'&&admitted.gamma===1,'admitted');
check(!admitted.scientificGainVerified&&!admitted.trainedDonorVerified&&admitted.protectedSourceActions===0,'no_science_claim');
const novel={featureSchemaId,key:'NEVER_SEEN',features:[1,1,1],raw:.5,donor:.9};
check(Math.abs(predictPairwise(novel,admitted)-.6)<1e-12,'unseen_triple_combination_pairwise_supported');
check(predictPairwise({...novel,donor:0,raw:.95},admitted)===.85,'unidentifiable_triple_interaction_still_harmful');
const twoId='public-preaction-bitpair-v1';
const two=(id,split,key,features,raw,donor,y)=>({...row(id,split,key,features,raw,donor,y),featureSchemaId:twoId});
const twoArgs={fit:[two('f1','FIT','K',[0,0],.5,.5,0)],oldValid:[two('o1','VALID_OLD','OLD',[0,0],.95,.95,1)],novelValid:[two('n1','VALID_NOVEL','NOVEL',[1,1],.5,.9,1)],featureSchemaId:twoId};
const rs02=gateTransfer(twoArgs),rs03=gatePairwise(twoArgs);
const unseen={featureSchemaId:twoId,key:'NEW_HELD',features:[1,0],raw:.5,donor:.9};
check(Math.abs(predictTransfer(unseen,rs02)-.6)<1e-12,'rs02_exposes_unseen_pair');
check(predictPairwise(unseen,rs03)===.5,'rs03_falls_back_for_unsupported_pair');
check(predictPairwise({...unseen,features:[1,1]},rs03)===.6,'rs03_allows_seen_pair_on_new_key');
// Pairwise minority veto: a joint [1,1] old-world regression is diluted in
// the RS02 global/single-coordinate groups, yet is visible in the RS03 pair group.
const oldMany=Array.from({length:99},(_,i)=>two('old'+i,'VALID_OLD','OLDM',i%3===0?[0,0]:i%3===1?[0,1]:[1,0],.95,.95,1));
oldMany.push(two('rare','VALID_OLD','OLDM',[1,1],.9,0,1));
const pairArgs={fit:twoArgs.fit,oldValid:oldMany,novelValid:twoArgs.novelValid,featureSchemaId:twoId};
const pairBase=gateTransfer(pairArgs),pairProtected=gatePairwise(pairArgs);
check(pairBase.gamma===1 && pairBase.candidates[0].maxOldGroupDrift<.02,'rs02_rare_interaction_diluted');
check(pairProtected.candidates[0].maxOldPairDrift>.02 && !pairProtected.candidates[0].acceptedPairwise,'pair_veto_detects_rare_old_interaction');
check(pairProtected.gamma===.5 && pairProtected.status==='DEV_PAIRWISE_ADMITTED','pairwise_downweights_donor');
rejects(()=>predictPairwise({...unseen,y:1},rs03),'PREDICTION_LABEL_PRESENT');
rejects(()=>predictPairwise({...unseen,features:[2,0]},rs03),'BAD_PREACTION_FEATURES');
rejects(()=>predictPairwise(unseen,{...rs03,pairScope:['0:1:0:0','0:1:0:0']}),'BAD_PAIR_SCOPE');
rejects(()=>predictPairwise(unseen,{...rs03,pairScope:['0:3:1:0']}),'BAD_PAIR_SCOPE');
// In two causal worlds with identical FIT/VALID rows but opposite unobserved triple outcomes,
// this predictor is identical. The opposite world is necessarily harmed by any fixed shift.
const forecast=predictPairwise(novel,admitted);
check((forecast-0)**2 > (novel.raw-0)**2 && (forecast-1)**2 < (novel.raw-1)**2,'identical_evidence_opposite_hidden_label');
console.log('DWSA_RS03_FOCUSED_PASS; old pair unsupported fallback; novel 3-way shift possible; scientific gain UNVERIFIED');

