// GKD-01 — assistant-response factual donor => generic numerical program.
// Preregistered at bd0349022a1e29fe639c231f00ec425d9ffe31de BEFORE implementation/scoring.
// No pretrained-weight access, no automatic natural-language compiler, no teacher inference after source freeze.
import { createHash } from 'node:crypto';
import { performance } from 'node:perf_hooks';

const RULES = [
  [1,7,1,2,255], [2,8,1,2,255], [3,9,8,7,255],
  [4,10,7,9,6], [3,11,0,10,255], [2,12,0,11,255],
  [2,13,12,3,255], [2,14,4,5,255], [3,15,13,14,255]
];
// ADD=1, MUL=2, DIV=3, SELECT=4; registers 0..6 contain V,R1,R2,t,m,c,mode.
// Intermediate registers encode series/parallel resistance, current, power,
// energy and adiabatic temperature rise. Arithmetic opcodes are domain-neutral.
const sha = x => createHash('sha256').update(x).digest();
const requireGood = (x, label) => { if (!x) throw Error('GKD01_FAIL_CLOSED:' + label); };
export function compile() {
  const body = Buffer.alloc(53);
  body.write('GKD1', 0, 'ascii');
  body[4]=1; body[5]=9; body[6]=16;
  for (let i=0;i<9;i++) for(let j=0;j<5;j++) body[8+5*i+j]=RULES[i][j];
  return Buffer.concat([body,sha(body)]);
}
export function decode(bytes) {
  requireGood(Buffer.isBuffer(bytes) && bytes.length===85,'SIZE');
  const body=bytes.subarray(0,53);
  requireGood(bytes.subarray(53).equals(sha(body)),'DIGEST');
  requireGood(body.toString('ascii',0,4)==='GKD1' && body[4]===1 &&
    body[5]===9 && body[6]===16 && body[7]===0,'HEADER');
  const available=new Set([0,1,2,3,4,5,6]),program=[];
  for(let i=0;i<9;i++) {
    const r=[...body.subarray(8+5*i,13+5*i)];
    const [op,dest,a,b,aux]=r;
    requireGood(op>=1 && op<=4,'OPCODE');
    requireGood(dest>=7 && dest<=15 && !available.has(dest),'DEST');
    requireGood(available.has(a) && available.has(b),'SOURCE');
    requireGood(op===4?aux===6:aux===255,'AUX');
    available.add(dest);program.push(r);
  }
  requireGood([10,11,12,13,15].every(x=>available.has(x)),'OUTPUT');
  return program;
}
function validate(x) {
  requireGood(Array.isArray(x)&&x.length===7&&x.every(Number.isFinite),'INPUT');
  const [v,r1,r2,t,m,c,topology]=x;
  requireGood(v>=0&&r1>0&&r2>0&&t>=0&&m>0&&c>0,'DOMAIN');
  requireGood(topology===0||topology===1,'UNKNOWN_WORLD');
}
export function execute(program,x) {
  validate(x);
  const r=[...x,...Array(9).fill(NaN)];
  for(const [op,dest,a,b,aux] of program) {
    let z;
    if(op===1)z=r[a]+r[b];
    else if(op===2)z=r[a]*r[b];
    else if(op===3){requireGood(r[b]!==0,'ZERO_DENOMINATOR');z=r[a]/r[b];}
    else if(op===4)z=r[aux]===1?r[b]:r[a];
    else throw Error('GKD01_FAIL_CLOSED:RUNTIME_OPCODE');
    requireGood(Number.isFinite(z),'RESULT');
    r[dest]=z;
  }
  return [r[10],r[11],r[12],r[13],r[15]];
}
function symbolic(x) { // Independent exact same-information symbolic control.
  validate(x);
  const [v,r1,r2,t,m,c,topology]=x;
  const resistance=topology===0?r1+r2:r1*r2/(r1+r2);
  const current=v/resistance,power=v*current,energy=power*t;
  return [resistance,current,power,energy,energy/(m*c)];
}
function rng(seed) {
  let s=seed>>>0;
  return()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)/4294967296;};
}
function expectFailure(fn,label){
  let okay=false;
  try {fn();} catch(e){okay=String(e.message).startsWith('GKD01_FAIL_CLOSED:');}
  requireGood(okay,'MISSED_NEGATIVE_'+label);
}
function reSign(x){const b=Buffer.from(x);sha(b.subarray(0,53)).copy(b,53);return b;}
const relative=(a,b)=>Math.abs(a-b)/Math.max(1,Math.abs(b));
export function run(){
  const start=performance.now(),bytes=compile(),program=decode(bytes);
  requireGood(bytes.length===85&&compile().equals(bytes),'COMPILE');
  const bad=Buffer.from(bytes);bad[8+8*5]=1; // Sham: change final DIV to ADD.
  const sham=decode(reSign(bad));
  let cases=0,ties=0,shamWrong=0,maxError=0,first;
  for(const seed of [71,131,211]) {
    const rand=rng(seed);
    for(const topology of [0,1]) for(let i=0;i<128;i++) {
      const x=[2+22*rand(),1+19*rand(),1+19*rand(),
        1+9*rand(),0.2+4.8*rand(),100+900*rand(),topology];
      if(!first)first=x;
      const got=execute(program,x),truth=symbolic(x),wrong=execute(sham,x);
      const e=Math.max(...got.map((a,j)=>relative(a,truth[j])));
      maxError=Math.max(maxError,e);if(e<=1e-12)ties++;
      if(relative(wrong[4],truth[4])>1e-12)shamWrong++;
      cases++;
    }
  }
  let cold=0;
  for(let i=0;i<3;i++){
    const restored=decode(Buffer.from(bytes));
    requireGood(JSON.stringify(restored)===JSON.stringify(program),'RESTORE');
    requireGood(JSON.stringify(execute(restored,first))===JSON.stringify(execute(program,first)),'REPLAY');
    cold++;
  }
  const tampered=Buffer.from(bytes);tampered[14]^=1;
  expectFailure(()=>decode(tampered),'DIGEST');
  const invalidOp=Buffer.from(bytes);invalidOp[8]=255;
  expectFailure(()=>decode(reSign(invalidOp)),'OPCODE');
  const invalidHeader=Buffer.from(bytes);invalidHeader[7]=9;
  expectFailure(()=>decode(reSign(invalidHeader)),'HEADER');
  expectFailure(()=>execute(program,[...first.slice(0,6),2]),'UNKNOWN_WORLD');
  expectFailure(()=>execute(program,[first[0],0,...first.slice(2)]),'RESISTANCE');
  expectFailure(()=>execute(program,[...first.slice(0,4),0,...first.slice(5)]),'MASS');
  expectFailure(()=>execute(program,[NaN,...first.slice(1)]),'NONFINITE');
  requireGood(cases===768&&ties===cases&&maxError<=1e-12,'SYMBOLIC_PARITY');
  requireGood(shamWrong/cases>=0.99,'SHAM');
  const result={
    schema:'yggdrasil.chatgpt-response-donor-dev.v1',
    experiment_id:'GKD-01',classification:'ENGINEERING_DEV_PASS_SCIENTIFIC_UNVERIFIED',
    provenance:'assistant-authored ideal-circuit claims manually compiled to generic opcodes',
    cases,seeds:[71,131,211],checkpoint_bytes:bytes.length,
    checkpoint_sha256:sha(bytes).toString('hex'),
    teacher_inference_during_recipient_run:0,symbolic_control_ties:ties,
    max_relative_error:maxError,sham_temperature_errors:shamWrong,
    cold_restores:cold,guard_negative_cases_pass:7,
    runtime_ms:+(performance.now()-start).toFixed(3),
    scientific_gain_verified:false,native_accepted:false,
    limitations:'same law-family equations; no unseen SCM, trained control superiority, automatic donor extraction or native cumulative learning'
  };
  console.log(JSON.stringify(result,null,2));return result;
}
if(process.argv[1]?.endsWith('/run.mjs')||process.argv[1]?.endsWith('\\run.mjs'))run();
