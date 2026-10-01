Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$Controller=(Resolve-Path 'controller').Path
$Research=(Resolve-Path 'research').Path
$Expected='91e4472282144d964988a667beae5dd2742b8a88'
$ExpectedNorth='3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905'

$C=Get-Content -Raw -LiteralPath (Join-Path $Controller '.research-autonomy\config.json')|ConvertFrom-Json
if($C.schema-cne'research.autonomy.v2'){throw 'CONFIG_SCHEMA_INVALID'}
if([bool]$C.enabled){throw 'CONFIG_MUST_BE_DISABLED_DURING_FINAL_GATE'}
if($C.ckb_plane_role-cne'governance-only'){throw 'CKB_PLANE_ROLE_INVALID'}
if($C.active_branch-cne'research/autonomy-yggdrasil-active'){throw 'ACTIVE_BRANCH_INVALID'}
if($C.north_star_sha256-cne$ExpectedNorth){throw 'NORTH_STAR_CONFIG_IDENTITY_INVALID'}

$ControllerPath=Join-Path $Controller 'scripts\Invoke-RepoLocalResearchCycle.ps1'
$Tokens=$null;$Errors=$null
[void][Management.Automation.Language.Parser]::ParseFile($ControllerPath,[ref]$Tokens,[ref]$Errors)
if(@($Errors).Count){throw "CONTROLLER_PARSE_FAILED count=$(@($Errors).Count)"}

$Head=(& git -C $Research rev-parse HEAD).Trim()
if($Head-cne$Expected){throw "ACTIVE_HEAD_DRIFT expected=$Expected actual=$Head"}
if(((& git -C $Research status --porcelain)-join'').Trim()){throw 'ACTIVE_WORKTREE_DIRTY'}

$NorthPath=Join-Path $Research 'research\architecture\yggdrasil-north-star.ice'
$North=(Get-FileHash -LiteralPath $NorthPath -Algorithm SHA256).Hash.ToLowerInvariant()
if($North-cne$ExpectedNorth){throw "NORTH_STAR_DRIFT expected=$ExpectedNorth actual=$North"}

foreach($TaskName in @('CKBPlane Research Sidecar','CKBPlane Research Sidecar Yggdrasil')){
  $T=Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
  Write-Host "TASK name=$TaskName state=$($T.State)"
  if([string]$T.State-cne'Disabled'){throw "RESEARCH_SIDECAR_NOT_DISABLED name=$TaskName state=$($T.State)"}
}

$Codex='C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\bin\codex.exe'
$Py='C:\ProgramData\CKBR\research-sidecar-yggdrasil\python312\python.exe'
foreach($P in @($Codex,$Py)){if(-not(Test-Path -LiteralPath $P -PathType Leaf)){throw "RUNTIME_MISSING path=$P"}}
& $Codex --version
if($LASTEXITCODE-ne0){throw 'CODEX_VERSION_FAILED'}
& $Py --version
if($LASTEXITCODE-ne0){throw 'PYTHON_VERSION_FAILED'}
& $Py -c "import numpy, torch; print('numpy='+numpy.__version__); print('torch='+torch.__version__)"
if($LASTEXITCODE-ne0){throw 'PYTHON_DEPENDENCIES_FAILED'}

$Q=Get-Content -Raw -LiteralPath (Join-Path $Research '.yggdrasil\qualification-request.json')|ConvertFrom-Json
$R=Get-Content -Raw -LiteralPath (Join-Path $Research '.yggdrasil\isolated-run.json')|ConvertFrom-Json
if([string]$Q.schema-cne'yggdrasil.research-qualification-request.v1'){throw 'QUALIFICATION_SCHEMA_INVALID'}
if([string]$Q.experiment-cne'EXP-DG1B-CRITICAL-INTEGRATION-WINDOW-016'){throw "EXPERIMENT_DRIFT actual=$($Q.experiment)"}
if([string]$Q.branch-cne'research/yggdrasil-exp-dg1b-critical-integration-window-016-r1'){throw "SEALED_REQUEST_BRANCH_DRIFT actual=$($Q.branch)"}
if([string]$R.request_id-cne[string]$Q.experiment){throw 'RUN_REQUEST_ID_MISMATCH'}
if([string]$R.source-cne[string]$Q.source){throw 'RUN_SOURCE_MISMATCH'}
if(@($R.open_args).Count-ne0){throw 'RUN_OPEN_ARGS_FORBIDDEN'}
if((@($R.run_args)|Where-Object{[string]$_-ceq'{out}'}).Count-ne1){throw 'RUN_OUT_ARG_INVALID'}

$Source=Join-Path $Research ([string]$Q.source)
if(-not(Test-Path -LiteralPath $Source -PathType Leaf)){throw "SOURCE_MISSING path=$($Q.source)"}
$Root=Join-Path $env:RUNNER_TEMP 'ygg-final-gate'
if(Test-Path -LiteralPath $Root){Remove-Item -LiteralPath $Root -Recurse -Force}
New-Item -ItemType Directory -Force -Path $Root|Out-Null

function Invoke-One([string]$Out){
  $Args=@()
  foreach($A in @($R.run_args)){
    if([string]$A-ceq'{out}'){$Args+=$Out}else{$Args+=[string]$A}
  }
  Push-Location $Research
  try{
    & $Py $Source @Args
    if($LASTEXITCODE-ne0){throw "SCIENTIFIC_RUN_FAILED exit=$LASTEXITCODE"}
  }finally{Pop-Location}
  if(-not(Test-Path -LiteralPath $Out -PathType Leaf)){throw 'SCIENTIFIC_RESULT_MISSING'}
}

$O1=Join-Path $Root 'result-1.json'
$O2=Join-Path $Root 'result-2.json'
Invoke-One $O1
Invoke-One $O2
$B1=[IO.File]::ReadAllBytes($O1);$B2=[IO.File]::ReadAllBytes($O2)
if($B1.Length-ne$B2.Length){throw 'SCIENTIFIC_RESULT_NONDETERMINISTIC_LENGTH'}
for($I=0;$I-lt$B1.Length;$I++){if($B1[$I]-ne$B2[$I]){throw 'SCIENTIFIC_RESULT_NONDETERMINISTIC_BYTES'}}
$Science=Get-Content -Raw -LiteralPath $O1|ConvertFrom-Json
if([string]$Science.schema-cne'yggdrasil.research-scientific-result.v1'){throw 'SCIENTIFIC_RESULT_SCHEMA_INVALID'}
if([string]$Science.experiment-cne[string]$Q.experiment){throw 'SCIENTIFIC_RESULT_EXPERIMENT_MISMATCH'}
if($null-eq$Science.metrics){throw 'SCIENTIFIC_RESULT_METRICS_MISSING'}
$ResultSha=(Get-FileHash -LiteralPath $O1 -Algorithm SHA256).Hash.ToLowerInvariant()

Write-Host 'YGGDRASIL_REPO_LOCAL_FINAL_GATE=PASS'
Write-Host "active_head=$Head"
Write-Host "north_star_sha256=$North"
Write-Host "result_sha256=$ResultSha"
