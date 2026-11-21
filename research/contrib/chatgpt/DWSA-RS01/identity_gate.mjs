// DWSA-RS01: source-free identity-preserving donor admission gate.
// Isolated arithmetic utility, NOT native Yggdrasil, a donor runtime, or a scientific result.
export const RS01_SCHEMA="dwsa-rs01.identity-capsules.v1";
function fail(msg){throw Error(msg);}
function p01(v){if(typeof v!=="number"||!Number.isFinite(v)||v<0||v>1)fail("BAD_PROBABILITY");return v;}
function rowCheck(r,split){
 if(!r||r.split!==split)fail("SPLIT_VIOLATION");
 if(typeof r.id!=="string"||!/^[A-Za-z0-9_.:-]{1,80}$/.test(r.id))fail("BAD_ROW_ID");
 if(typeof r.key!=="string"||!/^[A-Za-z0-9_.:-]{1,64}$/.test(r.key))fail("BAD_CONTEXT_KEY");
 if(r.y!==0&&r.y!==1)fail("BAD_LABEL");
 p01(r.raw);p01(r.donor);
}
function partition(rows,split,ids){
 if(!Array.isArray(rows)||!rows.length)fail("EMPTY_PARTITION");
 for(const r of rows){rowCheck(r,split);if(ids.has(r.id))fail("DUPLICATE_ROW_ID");ids.add(r.id);}
}
const clip=v=>Math.max(0,Math.min(1,v)),bound=v=>Math.max(-0.1,Math.min(0.1,v));
export function fitCapsules(fit){
 partition(fit,"FIT",new Set());
 const groups=new Map();
 for(const r of fit){const g=groups.get(r.key)||{key:r.key,n:0,residual:0};g.n++;g.residual+=r.y-r.raw;groups.set(r.key,g);}
 const ranked=Array.from(groups.values()).sort((a,b)=>b.n-a.n||(a.key<b.key?-1:a.key>b.key?1:0)).slice(0,16);
 const cells=Object.create(null);
 for(const g of ranked)cells[g.key]=bound(g.residual/(g.n+20));
 return {schema:RS01_SCHEMA,shrink:20,maxCells:16,maxAbsShift:0.1,cells};
}
export function predict(row,capsules,gamma=0){
 if(!row||typeof row.key!=="string"||!/^[A-Za-z0-9_.:-]{1,64}$/.test(row.key))fail("BAD_CONTEXT_KEY");
 if(!capsules||capsules.schema!==RS01_SCHEMA||!capsules.cells||typeof capsules.cells!=="object")fail("BAD_CAPSULE");
 p01(row.raw);p01(row.donor);
 if(![0,0.25,0.5,1].includes(gamma))fail("BAD_GAMMA");
 const v=Object.prototype.hasOwnProperty.call(capsules.cells,row.key)?capsules.cells[row.key]:0;
 if(typeof v!=="number"||!Number.isFinite(v)||Math.abs(v)>0.1)fail("BAD_CAPSULE_SHIFT");
 return clip(row.raw+v+gamma*(row.donor-row.raw));
}
function brier(rows,fn){return rows.reduce((s,r)=>{const e=fn(r)-r.y;return s+e*e;},0)/rows.length;}
export function gateDonor({fit,oldValid,novelValid}){
 const ids=new Set();
 partition(fit,"FIT",ids);partition(oldValid,"VALID_OLD",ids);partition(novelValid,"VALID_NOVEL",ids);
 const capsules=fitCapsules(fit),oldRawBrier=brier(oldValid,r=>r.raw),novelRawBrier=brier(novelValid,r=>r.raw);
 const novelRepairBrier=brier(novelValid,r=>predict(r,capsules,0));
 const candidates=[1,0.5,0.25].map(gamma=>{
  const oldBrier=brier(oldValid,r=>predict(r,capsules,gamma));
  const novelBrier=brier(novelValid,r=>predict(r,capsules,gamma));
  const oldDrift=oldBrier-oldRawBrier,rawGain=novelRawBrier-novelBrier,donorIncrement=novelRepairBrier-novelBrier;
  return {gamma,oldBrier,novelBrier,oldDrift,rawGain,donorIncrement,
   accepted:oldDrift<=0.02+1e-12&&rawGain>=0.005-1e-12&&donorIncrement>=0.002-1e-12};
 });
 const good=candidates.filter(c=>c.accepted).sort((a,b)=>a.novelBrier-b.novelBrier||a.gamma-b.gamma);
 return {schema:RS01_SCHEMA,status:good.length?"VALIDATION_ADMITTED":"VALIDATION_REJECTED",
  gamma:good.length?good[0].gamma:0,capsules,oldRawBrier,novelRawBrier,novelRepairBrier,candidates,
  scientificGainVerified:false,protectedSourceActions:0};
}
