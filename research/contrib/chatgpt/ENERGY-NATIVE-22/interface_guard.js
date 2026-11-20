/* ENERGY-NATIVE-22: fail-closed, read-only static interface compatibility survey.
 * Consumes in-memory GitHub-readback source documents. Never mutates, imports,
 * executes, restores or trains a Yggdrasil learner.
 * CLI: node interface_guard.js snapshot.json
 */
const EnergyNative22=(()=>{
"use strict";
const paths={
 amalgam:"yggdrasil/native_causal_amalgam.py",
 cumulative:"yggdrasil/native_cumulative_learner.py",
 episode:"yggdrasil/native_episode_experience.py",
 staged:"research/contrib/chatgpt/CAUSAL-AMALGAM/staged_public_readout.py",
 retention:"research/contrib/chatgpt/CAUSAL-AMALGAM/retention_guard.py",
 synthetic:"research/contrib/chatgpt/ENERGY-FACTORS-21/experiment.js"
};
function inspect(contract,snapshot){
 const checks=[];
 function ck(id,ok,evidence){checks.push({id,pass:!!ok,evidence});}
 const pinned=contract.amalgam_owner_source_sha;
 ck("contract_source_pin",snapshot.ref===pinned,pinned);
 const files={};
 for(const [alias,path] of Object.entries(paths)){
  const found=snapshot.files[path];
  const expectation=contract.source_files.find(o=>o.path===path);
  const sha=expectation?.git_blob||(alias==="synthetic"?"5c2955056800123fd10c13bf5d1b7abc1e23a820":null);
  const ok=found&&typeof found.content==="string"&&found.content.length>0&&found.git_blob===sha;
  ck("exact_blob_"+alias,!!ok,path+" @ "+sha);
  files[alias]=ok?found.content:"";
 }
 const contains=(name,...needles)=>needles.every(x=>files[name].includes(x));
 ck("cumulative_stage_only_pinned_packets",contains("cumulative",
   "def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256, repair=None):",
   "source_sha256 == EXPERIENCE_SOURCE","packet_sha256","EPISODE_REQUIRES_INTEGRATED_PARENT"),
   paths.cumulative);
 ck("native_shared_update_is_the_one_entrypoint",contains("amalgam",
   "class NativeCausalAmalgam:","def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):",
   "self.native.observe_experience("),paths.amalgam);
 ck("native_pinned_cold_restore_existing",contains("amalgam",
   "def checkpoint(self):","def restore(cls, raw, expected_sha, *, native_parent, native_pin, donor_parent, donor_pin):",
   "AMALGAM_NATIVE_PREFIX","AMALGAM_NATIVE_REPLAY"),paths.amalgam);
 ck("native_episode_binary_views",contains("episode",
   "def _view(value):","len(value) == 2","def _views(value):","def observe(self, identifier, views, row):"),paths.episode);
 ck("native_row_fields_are_staged",contains("episode",
   'ROW_FIELDS = ("s1", "x1", "s2", "x2", "y")',
   'bits = [PublicCausalCells._bit(row[name], name.upper()) for name in ROW_FIELDS]'),paths.episode);
 ck("staged_actions_and_observation_order",contains("staged",
   "def first_action(self, action):","def observe_transition(self, state):",
   "def second_action(self, action):","def observe_reward(self, reward):",
   "self._model.observe_experience("),paths.staged);
 ck("staged_transition_not_exogenous_action",contains("staged",
   "self._state = PublicCausalCells._bit(state, \"S2\")",
   '"s2": self._state','"x1": self._first','"x2": self._second'),
   paths.staged);
 ck("retention_guard_existing_read_only_prefix",contains("retention",
   "def evaluate(anchor, candidate, windows, *, max_brier_drift):",
   "if new[:len(old)] != old:","readout_losses(anchor, historical)",
   "readout_losses(candidate, historical)"),paths.retention);
 ck("synthetic_direct_32_interventions",contains("synthetic",
   "const NOISE=.20,CHANGE=.25,INPUTS=32,OLD_N=24,NEW_N=16;",
   "const actions=contexts.slice(0,12);",
   "const x=mix(seed,scenario,\"oldinput\",k)%INPUTS;"),paths.synthetic);
 ck("synthetic_outcomes_are_not_native_experience_packets",
   !files.synthetic.includes("NativeCausalAmalgam")&&!files.synthetic.includes("StagedPublicReadout"),
   "No witnessed staged-episode mapping or native class usage in frozen Gate 21 source.");
 const staticInterfacePass=checks.every(x=>x.pass);
 return {
  schema:"energy-native-22-static-compatibility.v1",
  owner_source_commit:pinned,source_tree_status:"exact five pinned Git blobs, independent of current future owner head",
  static_interface_pass:staticInterfacePass,checks,
  direct_synthetic_to_native_translation:"UNVERIFIED_FAIL_CLOSED",
  native_cold_process_test:"NOT_RUN",
  original_source_replay:"NOT_RUN",
  empirical_native_transfer:"NOT_RUN",
  full_regression:"NOT_RUN",
  scientific_pass:false,deployable:false,
  reason:"Gate21 directly intervenes on 32 five-bit contexts. Native witness contract has two staged binary actions, an observed intermediary state and an observed reward. There is no proven source-faithful five-bit do-action -> staged episode mapping. Static ABI checks cannot establish a native learning or retention gain.",
  existing_qualified_path:"Amalgam owner PR #1278: staged readouts, pinned observe_experience, checkpoint/restore, historical retention_guard.evaluate; requires owner-authorized sealed native parent checkpoints, action-matched original witnesses, fresh held transfer and independent cold restore.",
  action_required:"NONE for contributor. Native first-use, runner dispatch, checkpoint promotion and merges remain owner-gated."
 };
}
return {inspect};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyNative22;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs");
  const input=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));
  const report=EnergyNative22.inspect(input.contract,input.snapshot);
  process.stdout.write(JSON.stringify(report,null,2)+"\n");
  if(!report.static_interface_pass)process.exitCode=1;
 }
}
