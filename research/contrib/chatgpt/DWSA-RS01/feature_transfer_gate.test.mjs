// Focused source-free tests only. Run: node feature_transfer_gate.test.mjs
import {gateTransfer,predictTransfer,RS02_SCHEMA} from "./feature_transfer_gate.mjs";
function check(value,name){if(!value)throw Error("FAIL:"+name);}
function rejects(fn,msg){try {fn();throw Error("NO_REJECTION");}catch(e){if(e.message!==msg)throw e;}}
const featureSchemaId="public-preaction-bitpair-v1";
const row=(id,split,key,features,raw,donor,y)=>({id,split,key,features,raw,donor,y,featureSchemaId});
const fit=[row("f1","FIT","FITKEY",[0,0],.5,.5,1),row("f2","FIT","FITKEY",[0,0],.5,.5,0)];
const old=[row("o1","VALID_OLD","OLDKEY",[0,0],.9,.9,1)];
const novel=[row("n1","VALID_NOVEL","NEWKEY",[1,1],.5,.9,1)];
const args={fit,oldValid:old,novelValid:novel,featureSchemaId:"public-preaction-bitpair-v1"};
const good=gateTransfer(args);
check(good.schema===RS02_SCHEMA&&good.status==="DEV_VALIDATION_ADMITTED"&&good.gamma===1,"admit");
check(!good.scientificGainVerified&&!good.trainedDonorVerified&&good.protectedSourceActions===0,"no_false_science");
const unseen={key:"NEVER_VALIDATED_KEY",features:[1,0],raw:.5,donor:.9,featureSchemaId};
check(Math.abs(predictTransfer(unseen,good)-.6)<1e-12,"unseen_key_unseen_feature_combination_nonzero_transfer");
check(predictTransfer({featureSchemaId,key:"HELD",features:[1,0],raw:.95,donor:0},good)===.85,"bounded_donor_delta");
const unsupported=gateTransfer({...args,novelValid:[row("n2","VALID_NOVEL","NEWKEY",[0,0],.5,.9,1)]});
check(predictTransfer({featureSchemaId,key:"OTHER",features:[1,0],raw:.95,donor:0},unsupported)===.95,"unsupported_marginal_raw_fallback");
const bad=gateTransfer({...args,novelValid:[row("n3","VALID_NOVEL","NEWKEY",[1,1],.9,0,1)]});
check(bad.status==="DEV_VALIDATION_REJECTED"&&bad.gamma===0&&Object.keys(bad.capsules.cells).length===0,"reject_atomic");
check(predictTransfer(unseen,bad)===.5,"reject_raw_restore");
const minorFit=Array.from({length:20},(_,i)=>row("mf"+i,"FIT","RARE",[0,0],.9,.9,0));
const common=Array.from({length:99},(_,i)=>row("o"+i,"VALID_OLD","COMMON",[0,0],.95,.95,1));
common.push(row("rare","VALID_OLD","RARE",[1,0],1,0,1));
const minor=gateTransfer({fit:minorFit,oldValid:common,novelValid:novel,featureSchemaId:"public-preaction-bitpair-v1"});
check(minor.candidates[0].oldDrift<.02&&minor.candidates[0].maxOldGroupDrift>.02,"minority_veto_proven");
check(minor.status==="DEV_VALIDATION_ADMITTED"&&minor.gamma===.25,"minority_forces_smallest_gamma_not_full_veto");
check(predictTransfer({featureSchemaId,key:"RARE",features:[1,0],raw:1,donor:0},minor)===.875,"minority_residual_risk_documented");
// No held label or future outcome is permitted in prediction calls.
rejects(()=>predictTransfer({...unseen,y:1},good),"PREDICTION_LABEL_PRESENT");
rejects(()=>predictTransfer({...unseen,features:[1,2]},good),"BAD_PREACTION_FEATURES");
rejects(()=>predictTransfer({...unseen,featureSchemaId:"other"},good),"FEATURE_SCHEMA_MISMATCH");
rejects(()=>predictTransfer({...unseen,raw:NaN},good),"BAD_PROBABILITY");
rejects(()=>predictTransfer(unseen,{...good,supportedValues:[[0,0],[0,1]]}),"BAD_FEATURE_SCOPE");
rejects(()=>predictTransfer(unseen,{...good,capsules:{...good.capsules,cells:{BAD:.5}}}),"BAD_CAPSULE_SHIFT");
rejects(()=>gateTransfer({...args,novelValid:[row("o1","VALID_NOVEL","NEWKEY",[1,1],.5,.9,1)]}),"DUPLICATE_ROW_ID");
rejects(()=>gateTransfer({...args,novelValid:[row("n5","VALID_NOVEL","FITKEY",[1,1],.5,.9,1)]}),"NOVEL_KEY_OVERLAP");
rejects(()=>gateTransfer({...args,featureSchemaId:"../../bad"}),"BAD_FEATURE_SCHEMA_ID");
rejects(()=>gateTransfer({...args,fit:[{...fit[0],featureSchemaId:"changed"}] }),"FEATURE_SCHEMA_MISMATCH");
check(fit.every(r=>r.y===0||r.y===1)&&old[0].key==="OLDKEY","inputs_unchanged");
// Negative: unseen feature *combination* is not the same thing as an unfamiliar causal law.
// An anti-correlated donor on that combo would still shift the forecast; this is not a retention proof.
check(predictTransfer({featureSchemaId,key:"CAUSAL_LAW_SHIFT",features:[1,0],raw:.95,donor:.05},good)===.85,"unmodeled_interaction_risk_explicit");
console.log("DWSA_RS02_SOURCE_FREE_FOCUSED=PASS; feature-transfer possible; original actions=0; scientific gain=UNVERIFIED");
