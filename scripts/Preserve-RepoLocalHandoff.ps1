Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$Repo='spoonman136668-ai/Yggdrasil'
$Cache='C:\ProgramData\CKBR\research-sidecar-yggdrasil\workspaces\yggdrasil-baseline-cache'
$ExpectedSha='91e4472282144d964988a667beae5dd2742b8a88'
$ExpectedBranch='research/yggdrasil-exp-dg1b-critical-integration-window-016-r1'
$ExpectedExperiment='EXP-DG1B-CRITICAL-INTEGRATION-WINDOW-016'

if([string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)){throw 'GITHUB_TOKEN_MISSING'}
if(-not(Test-Path -LiteralPath $Cache -PathType Container)){throw "CACHE_MISSING path=$Cache"}

& git -C $Cache cat-file -e ($ExpectedSha+'^{commit}')
if($LASTEXITCODE-ne0){throw "EXPECTED_COMMIT_MISSING sha=$ExpectedSha"}

$RequestRaw=& git -C $Cache show ($ExpectedSha+':.yggdrasil/qualification-request.json')
if($LASTEXITCODE-ne0){throw 'QUALIFICATION_REQUEST_READ_FAILED'}
$Q=($RequestRaw -join [Environment]::NewLine)|ConvertFrom-Json
if([string]$Q.schema -cne 'yggdrasil.research-qualification-request.v1'){throw 'QUALIFICATION_SCHEMA_INVALID'}
if([string]$Q.experiment -cne $ExpectedExperiment){throw "EXPERIMENT_MISMATCH actual=$($Q.experiment)"}
if([string]$Q.branch -cne $ExpectedBranch){throw "BRANCH_MISMATCH actual=$($Q.branch)"}

$Tree=(& git -C $Cache rev-parse ($ExpectedSha+'^{tree}')).Trim()
if($LASTEXITCODE-ne0){throw 'TREE_READ_FAILED'}
$Remote='https://github.com/'+$Repo+'.git'
$Pair="x-access-token:$env:GITHUB_TOKEN"
$Basic=[Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($Pair))
$Header="AUTHORIZATION: basic $Basic"

$Before=@(& git -c "http.https://github.com/.extraheader=$Header" ls-remote --heads $Remote ("refs/heads/"+$ExpectedBranch))
if($LASTEXITCODE-ne0){throw 'REMOTE_READ_FAILED'}
if($Before.Count-gt0){
  $Existing=(([string]$Before[0]) -split '\s+')[0]
  if($Existing -cne $ExpectedSha){throw "REMOTE_BRANCH_CONFLICT expected=$ExpectedSha actual=$Existing"}
  Write-Host "already_preserved=true"
}else{
  & git -c "http.https://github.com/.extraheader=$Header" -C $Cache push $Remote ($ExpectedSha+":refs/heads/"+$ExpectedBranch)
  if($LASTEXITCODE-ne0){throw "PUSH_FAILED branch=$ExpectedBranch"}
}

$After=@(& git -c "http.https://github.com/.extraheader=$Header" ls-remote --heads $Remote ("refs/heads/"+$ExpectedBranch))
if($LASTEXITCODE-ne0 -or $After.Count-ne1){throw 'REMOTE_VERIFY_FAILED'}
$Actual=(([string]$After[0]) -split '\s+')[0]
if($Actual -cne $ExpectedSha){throw "REMOTE_VERIFY_SHA_MISMATCH expected=$ExpectedSha actual=$Actual"}

Write-Host 'YGGDRASIL_CUTOVER_PRESERVE=PASS'
Write-Host "experiment=$ExpectedExperiment"
Write-Host "branch=$ExpectedBranch"
Write-Host "sha=$ExpectedSha"
Write-Host "tree=$Tree"
