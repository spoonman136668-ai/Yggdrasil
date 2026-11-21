// RS03: conservative pairwise-coverage veto on RS02's public pre-action features.
// Development-only. Does NOT establish causal-law transfer or donor correctness.
import {gateTransfer, predictTransfer, RS02_SCHEMA} from './feature_transfer_gate.mjs';
export const RS03_SCHEMA = 'dwsa-rs03.pairwise-coverage.dev.v1';
const LIMIT = 0.02;
function fail(code) { throw Error(code); }
function tokens(xs) {
  const out=[];
  for(let i=0;i<xs.length;i++) for(let j=i+1;j<xs.length;j++) out.push(i+':'+j+':'+xs[i]+':'+xs[j]);
  return out;
}
function brier(rows, predictor) {
  return rows.reduce((s,r)=>{const d=predictor(r)-r.y;return s+d*d;},0)/rows.length;
}
function observed(r) {return {key:r.key,features:r.features,raw:r.raw,donor:r.donor,featureSchemaId:r.featureSchemaId};}
function maxPairDrift(rows,predictor) {
  const groups=new Map();
  for(const r of rows) for(const t of tokens(r.features)) {
    if(!groups.has(t)) groups.set(t,[]);
    groups.get(t).push(r);
  }
  return Math.max(...Array.from(groups.values(),g=>brier(g,r=>predictor(observed(r)))-brier(g,r=>r.raw)));
}
function validateScope(gate) {
  if(!gate || gate.schema!==RS03_SCHEMA || !Number.isInteger(gate.featureWidth) || gate.featureWidth<2 || gate.featureWidth>8 || !Array.isArray(gate.pairScope)) fail('BAD_RS03_GATE');
  const seen=new Set();
  for(const t of gate.pairScope) {
    const match=typeof t==='string'&&/^(\d):(\d):([01]):([01])$/.exec(t);
    if(!match || +match[1]>=+match[2] || +match[2]>=gate.featureWidth || seen.has(t)) fail('BAD_PAIR_SCOPE');
    seen.add(t);
  }
  if(gate.pairScope.length>4*gate.featureWidth*(gate.featureWidth-1)/2) fail('BAD_PAIR_SCOPE');
  return seen;
}
export function predictPairwise(row,gate) {
  const scope=validateScope(gate);
  // RS02 validates input and capsule before any supported/unsupported fallback.
  const base={...gate,schema:RS02_SCHEMA,gamma:0};
  const rawPlusCorrection=predictTransfer(row,base);
  if(!tokens(row.features).every(t=>scope.has(t))) return rawPlusCorrection;
  return predictTransfer(row,{...base,gamma:gate.gamma});
}
export function gatePairwise(args) {
  const base=gateTransfer(args); // seals split, unique witness IDs, labels and schema
  const pairScope=Array.from(new Set([...args.oldValid,...args.novelValid].flatMap(r=>tokens(r.features)))).sort();
  const scoped=gamma=>({...base,schema:RS02_SCHEMA,gamma});
  const candidates=base.candidates.map(c=>{
    const maxOldPairDrift=maxPairDrift(args.oldValid,row=>predictTransfer(row,scoped(c.gamma)));
    return {...c,maxOldPairDrift,acceptedPairwise:c.accepted&&maxOldPairDrift<=LIMIT+1e-12};
  });
  const best=candidates.filter(c=>c.acceptedPairwise).sort((a,b)=>a.novelBrier-b.novelBrier||a.gamma-b.gamma)[0];
  const capsules=best?base.capsules:{...base.capsules,cells:Object.create(null)};
  return {...base,schema:RS03_SCHEMA,status:best?'DEV_PAIRWISE_ADMITTED':'DEV_PAIRWISE_REJECTED',gamma:best?.gamma??0,capsules,pairScope,candidates,
    scientificGainVerified:false,trainedDonorVerified:false,protectedSourceActions:0};
}

