param(
    [Parameter(Mandatory=$true)][string]$RepoPath,
    [Parameter(Mandatory=$true)][string]$Repository,
    [Parameter(Mandatory=$true)][string]$ActiveBranch,
    [Parameter(Mandatory=$true)][string]$NorthStarPath,
    [Parameter(Mandatory=$true)][string]$NorthStarSha256,
    [string]$Trigger = 'manual',
    [string]$ResultPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-CanonicalTextSha256([string]$Path) {
    $Text=[IO.File]::ReadAllText($Path)
    $Normalized=$Text.Replace("`r`n","`n").Replace("`r","`n")
    $Utf8NoBom=New-Object Text.UTF8Encoding($false)
    $Bytes=$Utf8NoBom.GetBytes($Normalized)
    $Sha=[Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($Sha.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant()
    } finally {
        $Sha.Dispose()
    }
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & git -C $RepoPath @Args
    if($LASTEXITCODE -ne 0){throw "GIT_FAILED exit=$LASTEXITCODE args=$($Args -join ' ')"}
}

function Get-CommitFiles([string]$Commit){
    $Files=@(& git -C $RepoPath diff-tree --no-commit-id --name-only -r $Commit)
    if($LASTEXITCODE-ne0){throw "DIFF_TREE_FAILED commit=$Commit"}
    return @($Files|Where-Object{$_ -and $_.Trim()})
}

function Write-CycleResult([bool]$Advanced,[string]$Reason,[string]$Head){
    if([string]::IsNullOrWhiteSpace($ResultPath)){return}
    $Obj=[ordered]@{
        schema='research.repo-local-cycle-result.v1'
        program='Yggdrasil'
        advanced=$Advanced
        reason=$Reason
        head_sha=$Head
        generated_at_utc=[DateTime]::UtcNow.ToString('o')
    }
    $Dir=Split-Path -Parent $ResultPath
    if($Dir){New-Item -ItemType Directory -Force -Path $Dir|Out-Null}
    $Obj|ConvertTo-Json -Depth 20|Set-Content -LiteralPath $ResultPath -Encoding UTF8
}

function Resolve-Codex {
    foreach($P in @(
        'C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\bin\codex.exe',
        'C:\ProgramData\CKBR\codex\bin\codex.exe'
    )){
        if(Test-Path -LiteralPath $P -PathType Leaf){return $P}
    }
    $Cmd=Get-Command codex -ErrorAction SilentlyContinue
    if($Cmd){return $Cmd.Source}
    throw 'CODEX_NOT_AVAILABLE'
}

function Resolve-Python {
    foreach($P in @(
        'C:\ProgramData\CKBR\research-sidecar-yggdrasil\python312\python.exe',
        (Join-Path $env:RUNNER_TEMP 'python312-ygg-repo-local\python.exe')
    )){
        if(Test-Path -LiteralPath $P -PathType Leaf){return $P}
    }
    throw 'YGG_PYTHON_RUNTIME_MISSING'
}

function Get-OptionalMindContext([int]$MaxChars=12000){
    $Candidates=New-Object Collections.Generic.List[string]
    $RepoContext=Join-Path $RepoPath '.research-autonomy\mind-palace-context.txt'
    $Candidates.Add($RepoContext)
    if(-not[string]::IsNullOrWhiteSpace($env:MIND_PALACE_CONTEXT_PATH)){$Candidates.Add($env:MIND_PALACE_CONTEXT_PATH)}
    foreach($P in @(
        'C:\ProgramData\CKBR\mind-palace\contexts\Yggdrasil.txt',
        'C:\ProgramData\CKBR\mind-palace\Yggdrasil-context.txt'
    )){$Candidates.Add($P)}
    foreach($P in $Candidates){
        if(-not(Test-Path -LiteralPath $P -PathType Leaf)){continue}
        $Text=[IO.File]::ReadAllText($P)
        if($Text.Length-gt$MaxChars){$Text=$Text.Substring(0,$MaxChars)}
        Write-Host "MIND_PALACE_CONTEXT_USED path=$P chars=$($Text.Length)"
        return $Text
    }
    Write-Host 'MIND_PALACE_CONTEXT_UNAVAILABLE_FALLBACK=repository-lineage'
    return ''
}

if(-not(Test-Path -LiteralPath $RepoPath -PathType Container)){throw "REPO_PATH_MISSING path=$RepoPath"}
if([string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)){throw 'GITHUB_TOKEN_MISSING'}

Push-Location $RepoPath
try{
    $Branch=((& git branch --show-current 2>$null|Select-Object -First 1)|Out-String).Trim()
    if($Branch-cne$ActiveBranch){throw "ACTIVE_BRANCH_MISMATCH expected=$ActiveBranch actual=$Branch"}

    $StartSha=(& git rev-parse HEAD).Trim()
    if($LASTEXITCODE-ne0){throw 'START_HEAD_READ_FAILED'}
    if(((& git status --porcelain)-join'').Trim()){throw 'START_WORKTREE_DIRTY'}

    $NorthStarFull=Join-Path $RepoPath $NorthStarPath
    if(-not(Test-Path -LiteralPath $NorthStarFull -PathType Leaf)){throw "NORTH_STAR_MISSING path=$NorthStarPath"}
    $NorthStarActual=Get-CanonicalTextSha256 $NorthStarFull
    if($NorthStarActual-cne$NorthStarSha256.ToLowerInvariant()){throw "NORTH_STAR_IDENTITY_DRIFT expected=$NorthStarSha256 actual=$NorthStarActual"}

    $StatePath=Join-Path $RepoPath '.research-autonomy\state.json'
    if($Trigger-ceq'schedule' -and (Test-Path -LiteralPath $StatePath -PathType Leaf)){
        try{
            $State=Get-Content -Raw -LiteralPath $StatePath|ConvertFrom-Json
            $Last=[DateTime]::Parse([string]$State.last_completed_utc).ToUniversalTime()
            $Age=([DateTime]::UtcNow-$Last).TotalMinutes
            if($Age-lt45){
                Write-Host "RESEARCH_AUTONOMY_WATCHDOG_SKIP age_minutes=$([math]::Round($Age,1))"
                Write-CycleResult -Advanced $false -Reason 'watchdog-recent-progress' -Head $StartSha
                return
            }
        }catch{
            Write-Host "RESEARCH_AUTONOMY_STATE_PARSE_WARNING $($_.Exception.Message)"
        }
    }

    git config user.name 'repo-local-research-autonomy'
    git config user.email 'repo-local-research-autonomy@users.noreply.github.com'

    $RunRoot=Join-Path $env:RUNNER_TEMP ("yggdrasil-repo-local-"+$env:GITHUB_RUN_ID+"-"+$env:GITHUB_RUN_ATTEMPT)
    if(Test-Path -LiteralPath $RunRoot){Remove-Item -LiteralPath $RunRoot -Recurse -Force}
    New-Item -ItemType Directory -Force -Path $RunRoot|Out-Null

    $MindContext=Get-OptionalMindContext
    $PromptPath=Join-Path $RunRoot 'agent-prompt.txt'
    $LastMessagePath=Join-Path $RunRoot 'agent-last-message.txt'
    $Prompt=@"
You are the bounded repo-local autonomous research worker for Yggdrasil.

AUTHORITY AND SCOPE
- Synthetic computational research only. No wetware or living tissue.
- You may modify only this Yggdrasil research checkout.
- CKB-plane is governance-only and is NOT part of this execution cycle.
- Never modify CKB, ckb-plane, KTRADE, accepted refs, production systems, broker/live interfaces, credentials, runner configuration, or authority configuration.
- Do not push to GitHub. The deterministic wrapper validates, qualifies, records evidence, and pushes.
- Do not create another scheduler, queue consumer, daemon, or retry loop.

FROZEN PROGRAM IDENTITY
- Active branch: $ActiveBranch
- Exact parent SHA for this cycle: $StartSha
- North Star path: $NorthStarPath
- North Star SHA-256: $NorthStarSha256

SCIENTIFIC CONTINUATION
1. Read the North Star, the complete current experiment/preregistration lineage, .research-autonomy evidence if present, .yggdrasil/qualification-request.json, and .yggdrasil/isolated-run.json.
2. Treat supported, mixed, null, and negative scientific outcomes as evidence. Do not weaken an assertion or retune a threshold to make a result pass.
3. Derive exactly ONE bounded next question that materially reduces uncertainty toward the North Star.
4. Before implementation, create exactly ONE new preregistration under research/experiments/*.ice. Freeze the question/hypothesis, exact parent SHA, arms/inputs, seeds, budgets, metrics, thresholds, controls, validity criteria, classification rules, stop conditions, and no-post-result-tuning rule.
5. Commit that preregistration ALONE as the first commit after $StartSha.
6. Then implement only the bounded experiment. Keep changes inside research/experiments/, research/applications/plane/, .yggdrasil/qualification-request.json, and .yggdrasil/isolated-run.json.
7. The final implementation commit must update BOTH .yggdrasil/qualification-request.json and .yggdrasil/isolated-run.json.
8. Qualification request schema must be yggdrasil.research-qualification-request.v1. Its branch MUST be $ActiveBranch and baseline_sha MUST be $StartSha.
9. Source must be research/applications/plane/*.py and must emit schema yggdrasil.research-scientific-result.v1 with an experiment field matching the request and a metrics object.
10. isolated-run schema must be 1, request_id must match the experiment, source must match the qualification request, timeout_seconds must be 1..1800, run_args must contain exactly one {out}, and open_args must remain empty.
11. Preserve fixed resources, frozen scientific controls, disjoint seeds where required, deterministic duplicate runs, and no post-result threshold/budget/capacity tuning.
12. Make all required commits locally with concise research commit messages. Leave the worktree clean.

If evidence is insufficient, provenance is incomplete, the next question would widen authority, or safe continuation is ambiguous, make no changes and exit nonzero with a clear blocker.

OPTIONAL ADVISORY MIND-PALACE CONTEXT
$MindContext
"@
    [IO.File]::WriteAllText($PromptPath,$Prompt,(New-Object Text.UTF8Encoding($false)))

    $Codex=Resolve-Codex
    $OldCodeHome=$env:CODEX_HOME
    $OldHome=$env:HOME
    $OldProfile=$env:USERPROFILE
    try{
        $CodexHome='C:\ProgramData\CKBR\codex\home'
        if(Test-Path -LiteralPath $CodexHome -PathType Container){
            $env:CODEX_HOME=$CodexHome
            $env:HOME=$CodexHome
            $env:USERPROFILE=$CodexHome
        }
        $Models=@('gpt-5.6-sol','gpt-5.6-luna')
        $Succeeded=$false
        foreach($Model in $Models){
            Write-Host "RESEARCH_AGENT_ATTEMPT provider=codex model=$Model"
            $Args=@('exec','--sandbox','workspace-write','--approve-for-me','--model',$Model,'--output-last-message',$LastMessagePath,'-')
            $Proc=Start-Process -FilePath $Codex -ArgumentList $Args -WorkingDirectory $RepoPath -RedirectStandardInput $PromptPath -NoNewWindow -Wait -PassThru
            if($Proc.ExitCode-eq0){$Succeeded=$true;break}
            Write-Host "RESEARCH_AGENT_RETRY model=$Model exit=$($Proc.ExitCode)"
            & git reset --hard $StartSha|Out-Null
            & git clean -fd|Out-Null
        }
        if(-not$Succeeded){throw 'RESEARCH_AGENT_FAILED_ALL_MODELS'}
    }finally{
        $env:CODEX_HOME=$OldCodeHome
        $env:HOME=$OldHome
        $env:USERPROFILE=$OldProfile
    }

    if(((& git status --porcelain)-join'').Trim()){throw 'AGENT_LEFT_UNCOMMITTED_CHANGES'}
    $BranchAfter=((& git branch --show-current 2>$null|Select-Object -First 1)|Out-String).Trim()
    if($BranchAfter-cne$ActiveBranch){throw "AGENT_BRANCH_CHANGED expected=$ActiveBranch actual=$BranchAfter"}

    $Commits=@(& git rev-list --reverse "$StartSha..HEAD"|Where-Object{$_ -and $_.Trim()})
    if($LASTEXITCODE-ne0){throw 'REV_LIST_FAILED'}
    if($Commits.Count-lt2){throw "CONTINUATION_COMMIT_COUNT_TOO_SMALL count=$($Commits.Count)"}

    $AllFiles=New-Object Collections.Generic.List[string]
    foreach($Commit in $Commits){foreach($File in (Get-CommitFiles $Commit)){$AllFiles.Add($File)}}
    foreach($File in $AllFiles){
        if($File-match'(?i)(^|/)(ckb|ckb-plane|ktrade)(/|$)' -or $File-match'(?i)(coinbase|broker|credential|accepted-ref)'){throw "FORBIDDEN_PATH_CHANGE path=$File"}
        $Allowed=$File-eq'.yggdrasil/qualification-request.json' -or $File-eq'.yggdrasil/isolated-run.json' -or $File.StartsWith('research/experiments/') -or $File.StartsWith('research/applications/plane/')
        if(-not$Allowed){throw "CHANGE_OUTSIDE_RESEARCH_POLICY path=$File"}
    }

    $FirstFiles=@(Get-CommitFiles $Commits[0])
    if($FirstFiles.Count-ne1 -or -not$FirstFiles[0].StartsWith('research/experiments/') -or -not$FirstFiles[0].EndsWith('.ice')){
        throw "PREREG_NOT_FIRST_AND_ALONE files=$($FirstFiles -join ',')"
    }

    $QPath=Join-Path $RepoPath '.yggdrasil\qualification-request.json'
    $RPath=Join-Path $RepoPath '.yggdrasil\isolated-run.json'
    foreach($P in @($QPath,$RPath)){if(-not(Test-Path -LiteralPath $P -PathType Leaf)){throw "REQUEST_MISSING path=$P"}}
    $Q=Get-Content -Raw -LiteralPath $QPath|ConvertFrom-Json
    $R=Get-Content -Raw -LiteralPath $RPath|ConvertFrom-Json

    if([string]$Q.schema-cne'yggdrasil.research-qualification-request.v1'){throw 'QUALIFICATION_SCHEMA_INVALID'}
    if([string]$Q.branch-cne$ActiveBranch){throw "QUALIFICATION_BRANCH_MISMATCH expected=$ActiveBranch actual=$($Q.branch)"}
    if([string]$Q.baseline_sha-cne$StartSha){throw "QUALIFICATION_BASELINE_MISMATCH expected=$StartSha actual=$($Q.baseline_sha)"}
    if([string]$Q.experiment-notmatch'^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$'){throw 'QUALIFICATION_EXPERIMENT_INVALID'}
    if([string]$Q.source-notmatch'^research/applications/plane/[A-Za-z0-9._/-]+\.py$'){throw 'QUALIFICATION_SOURCE_INVALID'}
    if([string]$Q.isolated_run_path-cne'.yggdrasil/isolated-run.json'){throw 'QUALIFICATION_RUN_PATH_INVALID'}
    if([int]$R.schema-ne1){throw 'ISOLATED_RUN_SCHEMA_INVALID'}
    if([string]$R.request_id-cne[string]$Q.experiment){throw 'ISOLATED_RUN_REQUEST_ID_MISMATCH'}
    if([string]$R.source-cne[string]$Q.source){throw 'ISOLATED_RUN_SOURCE_MISMATCH'}
    if([int]$R.timeout_seconds-lt1 -or [int]$R.timeout_seconds-gt1800){throw 'ISOLATED_RUN_TIMEOUT_INVALID'}
    $RunArgs=@($R.run_args)
    if(($RunArgs|Where-Object{[string]$_-ceq'{out}'}).Count-ne1){throw 'ISOLATED_RUN_OUT_ARG_REQUIRED'}
    if(@($R.open_args).Count-ne0){throw 'ISOLATED_RUN_OPEN_ARGS_FORBIDDEN'}

    $SourceFull=Join-Path $RepoPath ([string]$Q.source)
    if(-not(Test-Path -LiteralPath $SourceFull -PathType Leaf)){throw "SOURCE_MISSING path=$($Q.source)"}
    $SourceText=Get-Content -Raw -LiteralPath $SourceFull
    if($SourceText-notmatch[regex]::Escape('yggdrasil.research-scientific-result.v1')){throw 'SOURCE_RESULT_SCHEMA_TOKEN_MISSING'}

    $LastFiles=@(Get-CommitFiles $Commits[-1])
    foreach($Required in @('.yggdrasil/qualification-request.json','.yggdrasil/isolated-run.json')){
        if($LastFiles-notcontains$Required){throw "FINAL_IMPLEMENTATION_COMMIT_MISSING_REQUEST path=$Required"}
    }

    $Py=Resolve-Python
    $ResultDir=Join-Path $RunRoot 'qualification'
    New-Item -ItemType Directory -Force -Path $ResultDir|Out-Null
    function Invoke-ScientificRun([string]$OutPath){
        $Args=New-Object Collections.Generic.List[string]
        foreach($A in @($R.run_args)){
            if([string]$A-ceq'{out}'){$Args.Add($OutPath)}else{$Args.Add([string]$A)}
        }
        & $Py $SourceFull @($Args)
        if($LASTEXITCODE-ne0){throw "SCIENTIFIC_RUN_FAILED exit=$LASTEXITCODE"}
        if(-not(Test-Path -LiteralPath $OutPath -PathType Leaf)){throw 'SCIENTIFIC_RESULT_MISSING'}
    }

    $Out1=Join-Path $ResultDir 'result-1.json'
    $Out2=Join-Path $ResultDir 'result-2.json'
    Invoke-ScientificRun $Out1
    Invoke-ScientificRun $Out2
    $B1=[IO.File]::ReadAllBytes($Out1)
    $B2=[IO.File]::ReadAllBytes($Out2)
    if($B1.Length-ne$B2.Length){throw 'SCIENTIFIC_RESULT_NONDETERMINISTIC_LENGTH'}
    for($I=0;$I-lt$B1.Length;$I++){if($B1[$I]-ne$B2[$I]){throw 'SCIENTIFIC_RESULT_NONDETERMINISTIC_BYTES'}}

    $Science=Get-Content -Raw -LiteralPath $Out1|ConvertFrom-Json
    if([string]$Science.schema-cne'yggdrasil.research-scientific-result.v1'){throw 'SCIENTIFIC_RESULT_SCHEMA_INVALID'}
    if([string]$Science.experiment-cne[string]$Q.experiment){throw 'SCIENTIFIC_RESULT_EXPERIMENT_MISMATCH'}
    if($null-eq$Science.metrics){throw 'SCIENTIFIC_RESULT_METRICS_MISSING'}

    if(((& git status --porcelain)-join'').Trim()){throw "QUALIFICATION_MUTATED_WORKTREE status=$((& git status --porcelain)-join';')"}

    $QualifiedHead=(& git rev-parse HEAD).Trim()
    $ResultSha=(Get-FileHash -LiteralPath $Out1 -Algorithm SHA256).Hash.ToLowerInvariant()
    $EvidenceDir=Join-Path $RepoPath '.research-autonomy\evidence'
    New-Item -ItemType Directory -Force -Path $EvidenceDir|Out-Null
    $ExperimentSafe=([string]$Q.experiment)-replace'[^A-Za-z0-9._-]','_'
    $BundleDir=Join-Path $EvidenceDir ("$ExperimentSafe-$env:GITHUB_RUN_ID")
    New-Item -ItemType Directory -Force -Path $BundleDir|Out-Null
    Copy-Item -LiteralPath $Out1 -Destination (Join-Path $BundleDir 'result.json') -Force

    $Summary=[ordered]@{
        schema='yggdrasil.repo-local-qualification-summary.v1'
        experiment=[string]$Q.experiment
        branch=$ActiveBranch
        baseline_sha=$StartSha
        qualified_head_sha=$QualifiedHead
        source=[string]$Q.source
        duplicate_byte_identical=$true
        result_sha256=$ResultSha
        platform='windows-self-hosted'
        runner_name=$env:RUNNER_NAME
        generated_at_utc=[DateTime]::UtcNow.ToString('o')
    }
    $Summary|ConvertTo-Json -Depth 20|Set-Content -LiteralPath (Join-Path $BundleDir 'summary.json') -Encoding UTF8

    $State=[ordered]@{
        schema='research.repo-local-state.v1'
        program='Yggdrasil'
        active_branch=$ActiveBranch
        north_star_path=$NorthStarPath
        north_star_sha256=$NorthStarSha256
        parent_sha=$StartSha
        qualified_head_sha=$QualifiedHead
        experiment=[string]$Q.experiment
        result_sha256=$ResultSha
        last_completed_utc=[DateTime]::UtcNow.ToString('o')
        github_run_id=$env:GITHUB_RUN_ID
        authority='research-only'
        ckb_plane_role='governance-only'
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $StatePath)|Out-Null
    $State|ConvertTo-Json -Depth 30|Set-Content -LiteralPath $StatePath -Encoding UTF8

    Invoke-Git add '.research-autonomy'
    Invoke-Git commit -m ("research: record qualified evidence for "+[string]$Q.experiment)
    $EvidenceHead=(& git rev-parse HEAD).Trim()
    Invoke-Git push origin ("HEAD:refs/heads/"+$ActiveBranch)

    Write-CycleResult -Advanced $true -Reason 'qualified-and-pushed' -Head $EvidenceHead
    Write-Host 'REPO_LOCAL_RESEARCH_CYCLE_PASS'
    Write-Host "experiment=$($Q.experiment)"
    Write-Host "parent_sha=$StartSha"
    Write-Host "qualified_head=$QualifiedHead"
    Write-Host "evidence_head=$EvidenceHead"
} catch {
    try{
        $Head=(& git -C $RepoPath rev-parse HEAD 2>$null|Select-Object -First 1)
        if($null-eq$Head){$Head=''}
        Write-CycleResult -Advanced $false -Reason $_.Exception.Message -Head ([string]$Head).Trim()
    }catch{}
    throw
} finally {
    Pop-Location
}
