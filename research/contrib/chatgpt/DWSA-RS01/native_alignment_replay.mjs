// RS01 reproducible read-only retrospective Yggdrasil native/Jepa replay.
// No environment import, donor training, test-world stepping, checkpoint write,
// production learner change, or protected first-use. CONSUNMED DATA diagnostic.
// Run with Node 22+:
// node native_alignment_replay.mjs /path/to/pinned-pr1278/selection-dev-01/trace.json
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {gateDonor, predict} from "./identity_gate.mjs";

const SOURCE_PR1278_HEAD="86264b41a08d49f558418c0fba367f3a2636befa";
const TRACE_BLOB_SHA1="9db0d3742fc8bd009c61d0864e4aba739a19e4e1";
const TRACE_SHA256="36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114";
const GATE_BLOB_SHA1="c73225ad322206dc6b308823d9f3a7a95a476d10";
const SCALE=1_000_000;

function requireTrue(ok,msg){if(!ok)throw Error(msg);}
function gitBlob(raw){return createHash("sha1").update("blob "+raw.length+"\0").update(raw).digest("hex");}
function sha256(raw){return createHash("sha256").update(raw).digest("hex");}
function brier(rows,fn){return rows.reduce((n,r)=>{const d=fn(r)-r.y;return n+d*d;},0)/rows.length;}
function rowsFrom(trace,donor,first,end,split){
 return trace.slice(first,end).map(r=>({id:r.id,split,
  key:"context"+r.views[0][0]+":action"+r.row.x1,
  raw:r.prediction.native/SCALE,donor:r.prediction[donor]/SCALE,y:r.row.s2}));
}
function evaluate(trace,donor){
 const fit=rowsFrom(trace,donor,0,16,"FIT");
 const oldValid=rowsFrom(trace,donor,16,32,"VALID_OLD");
 const novelValid=rowsFrom(trace,donor,32,48,"VALID_NOVEL");
 const heldNovel=rowsFrom(trace,donor,48,64,"HELD_NOVEL");
 const heldOld=rowsFrom(trace,donor,64,96,"HELD_OLD");
 const gate=gateDonor({fit,oldValid,novelValid});
 const score=rows=>({raw:brier(rows,r=>r.raw),donor:brier(rows,r=>r.donor),
   candidate:brier(rows,r=>predict(r,gate.capsules,gate.gamma))});
 return {donor,fit:fit.length,valid_old:oldValid.length,valid_novel:novelValid.length,
   held_novel:heldNovel.length,held_old:heldOld.length,
   decision:gate.status,gamma:gate.gamma,
   proposed_capsules:Object.keys(gate.proposedCapsules.cells).length,
   active_capsules:Object.keys(gate.capsules.cells).length,
   active_donor_keys:gate.capsules.donorKeys,
   validation_candidates:gate.candidates,
   brier:{held_novel:score(heldNovel),held_old:score(heldOld)}};
}
function run(traceBytes,gateBytes){
 requireTrue(gitBlob(traceBytes)===TRACE_BLOB_SHA1,"TRACE_GIT_BLOB_DRIFT");
 requireTrue(sha256(traceBytes)===TRACE_SHA256,"TRACE_SHA256_DRIFT");
 requireTrue(gitBlob(gateBytes)===GATE_BLOB_SHA1,"RS01_GATE_BLOB_DRIFT");
 const trace=JSON.parse(traceBytes.toString("utf8"));
 requireTrue(Array.isArray(trace)&&trace.length===96,"ROW_COUNT");
 const ids=new Set();
 for(let i=0;i<trace.length;i++){
  const r=trace[i];
  requireTrue(r.phase===Math.floor(i/32)&&r.origin===0,"SOURCE_PHASE_DRIFT");
  requireTrue(typeof r.id==="string"&&!ids.has(r.id),"WITNESS_ID_DRIFT");ids.add(r.id);
  requireTrue(r.prediction?.selector===r.prediction?.native,"NATIVE_SELECTOR_DRIFT");
  requireTrue([0,1].includes(r.row?.s2)&&[0,1].includes(r.row?.x1),"PUBLIC_OBSERVATION_DRIFT");
  requireTrue([0,1].includes(r.views?.[0]?.[0]),"CONTEXT_DRIFT");
  for(const key of ["native","direct","temporal"]){
   const p=r.prediction[key];
   requireTrue(Number.isSafeInteger(p)&&p>=0&&p<=SCALE,"FORECAST_DRIFT");
  }
 }
 return {schema:"dwsa-rs01.native-alignment-retro.v1",
  kind:"ALREADY_CONSUMED_RETROSPECTIVE_DIAGNOSTIC_NOT_NEW_SCIENCE",
  source_pr_head:SOURCE_PR1278_HEAD,source_trace_blob_sha1:TRACE_BLOB_SHA1,
  source_trace_sha256:TRACE_SHA256,gate_blob_sha1:GATE_BLOB_SHA1,source_actions:0,
  partitions:{fit:[0,16],valid_old:[16,32],valid_novel:[32,48],held_novel:[48,64],held_old:[64,96]},
  predictions_frozen:false,protected_first_use_authorized:false,scientific_gain_verified:false,
  outcomes:["direct","temporal"].map(name=>evaluate(trace,name))};
}
const [tracePath]=process.argv.slice(2);
if(!tracePath)throw Error("USAGE: node native_alignment_replay.mjs /path/to/existing/trace.json");
const output=run(readFileSync(tracePath),readFileSync(new URL("./identity_gate.mjs",import.meta.url)));
process.stdout.write(JSON.stringify(output,null,2)+"\n");
