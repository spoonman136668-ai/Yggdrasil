// RS02: source-free compositional pre-action feature transfer, isolated from native Yggdrasil.
// Public feature provenance and any future source-first-use require independent owner admission.
import {fitCapsules, RS01_SCHEMA} from "./identity_gate.mjs";
export const RS02_SCHEMA = "dwsa-rs02.public-feature-transfer.dev.v1";
const idPattern = /^[A-Za-z0-9_.:-]{1,80}$/;
const keyPattern = /^[A-Za-z0-9_.:-]{1,64}$/;
const schemaPattern = /^[A-Za-z0-9_.:-]{1,80}$/;
const allowedGammas = [1, 0.5, 0.25];
const clip = v => Math.max(0, Math.min(1, v));
const bound = v => Math.max(-0.1, Math.min(0.1, v));
function fail(msg) { throw Error(msg); }
function probability(x) { if (typeof x !== "number" || !Number.isFinite(x) || x < 0 || x > 1) fail("BAD_PROBABILITY"); }
function features(x, width) {
  if (!Array.isArray(x) || x.length < 2 || x.length > 8 || (width !== null && x.length !== width) || x.some(v => v !== 0 && v !== 1)) fail("BAD_PREACTION_FEATURES");
}
function partitions(rows, split, ids, width, featureSchemaId) {
  if (!Array.isArray(rows) || !rows.length) fail("EMPTY_PARTITION");
  for (const r of rows) {
    if (!r || r.split !== split) fail("SPLIT_VIOLATION");
    if (typeof r.id !== "string" || !idPattern.test(r.id)) fail("BAD_ROW_ID");
    if (ids.has(r.id)) fail("DUPLICATE_ROW_ID");
    ids.add(r.id);
    if (typeof r.key !== "string" || !keyPattern.test(r.key)) fail("BAD_CONTEXT_KEY");
    if (r.featureSchemaId !== featureSchemaId) fail("FEATURE_SCHEMA_MISMATCH");
    if (r.y !== 0 && r.y !== 1) fail("BAD_LABEL");
    probability(r.raw); probability(r.donor); features(r.features, width);
  }
}
function observed(r) { return {key:r.key,raw:r.raw,donor:r.donor,features:r.features,featureSchemaId:r.featureSchemaId}; }
function brier(rows, fn) { return rows.reduce((s,r) => { const d=fn(observed(r))-r.y; return s+d*d; },0)/rows.length; }
function oldGroupDrift(rows, prediction) {
  const groups = new Map();
  function add(k,r) { let v=groups.get(k); if(!v){v=[];groups.set(k,v);}v.push(r); }
  for (const r of rows) {
    add("key:"+r.key,r);
    for (let i=0;i<r.features.length;i++) add("feature:"+i+":"+r.features[i],r);
  }
  return Math.max(...Array.from(groups.values(),group=>brier(group,prediction)-brier(group,r=>r.raw)));
}
function supported(values, xs) { return xs.every((v,i)=>values[i].includes(v)); }
export function predictTransfer(row, gate) {
  if(!gate || gate.schema!==RS02_SCHEMA || typeof gate.featureSchemaId!=="string" || !schemaPattern.test(gate.featureSchemaId)) fail("BAD_GATE");
  if(!row || typeof row.key!=="string" || !keyPattern.test(row.key)) fail("BAD_CONTEXT_KEY");
  if(Object.prototype.hasOwnProperty.call(row,"y")) fail("PREDICTION_LABEL_PRESENT");
  if(row.featureSchemaId!==gate.featureSchemaId) fail("FEATURE_SCHEMA_MISMATCH");
  probability(row.raw); probability(row.donor);
  features(row.features,gate.featureWidth);
  if(!Array.isArray(gate.supportedValues)||gate.supportedValues.length!==gate.featureWidth||gate.supportedValues.some(x=>!Array.isArray(x)||!x.length||x.some(v=>v!==0&&v!==1)||new Set(x).size!==x.length)) fail("BAD_FEATURE_SCOPE");
  if(![0,...allowedGammas].includes(gate.gamma)) fail("BAD_GAMMA");
  if(!gate.capsules || gate.capsules.schema!==RS01_SCHEMA || !gate.capsules.cells || typeof gate.capsules.cells!=="object" || Object.keys(gate.capsules.cells).length>16) fail("BAD_CAPSULE");
  for (const [k,v] of Object.entries(gate.capsules.cells)) {
    if(!keyPattern.test(k) || typeof v!=="number" || !Number.isFinite(v) || Math.abs(v)>0.1) fail("BAD_CAPSULE_SHIFT");
  }
  const correction=Object.prototype.hasOwnProperty.call(gate.capsules.cells,row.key)?gate.capsules.cells[row.key]:0;
  const transfer=supported(gate.supportedValues,row.features)?gate.gamma*bound(row.donor-row.raw):0;
  return clip(row.raw+correction+transfer);
}
export function gateTransfer({fit,oldValid,novelValid,featureSchemaId}) {
  if(typeof featureSchemaId!=="string"||!schemaPattern.test(featureSchemaId)) fail("BAD_FEATURE_SCHEMA_ID");
  const ids=new Set();
  if(!Array.isArray(fit)||!fit.length||!Array.isArray(fit[0]?.features)) fail("EMPTY_PARTITION");
  const width=fit[0].features.length;
  partitions(fit,"FIT",ids,width,featureSchemaId);partitions(oldValid,"VALID_OLD",ids,width,featureSchemaId);partitions(novelValid,"VALID_NOVEL",ids,width,featureSchemaId);
  const seenKeys=new Set([...fit,...oldValid].map(r=>r.key));
  if(novelValid.some(r=>seenKeys.has(r.key))) fail("NOVEL_KEY_OVERLAP");
  // Admission may inspect only FIT and validation features, never held identifiers or labels.
  const supportedValues=Array.from({length:width},(_,i)=>Array.from(new Set([...oldValid,...novelValid].map(r=>r.features[i]))).sort());
  const proposed=fitCapsules(fit);
  const create=gamma=>({schema:RS02_SCHEMA,featureSchemaId,featureWidth:width,supportedValues,gamma,capsules:proposed});
  const oldRaw=brier(oldValid,r=>r.raw),novelRaw=brier(novelValid,r=>r.raw);
  const novelRepair=brier(novelValid,r=>predictTransfer(r,create(0)));
  const candidates=allowedGammas.map(gamma=>{
    const predictor=r=>predictTransfer(r,create(gamma));
    const oldBrier=brier(oldValid,predictor),novelBrier=brier(novelValid,predictor);
    const oldDrift=oldBrier-oldRaw,rawGain=novelRaw-novelBrier,donorIncrement=novelRepair-novelBrier;
    const maxOldGroupDrift=oldGroupDrift(oldValid,predictor);
    return {gamma,oldBrier,novelBrier,oldDrift,maxOldGroupDrift,rawGain,donorIncrement,
      accepted:oldDrift<=0.02+1e-12 && maxOldGroupDrift<=0.02+1e-12 && rawGain>=0.005-1e-12 && donorIncrement>=0.002-1e-12};
  });
  const good=candidates.filter(c=>c.accepted).sort((a,b)=>a.novelBrier-b.novelBrier||a.gamma-b.gamma);
  const gamma=good.length?good[0].gamma:0;
  const capsules=good.length?proposed:{...proposed,cells:Object.create(null)};
  return {schema:RS02_SCHEMA,status:good.length?"DEV_VALIDATION_ADMITTED":"DEV_VALIDATION_REJECTED",featureSchemaId,featureWidth:width,supportedValues,gamma,capsules,candidates,
    scientificGainVerified:false,protectedSourceActions:0,trainedDonorVerified:false};
}
