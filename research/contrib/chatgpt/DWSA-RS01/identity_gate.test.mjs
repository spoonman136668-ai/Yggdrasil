// Source-free deterministic interface checks. Run: node identity_gate.test.mjs
import {fitCapsules,predict,gateDonor,RS01_SCHEMA} from "./identity_gate.mjs";
function assert(ok,label){if(!ok)throw Error("TEST_FAIL:"+label);}
function rejects(fn,expected){try{fn();throw Error("NO_REJECTION");}catch(e){if(e.message!==expected)throw e;}}
const row=(id,split,key,raw,donor,y)=>({id,split,key,raw,donor,y});
const fit=[row("f1","FIT","A",.5,.9,1),row("f2","FIT","A",.5,.1,0)];
const oldValid=[row("o1","VALID_OLD","OLD",.9,.9,1)];
const novelValid=[row("n1","VALID_NOVEL","NEW",.5,.9,1)];
const good=gateDonor({fit,oldValid,novelValid});
assert(good.schema===RS01_SCHEMA&&good.status==="VALIDATION_ADMITTED"&&good.gamma===1,"positive_admission");
assert(good.scientificGainVerified===false&&good.protectedSourceActions===0,"no_scientific_claim");
const denied=gateDonor({fit,oldValid:[row("o2","VALID_OLD","OLD",.9,0,1)],novelValid});
assert(denied.status==="VALIDATION_REJECTED"&&denied.gamma===0,"old_retention_gate");
assert(JSON.stringify(good.proposedCapsules)===JSON.stringify(denied.proposedCapsules),"validation_not_used_to_fit");
assert(predict({key:"unseen",raw:.27,donor:.91},good.capsules,0)===.27,"identity_fallback");
assert(Object.keys(denied.capsules.cells).length===0,"rejected_donor_has_no_active_repairs");
const correctedFit=[row("f3","FIT","REPAIR",.1,.9,1)];
const refused=gateDonor({fit:correctedFit,oldValid:[row("o3","VALID_OLD","OLD",.9,0,1)],novelValid});
assert(refused.status==="VALIDATION_REJECTED","repair_candidate_refused");
assert(refused.proposedCapsules.cells.REPAIR>0,"positive_proposed_repair");
assert(predict({key:"REPAIR",raw:.33,donor:.99},refused.capsules,refused.gamma)===.33,"rejected_repair_rollback");
const twenty=Array.from({length:20},(_,i)=>row("i"+i,"FIT","cell"+i,.1,.2,1));
assert(Object.keys(fitCapsules(twenty).cells).length===16,"bounded_capacity");
rejects(()=>fitCapsules([row("x","HELD","A",.2,.3,1)]),"SPLIT_VIOLATION");
rejects(()=>fitCapsules([row("x","FIT","A",NaN,.3,1)]),"BAD_PROBABILITY");
rejects(()=>fitCapsules([row("x","FIT","A",.2,.3,2)]),"BAD_LABEL");
rejects(()=>gateDonor({fit,oldValid:[row("f1","VALID_OLD","A",.2,.3,1)],novelValid}),"DUPLICATE_ROW_ID");
rejects(()=>predict(novelValid[0],{...good.capsules,cells:{NEW:.9}},0),"BAD_CAPSULE_SHIFT");
rejects(()=>predict(novelValid[0],good.capsules,.1),"BAD_GAMMA");
assert(Object.prototype.hasOwnProperty.call(fitCapsules([row("x","FIT","__proto__",.2,.5,1)]).cells,"__proto__"),"safe_context_storage");
console.log("DWSA_RS01_FOCUSED_TESTS=PASS; no original-world actions");
