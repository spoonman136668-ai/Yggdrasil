/** WSP-196 exact original GB1 reproduction. Never run against nonmatching input.
 * Reads local source bytes only, writes no files, and checks the sealed result.
 * An independent rerun is a NEW science action, not evidence of first-run acceptance.
 */
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {evaluateWSP196} from "./evaluate.mjs";
if(process.argv.length!==3)throw Error("USAGE: node reproduce.mjs /authorized/original/Mutfit");
const root=dirname(fileURLToPath(import.meta.url)),buffer=readFileSync(resolve(process.argv[2]));
if(buffer.length!==13837211)throw Error("ORIGINAL_BYTES_SIZE_DRIFT");
const content=Buffer.concat([Buffer.from("blob "+buffer.length+"\0","ascii"),buffer]);
const sha=createHash("sha1").update(content).digest("hex");
if(sha!=="3bf094f1b5c8bd84a35e04ae9c23bcf97c2bfa89")throw Error("ORIGINAL_GIT_BLOB_SHA_MISMATCH");
const sealed=JSON.parse(readFileSync(resolve(root,"result.json"),"utf8"));
const reproduced=evaluateWSP196(buffer.toString("utf8"));
function approx(x,y,key){if(!Number.isFinite(x)||!Number.isFinite(y)||Math.abs(x-y)>1e-10*Math.max(1,Math.abs(x),Math.abs(y)))throw Error("WSP196_NOT_REPRODUCIBLE_"+key);}
approx(reproduced.candidate.dev_rmse,sealed.candidate.dev_rmse,"CANDIDATE");
approx(reproduced.strongest_control.dev_rmse,sealed.strongest_control.dev_rmse,"STRONG_CONTROL");
approx(reproduced.held.relative_gain_vs_strong,sealed.held.relative_gain_vs_strong,"GAIN");
approx(reproduced.held.bootstrap_95_lower,sealed.held.bootstrap_95_lower,"BOOT_LOWER");
approx(reproduced.held.bootstrap_95_upper,sealed.held.bootstrap_95_upper,"BOOT_UPPER");
if(reproduced.classification!==sealed.classification)throw Error("WSP196_CLASSIFICATION_CHANGED");
console.log(JSON.stringify({reproduction:"PASS",exact_original_blob:sha,development:sealed.classification,
scientific_pass:false,original_data_redistributed:false,runner_dispatch:false}));
