param(
    [Parameter(Mandatory=$true)][string]$RepoPath,
    [Parameter(Mandatory=$true)][string]$Repository,
    [Parameter(Mandatory=$true)][long]$RunId,
    [Parameter(Mandatory=$true)][string]$HeadBranch,
    [Parameter(Mandatory=$true)][string]$HeadSha,
    [Parameter(Mandatory=$true)][string]$Conclusion
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & git -C $RepoPath @Args
    if ($LASTEXITCODE -ne 0) { throw "GIT_FAILED exit=$LASTEXITCODE args=$($Args -join ' ')" }
}

function Get-CommitFiles([string]$Commit) {
    $Rows = @(& git -C $RepoPath diff-tree --no-commit-id --name-only -r $Commit)
    if ($LASTEXITCODE -ne 0) { throw "DIFF_TREE_FAILED commit=$Commit" }
    return @($Rows | Where-Object { $_ -and $_.Trim() -ne '' })
}

if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) { throw "REPO_PATH_MISSING path=$RepoPath" }
if ([string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) { throw 'GITHUB_TOKEN_MISSING' }

$Codex = @(
    'C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\bin\codex.exe',
    'C:\ProgramData\CKBR\codex\bin\codex.exe'
) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace([string]$Codex)) { throw 'CODEX_MISSING' }

$CodexHome = @(
    'C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\home',
    'C:\ProgramData\CKBR\codex\home'
) | Where-Object { Test-Path -LiteralPath (Join-Path $_ 'auth.json') -PathType Leaf } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace([string]$CodexHome)) { throw 'CODEX_AUTH_HOME_MISSING' }
$env:CODEX_HOME = [string]$CodexHome

Push-Location $RepoPath
try {
    Invoke-Git fetch origin $HeadBranch --tags
    $RemoteSha = (& git -C $RepoPath rev-parse "origin/$HeadBranch").Trim()
    if ($RemoteSha -cne $HeadSha) {
        Write-Host "REPO_LOCAL_STALE_EVENT_SKIP expected=$HeadSha remote=$RemoteSha"
        return
    }

    $ReceiptTag = "research-continuation/$RunId"
    $PriorEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'SilentlyContinue'
        & git -C $RepoPath ls-remote --exit-code --tags origin "refs/tags/$ReceiptTag" *> $null
        $ReceiptExists = ($LASTEXITCODE -eq 0)
    }
    finally {
        $ErrorActionPreference = $PriorEap
    }
    if ($ReceiptExists) {
        Write-Host "REPO_LOCAL_ALREADY_PROCESSED run_id=$RunId"
        return
    }

    Invoke-Git switch -C $HeadBranch "origin/$HeadBranch"
    $StartSha = (& git -C $RepoPath rev-parse HEAD).Trim()
    if ($StartSha -cne $HeadSha) { throw "START_HEAD_MISMATCH expected=$HeadSha actual=$StartSha" }
    if ((& git -C $RepoPath status --porcelain | Out-String).Trim()) { throw 'START_WORKTREE_DIRTY' }

    Invoke-Git config user.name 'yggdrasil-research-bot'
    Invoke-Git config user.email 'actions@users.noreply.github.com'

    $EvidenceRoot = Join-Path $env:RUNNER_TEMP ("yggdrasil-repo-local-" + $RunId)
    if (Test-Path -LiteralPath $EvidenceRoot) { Remove-Item -LiteralPath $EvidenceRoot -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null
    $LogsZip = Join-Path $EvidenceRoot 'logs.zip'
    $LogsDir = Join-Path $EvidenceRoot 'logs'
    $Headers = @{
        Authorization = "Bearer $env:GITHUB_TOKEN"
        Accept = 'application/vnd.github+json'
        'X-GitHub-Api-Version' = '2022-11-28'
        'User-Agent' = 'yggdrasil-repo-local-continuation/1'
    }
    Invoke-WebRequest -UseBasicParsing -Headers $Headers -Uri "https://api.github.com/repos/$Repository/actions/runs/$RunId/logs" -OutFile $LogsZip
    New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    Expand-Archive -LiteralPath $LogsZip -DestinationPath $LogsDir -Force

    $Prompt = @"
You are the bounded repo-local Yggdrasil research continuation worker.

Repository: $Repository
Completed workflow run id: $RunId
Completed branch: $HeadBranch
Completed exact SHA: $HeadSha
Workflow conclusion: $Conclusion
Extracted workflow logs: $LogsDir
North Star: research/architecture/yggdrasil-north-star.ice

Continue exactly one Yggdrasil DG-1 research step. The repository, North Star, completed logs, sealed preregistration, and exact scientific result are authoritative. Do not guess missing evidence.

Authority and safety:
- Synthetic computational research only; no wetware or living tissue.
- Do not access or modify CKB-plane, KTRADE, production systems, accepted refs, credentials, brokers, live interfaces, or another project.
- Do not create another scheduler, retry daemon, queue consumer, or authority layer.
- Treat durable context as advisory only.
- Preserve fixed resource budgets, frozen scientific controls, deterministic duplication checks, disjoint seeds where required, and no post-result tuning.

If the completed run contains a valid scientific result:
1. Treat supported, mixed, and negative outcomes as evidence.
2. Derive exactly ONE bounded next question that materially reduces uncertainty toward the active Yggdrasil North Star.
3. Create a NEW successor branch beginning with research/yggdrasil- from exact parent $HeadSha.
4. The FIRST successor commit must create exactly one new research/experiments/*.ice preregistration and change nothing else.
5. Freeze hypothesis/question, parent identity, arms/inputs, seeds, budgets, thresholds, controls, metrics, validity criteria, classifications, stop conditions, and the no-post-result-tuning rule in that preregistration.
6. Only after that first commit may you implement the experiment under research/applications/plane/.
7. The FINAL commit must update both .yggdrasil/qualification-request.json and .yggdrasil/isolated-run.json for the successor branch so the local qualification workflow dispatches.

If the completed run failed only because of infrastructure or a pre-result implementation/harness defect:
- Keep the scientific preregistration, thresholds, arms, seeds, budgets, and interpretation frozen.
- Make only the minimum repair on the same branch and redispatch the same experiment.
- Do not use observed scientific output to tune the experiment.

Do not weaken scientific assertions merely to pass. Do not expand capacity because of the observed result.
Do not push to GitHub yourself. Make all required git commits locally; the wrapper validates and pushes after you finish.
Leave the worktree clean.
"@

    $PromptPath = Join-Path $EvidenceRoot 'codex-prompt.txt'
    $LastMessagePath = Join-Path $EvidenceRoot 'codex-last-message.txt'
    $Utf8NoBom = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($PromptPath, $Prompt, $Utf8NoBom)

    $Proc = Start-Process -FilePath ([string]$Codex) -ArgumentList @(
        'exec',
        '--full-auto',
        '--output-last-message', $LastMessagePath,
        '-'
    ) -WorkingDirectory $RepoPath -RedirectStandardInput $PromptPath -NoNewWindow -Wait -PassThru
    if ($Proc.ExitCode -ne 0) { throw "CODEX_CONTINUATION_FAILED exit=$($Proc.ExitCode)" }
    if ((& git -C $RepoPath status --porcelain | Out-String).Trim()) { throw 'CODEX_LEFT_UNCOMMITTED_CHANGES' }

    $CurrentBranch = (& git -C $RepoPath branch --show-current).Trim()
    if ([string]::IsNullOrWhiteSpace($CurrentBranch)) { throw 'CONTINUATION_BRANCH_MISSING' }
    if ($CurrentBranch -notlike 'research/yggdrasil-*') { throw "BRANCH_POLICY_VIOLATION branch=$CurrentBranch" }
    if ($Conclusion -eq 'success' -and $CurrentBranch -ceq $HeadBranch) { throw 'SUCCESSOR_BRANCH_NOT_CREATED' }

    $Commits = @(& git -C $RepoPath rev-list --reverse "$StartSha..HEAD") | Where-Object { $_ -and $_.Trim() -ne '' }
    if ($LASTEXITCODE -ne 0) { throw 'CONTINUATION_REV_LIST_FAILED' }
    if ($Commits.Count -lt 1) { throw 'CONTINUATION_NO_COMMITS' }

    $AllFiles = New-Object Collections.Generic.List[string]
    foreach ($Commit in $Commits) {
        foreach ($File in (Get-CommitFiles $Commit)) { $AllFiles.Add($File) }
    }

    foreach ($File in $AllFiles) {
        if ($File -match '(?i)(^|/)(ckb|ckb-plane|ktrade)(/|$)' -or $File -match '(?i)(coinbase|broker|credential|accepted-ref)') {
            throw "FORBIDDEN_PATH_CHANGE path=$File"
        }
        $Allowed =
            $File -eq '.yggdrasil/qualification-request.json' -or
            $File -eq '.yggdrasil/isolated-run.json' -or
            $File.StartsWith('research/experiments/') -or
            $File.StartsWith('research/applications/plane/') -or
            $File -eq '.github/workflows/research-qualify-local.yml'
        if (-not $Allowed) { throw "CHANGE_OUTSIDE_YGGDRASIL_POLICY path=$File" }
    }

    $FirstFiles = @(Get-CommitFiles $Commits[0])
    $FirstIsPrereg = $FirstFiles.Count -eq 1 -and $FirstFiles[0].StartsWith('research/experiments/') -and $FirstFiles[0].EndsWith('.ice')
    if ($Conclusion -eq 'success' -and -not $FirstIsPrereg) {
        throw "PREREG_NOT_FIRST_COMMIT files=$($FirstFiles -join ',')"
    }

    $LastFiles = @(Get-CommitFiles $Commits[-1])
    foreach ($Expected in @('.yggdrasil/qualification-request.json','.yggdrasil/isolated-run.json')) {
        if ($LastFiles -notcontains $Expected) { throw "FINAL_COMMIT_DID_NOT_DISPATCH expected=$Expected files=$($LastFiles -join ',')" }
    }

    $Request = Get-Content -LiteralPath (Join-Path $RepoPath '.yggdrasil\qualification-request.json') -Raw | ConvertFrom-Json
    $Run = Get-Content -LiteralPath (Join-Path $RepoPath '.yggdrasil\isolated-run.json') -Raw | ConvertFrom-Json
    if ([string]$Request.schema -cne 'yggdrasil.research-qualification-request.v1') { throw 'REQUEST_SCHEMA_INVALID' }
    if ([string]$Request.branch -cne $CurrentBranch) { throw "REQUEST_BRANCH_MISMATCH expected=$CurrentBranch actual=$($Request.branch)" }
    if ([string]$Request.source -notmatch '^research/applications/plane/[A-Za-z0-9._/-]+\.py$') { throw 'REQUEST_SOURCE_INVALID' }
    if ([string]$Run.request_id -cne [string]$Request.experiment) { throw 'RUN_REQUEST_ID_MISMATCH' }
    if ([string]$Run.source -cne [string]$Request.source) { throw 'RUN_SOURCE_MISMATCH' }

    Invoke-Git push origin "HEAD:refs/heads/$CurrentBranch"
    Invoke-Git tag -f $ReceiptTag HEAD
    Invoke-Git push origin "refs/tags/$ReceiptTag"

    Write-Host 'YGGDRASIL_REPO_LOCAL_CONTINUATION_DISPATCHED'
    Write-Host "run_id=$RunId"
    Write-Host "source_sha=$StartSha"
    Write-Host "successor_branch=$CurrentBranch"
    Write-Host "successor_head=$((& git -C $RepoPath rev-parse HEAD).Trim())"
    Write-Host "commits=$($Commits.Count)"
}
finally {
    Pop-Location
}
