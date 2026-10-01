Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$ExpectedSha='91e4472282144d964988a667beae5dd2742b8a88'
$ExpectedTree='e21bd42bd27ac9a725cd45e4d15f21fb66a8f894'
$Cache='C:\ProgramData\CKBR\research-sidecar-yggdrasil\workspaces\yggdrasil-baseline-cache'
$TaskName='CKBPlane Research Sidecar Yggdrasil'
$SidecarExe='C:\ProgramData\CKBR\research-sidecar-yggdrasil\bin\research-sidecar.exe'
$Branch='research/yggdrasil-exp-dg1b-critical-integration-window-016-r1'
$Remote='https://github.com/spoonman136668-ai/Yggdrasil.git'

if([string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)){throw 'GITHUB_TOKEN_MISSING'}
if(-not(Test-Path -LiteralPath $Cache -PathType Container)){throw "CACHE_MISSING path=$Cache"}

$ActualSha=(& git -C $Cache rev-parse $ExpectedSha).Trim()
if($LASTEXITCODE-ne0 -or $ActualSha-cne$ExpectedSha){throw "CACHE_SHA_MISMATCH actual=$ActualSha"}
$ActualTree=(& git -C $Cache rev-parse "$ExpectedSha^{tree}").Trim()
if($LASTEXITCODE-ne0 -or $ActualTree-cne$ExpectedTree){throw "CACHE_TREE_MISMATCH expected=$ExpectedTree actual=$ActualTree"}

$Pair="x-access-token:$env:GITHUB_TOKEN"
$Basic=[Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($Pair))
$Auth="http.https://github.com/.extraheader=AUTHORIZATION: basic $Basic"
$Existing=@(& git -c $Auth ls-remote --heads $Remote "refs/heads/$Branch")
if($LASTEXITCODE-ne0){throw 'REMOTE_BRANCH_PROBE_FAILED'}
if($Existing.Count-gt0){throw "REMOTE_BRANCH_ALREADY_EXISTS branch=$Branch"}

$Task=Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if($null-eq$Task){throw "SIDECAR_TASK_MISSING name=$TaskName"}
Disable-ScheduledTask -TaskName $TaskName -ErrorAction Stop | Out-Null
try{Stop-ScheduledTask -TaskName $TaskName -ErrorAction Stop}catch{}
Start-Sleep -Seconds 2
foreach($P in @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    ([string]$_.ExecutablePath).Trim() -ieq $SidecarExe
})){
    Stop-Process -Id $P.ProcessId -Force -ErrorAction Stop
}
Start-Sleep -Seconds 1
$Task=Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
if([string]$Task.State -eq 'Running'){throw 'SIDECAR_TASK_STILL_RUNNING'}
$Procs=@(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    ([string]$_.ExecutablePath).Trim() -ieq $SidecarExe
})
if($Procs.Count-ne0){throw "SIDECAR_PROCESS_STILL_RUNNING count=$($Procs.Count)"}
Write-Host "YGGDRASIL_SIDECAR_DISABLED state=$($Task.State)"

$Work=Join-Path $env:RUNNER_TEMP 'yggdrasil-repo-local-cutover-r1'
if(Test-Path -LiteralPath $Work){Remove-Item -LiteralPath $Work -Recurse -Force}
try{
    & git -C $Cache worktree add --detach $Work $ExpectedSha
    if($LASTEXITCODE-ne0){throw 'WORKTREE_ADD_FAILED'}
    $Head=(& git -C $Work rev-parse HEAD).Trim()
    $Tree=(& git -C $Work rev-parse 'HEAD^{tree}').Trim()
    if($Head-cne$ExpectedSha -or $Tree-cne$ExpectedTree){throw 'WORKTREE_IDENTITY_MISMATCH'}

    $ReqPath=Join-Path $Work '.yggdrasil\qualification-request.json'
    $Req=Get-Content -LiteralPath $ReqPath -Raw|ConvertFrom-Json
    if([string]$Req.schema-cne'yggdrasil.research-qualification-request.v1'){throw 'REQUEST_SCHEMA_INVALID'}
    if([string]$Req.branch-cne$Branch){throw "REQUEST_BRANCH_UNEXPECTED actual=$($Req.branch)"}
    if([string]$Req.experiment-cne'EXP-DG1B-CRITICAL-INTEGRATION-WINDOW-016'){throw "REQUEST_EXPERIMENT_UNEXPECTED actual=$($Req.experiment)"}
    $Req | Add-Member -NotePropertyName cutover_revision -NotePropertyValue 'repo-local-r1' -Force
    $Json=$Req|ConvertTo-Json -Depth 20 -Compress
    [IO.File]::WriteAllText($ReqPath,$Json,(New-Object Text.UTF8Encoding($false)))

    $WorkflowPath=Join-Path $Work '.github\workflows\research-qualify-local.yml'
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $WorkflowPath)|Out-Null
    $Workflow=@'
name: Yggdrasil local research qualification

on:
  push:
    branches:
      - 'research/yggdrasil-*'
    paths:
      - '.yggdrasil/qualification-request.json'
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: yggdrasil-local-research-${{ github.ref_name }}
  cancel-in-progress: false

jobs:
  qualify:
    runs-on: [self-hosted, Windows, X64, yggdrasil, research-only]
    timeout-minutes: 45
    defaults:
      run:
        shell: powershell -NoProfile -ExecutionPolicy Bypass -Command ". '{0}'"

    steps:
      - name: Checkout exact research head
        uses: actions/checkout@v4
        with:
          fetch-depth: 1
          persist-credentials: false
          clean: true

      - name: Validate sealed request
        id: req
        run: |
          $ErrorActionPreference='Stop'
          $QPath='.yggdrasil/qualification-request.json'
          $RPath='.yggdrasil/isolated-run.json'
          foreach($P in @($QPath,$RPath)){if(-not(Test-Path -LiteralPath $P -PathType Leaf)){throw "REQUEST_MISSING path=$P"}}
          $Q=Get-Content -LiteralPath $QPath -Raw|ConvertFrom-Json
          $R=Get-Content -LiteralPath $RPath -Raw|ConvertFrom-Json
          if([string]$Q.schema -cne 'yggdrasil.research-qualification-request.v1'){throw 'QUALIFICATION_SCHEMA_INVALID'}
          if([string]$Q.branch -cne $env:GITHUB_REF_NAME){throw "QUALIFICATION_BRANCH_MISMATCH expected=$($Q.branch) actual=$env:GITHUB_REF_NAME"}
          if([string]$Q.baseline_sha -notmatch '^[0-9a-f]{40}$'){throw 'QUALIFICATION_BASELINE_INVALID'}
          if([string]$Q.source -notmatch '^research/applications/plane/[A-Za-z0-9._/-]+\.py$'){throw 'QUALIFICATION_SOURCE_INVALID'}
          if([string]$Q.isolated_run_path -cne $RPath){throw 'QUALIFICATION_RUN_PATH_INVALID'}
          if([int]$R.schema -ne 1){throw 'ISOLATED_RUN_SCHEMA_INVALID'}
          if([string]$R.request_id -cne [string]$Q.experiment){throw 'ISOLATED_RUN_REQUEST_ID_MISMATCH'}
          if([string]$R.source -cne [string]$Q.source){throw 'ISOLATED_RUN_SOURCE_MISMATCH'}
          if([int]$R.timeout_seconds -lt 1 -or [int]$R.timeout_seconds -gt 1800){throw 'ISOLATED_RUN_TIMEOUT_INVALID'}
          if(-not(Test-Path -LiteralPath ([string]$Q.source) -PathType Leaf)){throw 'QUALIFICATION_SOURCE_MISSING'}
          git merge-base --is-ancestor ([string]$Q.baseline_sha) $env:GITHUB_SHA
          if($LASTEXITCODE-ne0){throw 'QUALIFICATION_BASELINE_ANCESTRY_FAILED'}
          "experiment=$($Q.experiment)" >> $env:GITHUB_OUTPUT
          "source=$($Q.source)" >> $env:GITHUB_OUTPUT

      - name: Bind frozen Python runtime
        run: |
          $ErrorActionPreference='Stop'
          $Py='C:\ProgramData\CKBR\research-sidecar-yggdrasil\python312\python.exe'
          if(-not(Test-Path -LiteralPath $Py -PathType Leaf)){throw "PYTHON_RUNTIME_MISSING path=$Py"}
          "YGG_PYTHON=$Py" >> $env:GITHUB_ENV
          & $Py --version

      - name: Run sealed experiment twice
        run: |
          $ErrorActionPreference='Stop'
          $Q=Get-Content -LiteralPath '.yggdrasil/qualification-request.json' -Raw|ConvertFrom-Json
          $R=Get-Content -LiteralPath '.yggdrasil/isolated-run.json' -Raw|ConvertFrom-Json
          $Root=Join-Path $env:RUNNER_TEMP 'ygg-local-result'
          if(Test-Path -LiteralPath $Root){Remove-Item -LiteralPath $Root -Recurse -Force}
          New-Item -ItemType Directory -Force -Path $Root|Out-Null
          function Invoke-One([string]$Out){
            $Args=@()
            foreach($A in @($R.run_args)){if([string]$A -ceq '{out}'){$Args+=$Out}else{$Args+=[string]$A}}
            & $env:YGG_PYTHON ([string]$Q.source) @Args
            if($LASTEXITCODE-ne0){throw "SCIENTIFIC_RUN_FAILED exit=$LASTEXITCODE"}
            if(-not(Test-Path -LiteralPath $Out -PathType Leaf)){throw 'SCIENTIFIC_RESULT_MISSING'}
          }
          $A=Join-Path $Root 'result-1.json'
          $B=Join-Path $Root 'result-2.json'
          Invoke-One $A
          Invoke-One $B
          $BA=[IO.File]::ReadAllBytes($A);$BB=[IO.File]::ReadAllBytes($B)
          if($BA.Length-ne$BB.Length){throw 'SCIENTIFIC_RESULT_NONDETERMINISTIC_LENGTH'}
          for($i=0;$i-lt$BA.Length;$i++){if($BA[$i]-ne$BB[$i]){throw 'SCIENTIFIC_RESULT_NONDETERMINISTIC_BYTES'}}
          $S=Get-Content -LiteralPath $A -Raw|ConvertFrom-Json
          if([string]$S.schema -cne 'yggdrasil.research-scientific-result.v1'){throw 'SCIENTIFIC_RESULT_SCHEMA_INVALID'}
          if([string]$S.experiment -cne [string]$Q.experiment){throw 'SCIENTIFIC_RESULT_EXPERIMENT_MISMATCH'}
          if($null-eq$S.metrics){throw 'SCIENTIFIC_RESULT_METRICS_MISSING'}
          $Sha=(Get-FileHash -LiteralPath $A -Algorithm SHA256).Hash.ToLowerInvariant()
          Write-Host 'SCIENTIFIC_RESULT_BEGIN'
          Get-Content -LiteralPath $A -Raw
          Write-Host 'SCIENTIFIC_RESULT_END'
          Write-Host "scientific_result_sha256=$Sha"
          Write-Host 'YGGDRASIL_LOCAL_QUALIFICATION=PASS'

      - name: Upload scientific evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: yggdrasil-local-${{ github.run_id }}
          path: ${{ runner.temp }}\ygg-local-result\**
          if-no-files-found: warn
          retention-days: 30
'@
    [IO.File]::WriteAllText($WorkflowPath,$Workflow,(New-Object Text.UTF8Encoding($false)))

    & git -C $Work config user.name 'yggdrasil-research-bot'
    & git -C $Work config user.email 'actions@users.noreply.github.com'
    & git -C $Work add -- '.yggdrasil/qualification-request.json' '.github/workflows/research-qualify-local.yml'
    $Changed=@(& git -C $Work diff --cached --name-only)
    if($Changed.Count-ne2 -or $Changed-notcontains'.yggdrasil/qualification-request.json' -or $Changed-notcontains'.github/workflows/research-qualify-local.yml'){
        throw "CUTOVER_SCOPE_INVALID files=$($Changed -join ',')"
    }
    & git -C $Work commit -m 'infra: cut over Yggdrasil research to repo-local continuation'
    if($LASTEXITCODE-ne0){throw 'CUTOVER_COMMIT_FAILED'}
    $CutoverHead=(& git -C $Work rev-parse HEAD).Trim()

    & git -C $Work -c $Auth push $Remote "HEAD:refs/heads/$Branch"
    if($LASTEXITCODE-ne0){throw 'CUTOVER_PUSH_FAILED'}

    $RemoteLine=@(& git -c $Auth ls-remote --heads $Remote "refs/heads/$Branch")
    if($LASTEXITCODE-ne0 -or $RemoteLine.Count-ne1){throw 'CUTOVER_REMOTE_VERIFY_FAILED'}
    $RemoteSha=(([string]$RemoteLine[0])-split '\s+')[0]
    if($RemoteSha-cne$CutoverHead){throw "CUTOVER_REMOTE_SHA_MISMATCH expected=$CutoverHead actual=$RemoteSha"}

    Write-Host 'YGGDRASIL_REPO_LOCAL_CUTOVER=PASS'
    Write-Host "sealed_sha=$ExpectedSha"
    Write-Host "sealed_tree=$ExpectedTree"
    Write-Host "cutover_head=$CutoverHead"
    Write-Host "branch=$Branch"
}
finally{
    if(Test-Path -LiteralPath $Work){
        & git -C $Cache worktree remove --force $Work 2>$null
    }
}
