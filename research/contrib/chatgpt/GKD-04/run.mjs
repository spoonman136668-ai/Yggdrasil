// GKD-04: one generic typed causal AST -> numeric, source-hashed bytecode.
// Preregistered FIRST: 71a85055096d7d4fa4c92e0ae2afb3522b519848
// GPT donor JSON frozen: d20e77fcec0b64fa9f1e093d127881bdb8eb08e5
// Structured model response was authored using inference. No model inference at recipient execution.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const sha=b=>createHash('sha256').update(b).digest();
const guard=(ok,why)=>{if(!ok)throw Error('GKD04_FAIL_CLOSED:'+why);};
const same=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
const validDims=d=>Array.isArray(d)&&d.length===5&&d.every(x=>Number.isInteger(x)&&x>=-16&&x<=16);
const zero=[0,0,0,0,0],ops={add:1,sub:2,mul:3,div:4};
const maxInputs=8,maxOps=32;
const legalNode=n=>n&&typeof n==='object'&&!Array.isArray(n);

function validateClaim(c){
  guard(c&&typeof c.id==='string'&&Array.isArray(c.inputs)&&c.inputs.length>0&&c.inputs.length<=maxInputs,'CLAIM');
  guard(validDims(c.output_dimensions),'OUTPUT_DIMS');
  const names=new Set();
  for(const input of c.inputs){
    guard(input&&typeof input.name==='string'&&/^[a-zA-Z][a-zA-Z0-9_]{0,30}$/.test(input.name)&&!names.has(input.name),'INPUT_NAME');
    guard(validDims(input.dimensions),'INPUT_DIMS');
    guard(Number.isFinite(input.min)&&Number.isFinite(input.max)&&input.min<input.max,'BOUNDS');
    names.add(input.name);
  }
}
export function compile(claim){
  validateClaim(claim);
  const map=new Map(claim.inputs.map((x,i)=>[x.name,i])),instructions=[];
  let nodes=0;
  function walk(n,depth){
    guard(depth<=12&&++nodes<=96,'DEPTH_OR_NODES');
    guard(legalNode(n),'NODE');
    const keys=Object.keys(n).sort().join(',');
    if(keys==='input'){
      guard(typeof n.input==='string'&&map.has(n.input),'UNKNOWN_INPUT');
      const idx=map.get(n.input);return {r:idx,u:claim.inputs[idx].dimensions};
    }
    if(keys==='const'){
      guard(typeof n.const==='number'&&Number.isFinite(n.const),'CONST');
      guard(instructions.length<maxOps,'OP_BUDGET');
      const dst=claim.inputs.length+instructions.length;
      instructions.push({op:5,dst,a:255,b:255,value:n.const});
      return {r:dst,u:zero};
    }
    guard(keys==='args,op'&&typeof n.op==='string'&&Object.hasOwn(ops,n.op)&&Array.isArray(n.args)&&n.args.length===2,'OP');
    const a=walk(n.args[0],depth+1),b=walk(n.args[1],depth+1);
    let u;
    if(n.op==='add'||n.op==='sub'){guard(same(a.u,b.u),'ADD_UNIT_MISMATCH');u=a.u;}
    else if(n.op==='mul')u=a.u.map((x,i)=>x+b.u[i]);
    else u=a.u.map((x,i)=>x-b.u[i]);
    guard(validDims(u),'UNIT_OVERFLOW');
    guard(instructions.length<maxOps,'OP_BUDGET');
    const dst=claim.inputs.length+instructions.length;
    instructions.push({op:ops[n.op],dst,a:a.r,b:b.r,value:0});
    return {r:dst,u};
  }
  const result=walk(claim.formula,0);
  guard(instructions.length>0&&result.r===claim.inputs.length+instructions.length-1,'NO_COMPILED_ROOT');
  guard(same(result.u,claim.output_dimensions),'OUTPUT_UNIT_MISMATCH');
  const len=16+32+16*claim.inputs.length+12*instructions.length;
  const b=Buffer.alloc(len);
  b.write('GD04',0,'ascii');b[4]=1;b[5]=claim.inputs.length;b[6]=instructions.length;b[7]=result.r;
  for(let i=0;i<5;i++)b.writeInt8(result.u[i],8+i);
  sha(Buffer.from(JSON.stringify(claim))).copy(b,16);
  for(let i=0;i<claim.inputs.length;i++){b.writeDoubleLE(claim.inputs[i].min,48+16*i);b.writeDoubleLE(claim.inputs[i].max,56+16*i);}
  let start=48+16*claim.inputs.length;
  for(const [i,op] of instructions.entries()){
    const k=start+12*i;
    b[k]=op.op;b[k+1]=op.dst;b[k+2]=op.a;b[k+3]=op.b;
    if(op.op===5)b.writeDoubleLE(op.value,k+4);
  }
  return Buffer.concat([b,sha(b)]);
}
export function decode(bytes){
  guard(Buffer.isBuffer(bytes)&&bytes.length>=96,'SIZE');
  const b=bytes.subarray(0,-32);
  guard(bytes.subarray(-32).equals(sha(b)),'CHECKSUM');
  guard(b.toString('ascii',0,4)==='GD04'&&b[4]===1&&b[13]===0&&b[14]===0&&b[15]===0,'HEADER');
  const ni=b[5],nop=b[6],out=b[7];
  guard(ni>0&&ni<=maxInputs&&nop>0&&nop<=maxOps&&out===ni+nop-1,'COUNTS');
  guard(validDims(Array.from({length:5},(_,i)=>b.readInt8(8+i))),'OUTPUT_UNIT');
  guard(b.length===48+16*ni+12*nop,'EXACT_SIZE');
  const limits=[];
  for(let i=0;i<ni;i++){
    const min=b.readDoubleLE(48+16*i),max=b.readDoubleLE(56+16*i);
    guard(Number.isFinite(min)&&Number.isFinite(max)&&min<max,'DECODE_BOUNDS');
    limits.push([min,max]);
  }
  const code=[];
  const base=48+16*ni;
  for(let i=0;i<nop;i++){
    const k=base+12*i,op=b[k],dst=b[k+1],a=b[k+2],z=b[k+3],value=b.readDoubleLE(k+4);
    guard(dst===ni+i,'NONCANONICAL_TARGET');
    if(op===5)guard(a===255&&z===255&&Number.isFinite(value),'BAD_LITERAL');
    else guard(op>=1&&op<=4&&a<dst&&z<dst&&value===0,'BAD_INSTRUCTION');
    code.push({op,dst,a,b:z,value});
  }
  return {inputCount:ni,limits,code,outputRegister:out,unit:Array.from({length:5},(_,i)=>b.readInt8(8+i)),
    sourceDigest:b.subarray(16,48).toString('hex'),checkpointDigest:sha(bytes).toString('hex')};
}
export function execute(program,inputs){
  guard(Array.isArray(inputs)&&inputs.length===program.inputCount&&inputs.every(Number.isFinite),'RUNTIME_INPUTS');
  for(let i=0;i<inputs.length;i++)guard(inputs[i]>=program.limits[i][0]&&inputs[i]<=program.limits[i][1],'INPUT_OUTSIDE_DOMAIN');
  const regs=inputs.slice();
  for(const q of program.code){
    let v;
    if(q.op===5)v=q.value;
    else if(q.op===1)v=regs[q.a]+regs[q.b];
    else if(q.op===2)v=regs[q.a]-regs[q.b];
    else if(q.op===3)v=regs[q.a]*regs[q.b];
    else{
      guard(regs[q.b]!==0,'ZERO_DENOM');
      v=regs[q.a]/regs[q.b];
    }
    guard(Number.isFinite(v),'RESULT_NONFINITE');
    regs[q.dst]=v;
  }
  return regs[program.outputRegister];
}
function xorshift(seed){let s=seed>>>0;return()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)/4294967296;};}
function independentlyExpected(id,v){
  // Independent *same-information* textbook symbolic control, intentionally NOT evaluating donor AST.
  if(id==='ohmic_heat'){const [V,R,t,m,c]=v;return V*V*t/(R*m*c);}
  if(id==='hydrostatic'){const [rho,g,h]=v;return rho*g*h;}
  if(id==='hooke'){const [k,x]=v;return k*x;}
  if(id==='kinetic'){const [m,speed]=v;return 0.5*m*speed*speed;}
  throw Error('UNKNOWN_INDEPENDENT_REFERENCE');
}
const rel=(a,b)=>Math.abs(a-b)/Math.max(1,Math.abs(b));
function mustReject(fn,why){let failed=false;try{fn();}catch(e){failed=String(e.message).startsWith('GKD04_FAIL_CLOSED:');}guard(failed,'MISSING_NEGATIVE_'+why);}
function copy(x){return JSON.parse(JSON.stringify(x));}
export function run(){
  const donor=JSON.parse(readFileSync(new URL('./donor.json',import.meta.url),'utf8'));
  guard(donor.schema==='yggdrasil.gkd04.structured-assistant-donor.v1'&&donor.claims.length===4,'DONOR_SCHEMA');
  guard(same(donor.claims.map(x=>x.id),['ohmic_heat','hydrostatic','hooke','kinetic']),'DONOR_ROSTER');
  const seeds=[1441,2442,3443,4444],scores=[],claims=[];
  let cases=0,parity=0,cold=0,maxErr=0,totalBytes=0;
  for(const [ci,claim] of donor.claims.entries()){
    const b=compile(claim),decoded=decode(b),rand=xorshift(seeds[ci]);
    guard(decoded.sourceDigest===sha(Buffer.from(JSON.stringify(claim))).toString('hex'),'SOURCE_HASH');
    let correct=0;
    for(let j=0;j<256;j++){
      const x=claim.inputs.map(z=>z.min+(z.max-z.min)*rand());
      const got=execute(decoded,x),truth=independentlyExpected(claim.id,x),err=rel(got,truth);
      maxErr=Math.max(maxErr,err);
      guard(err<=1e-12,'SYMBOLIC_PARITY');
      cases++;parity++;correct++;
    }
    for(let k=0;k<3;k++){const restored=decode(Buffer.from(b));guard(restored.sourceDigest===decoded.sourceDigest&&restored.checkpointDigest===decoded.checkpointDigest,'COLD_RESTORE');cold++;}
    scores.push({id:claim.id,correct,total:256,checkpoint_bytes:b.length,source_sha256:decoded.sourceDigest,checkpoint_sha256:sha(b).toString('hex')});
    totalBytes+=b.length;claims.push({claim,b,decoded});
  }
  // An authentic-looking, dimensionally valid *wrong physics statement* passes type checking.
  const wrong=copy(donor.claims[2]),falseClaim={op:'mul',args:[{const:2},wrong.formula]};
  wrong.formula=falseClaim;
  const wrongCode=decode(compile(wrong)),wrongRand=xorshift(seeds[2]);
  let semanticallyWrong=0;
  for(let j=0;j<256;j++){
    const x=wrong.inputs.map(z=>z.min+(z.max-z.min)*wrongRand());
    if(rel(execute(wrongCode,x),independentlyExpected('hooke',x))>1e-12)semanticallyWrong++;
  }
  guard(semanticallyWrong===256,'SEMANTIC_FALSE_NEGATIVE');
  let guards=0;
  const neg=(fn,label)=>{mustReject(fn,label);guards++;};
  const baseClaim=donor.claims[2],badDim=copy(baseClaim);
  badDim.output_dimensions=[0,0,0,0,0];neg(()=>compile(badDim),'OUTPUT_UNIT');
  const addWrong=copy(baseClaim);addWrong.formula={op:'add',args:[{input:'k'},{input:'x'}]};neg(()=>compile(addWrong),'ADD_DIMENSION');
  const missing=copy(baseClaim);missing.formula={op:'mul',args:[{input:'unknown'},{input:'x'}]};neg(()=>compile(missing),'UNKNOWN_INPUT');
  const unknown=copy(baseClaim);unknown.formula={op:'pow',args:[{input:'k'},{input:'x'}]};neg(()=>compile(unknown),'UNKNOWN_OP');
  const invalidLiteral=copy(baseClaim);invalidLiteral.formula={op:'mul',args:[{const:Infinity},baseClaim.formula]};neg(()=>compile(invalidLiteral),'INFINITE_LITERAL');
  const invalidBounds=copy(baseClaim);invalidBounds.inputs[0].min=999;neg(()=>compile(invalidBounds),'BAD_BOUNDS');
  const repeated=copy(baseClaim);repeated.inputs[1].name='k';neg(()=>compile(repeated),'DUPLICATE_INPUT');
  const depth=copy(baseClaim);let deep=depth.formula;for(let k=0;k<14;k++)deep={op:'mul',args:[{const:1},deep]};depth.formula=deep;neg(()=>compile(depth),'DEPTH');
  const valid=claims[2],corrupt=Buffer.from(valid.b);corrupt[21]^=1;neg(()=>decode(corrupt),'CHECKSUM_TAMPER');
  const truncated=valid.b.subarray(0,-1);neg(()=>decode(truncated),'TRUNCATED');
  const signed=Buffer.from(valid.b);signed[0]=88;sha(signed.subarray(0,-32)).copy(signed,signed.length-32);neg(()=>decode(signed),'RESIGNED_HEADER');
  const badOp=Buffer.from(valid.b),offset=48+16*valid.claim.inputs.length;badOp[offset]=255;sha(badOp.subarray(0,-32)).copy(badOp,badOp.length-32);neg(()=>decode(badOp),'RESIGNED_OPCODE');
  neg(()=>execute(valid.decoded,[100,1]),'OUTSIDE_DOMAIN');
  neg(()=>execute(valid.decoded,[NaN,1]),'NONFINITE_RUNTIME');
  const zeroDen=copy(donor.claims[2]);
  zeroDen.formula={op:'div',args:[{input:'k'},{input:'x'}]};
  zeroDen.output_dimensions=[1,-1,-2,0,0];
  const zp=decode(compile(zeroDen));
  neg(()=>execute(zp,[1,0]),'ZERO_DENOMINATOR');
  guard(cases===1024&&parity===1024&&cold===12&&guards>=10,'FROZEN_CASES');
  const result={
    schema:'yggdrasil.gkd04.generic-ast-donor-dev.v1',experiment_id:'GKD-04',
    preregistration_commit:'71a85055096d7d4fa4c92e0ae2afb3522b519848',
    donor_commit:'d20e77fcec0b64fa9f1e093d127881bdb8eb08e5',
    classification:'ENGINEERING_DEV_PASS_SCIENTIFIC_UNVERIFIED',
    source_type:'GPT-authored structured JSON AST, not full natural-language parsing or GPT weight transfer',
    claims:scores,synthetic_dev_cases:cases,correct_against_exact_symbolic:parity,
    max_relative_error:maxErr,total_checkpoint_bytes:totalBytes,cold_restores:cold,
    dimensionally_valid_false_claim_compiled:true,false_claim_externally_rejected:semanticallyWrong,
    malformed_negative_guards_pass:guards,teacher_calls_at_recipient_runtime:0,
    native_accepted:false,scientific_gain_verified:false,
    limitations:'No real intervention source; donor units and AST authored, not discovered; symbolic controls tie all; typed compilation cannot verify causal truth or source issuer.'
  };
  console.log(JSON.stringify(result,null,2));return result;
}
if(process.argv[1]?.endsWith('/GKD-04/run.mjs')||process.argv[1]?.endsWith('\\GKD-04\\run.mjs'))run();
