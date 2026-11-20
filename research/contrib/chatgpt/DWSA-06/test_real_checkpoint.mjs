// Standalone engineering witness: pinned original donor-derived 52-byte body
// transferred from independently SHA-verified GitHub weight-only core function.
// Ten evaluation templates: Copyright (c) 2026 MasanneckLab, MIT License.
// Source license: https://github.com/MasanneckLab/neural-networks-explained/blob/149a2838309efe6ee5ec9e8c9689e4a321158b7d/LICENSE
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {decodePrototypes, encodePrototypes, classifyPrototypes} from './codec.mjs';

const BODY = '4457503601000a2354765cc4b573a0676eef2888eeec21784343b9d0f787d453e12f91087a7137dceab9d85462a8c4ea8e5e1090';
const patterns = [
  '01110100011001110101110011000101110',
  '00100011000010000100001000010001110',
  '01110100010000100010001000100011111',
  '11110000010000101110000010000111110',
  '00010001100101010010111110001000010',
  '11111100001000011110000010000111110',
  '01110100001000011110100011000101110',
  '11111000010001000100010000100001000',
  '01110100011000101110100011000101110',
  '01110100011000101111000010000101110',
].map(s => [...s].map(Number));
const body=Buffer.from(BODY,'hex');
assert.equal(body.length, 52);
const checkpoint = Buffer.concat([body,createHash('sha256').update(body).digest()]);
assert.equal(checkpoint.length, 84);
const restored=decodePrototypes(checkpoint);
assert.deepEqual(encodePrototypes(restored), checkpoint);
assert.deepEqual(restored.map(row=>row.reduce((a,b)=>a+b,0)),[17,19,19,14,20,19,14,22,15,14]);
for(let k=0;k<3;k++)assert.deepEqual(decodePrototypes(Buffer.from(checkpoint)),restored);
for(const pos of [0,8,36,51,52,70,83]){
 const bad=Buffer.from(checkpoint);bad[pos]^=1;
 assert.throws(()=>decodePrototypes(bad),/DWSA06_CODEC_REJECT/);
}
function seededRandom(seed){return()=>{seed|=0;seed=(seed+0x6d2b79f5)|0;let t=Math.imul(seed^(seed>>>15),1|seed);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296}}
const draw=seededRandom(637127);
const correctByClass=Array(10).fill(0);
for(let c=0;c<10;c++)for(let r=0;r<200;r++){
 const obs=patterns[c].map(bit=>draw()<0.07?1-bit:bit);
 const guess=classifyPrototypes(restored,obs);
 if(guess===c)correctByClass[c]++;
}
assert.deepEqual(correctByClass,[198,106,124,195,196,176,194,65,180,181]);
assert.equal(correctByClass.reduce((a,b)=>a+b,0),1615);
console.log(JSON.stringify({
 node:process.version, qualification:'DONOR_DERIVED_84_BYTE_CHECKPOINT_NODE_PASS',
 native_checkpoint_bytes:checkpoint.length, checkpoint_sha256:createHash('sha256').update(checkpoint).digest('hex'),
 original_source_commit:'149a2838309efe6ee5ec9e8c9689e4a321158b7d',
 original_donor_blob:'16ea8cf939bfa0f5f21e227d159b11d4ff578eca',
 original_template_blob:'6f95eea88422ceb01b3118e65cd45b9a4c065bd9',
 original_compiler_blob:'eee673dd0e8af3089bc5d1b686e4e00627940ead',
 schema:'dwsa06.donor_derived_checkpoint_node_replay.v1',
 scores:{correct:1615,n:2000,accuracy:0.8075,per_class:correctByClass},
 cold_restores:3, tamper_rejections:7, original_donor_forward_calls:0, source_first_use:false,
 scientific:'UNVERIFIED', deployment:'NONE',
},null,2));
