Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Url='https://github.com/openai/codex/releases/download/rust-v0.154.0/codex-code-mode-host-x86_64-pc-windows-msvc.exe'
$Expected='7b4987007702973dfeb49ec9a0c11f737488890e208ccb04f7a147769c4bb1f1'
$Targets=@(
  'C:\ProgramData\CKBR\codex\bin\codex.exe',
  'C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\bin\codex.exe'
)
$Tmp=Join-Path $env:RUNNER_TEMP 'codex-code-mode-host-0.154.0-x64.exe'
Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Tmp
$Hash=(Get-FileHash -LiteralPath $Tmp -Algorithm SHA256).Hash.ToLowerInvariant()
if($Hash-cne$Expected){throw "HOST_SHA256_MISMATCH expected=$Expected actual=$Hash"}
$Sig=Get-AuthenticodeSignature -LiteralPath $Tmp
Write-Host "HOST_SIGNATURE status=$($Sig.Status) subject=$($Sig.SignerCertificate.Subject)"
if([string]$Sig.Status-cne'Valid'){throw "HOST_SIGNATURE_INVALID status=$($Sig.Status)"}
foreach($Codex in $Targets){
  if(-not(Test-Path -LiteralPath $Codex -PathType Leaf)){throw "CODEX_MISSING path=$Codex"}
  $Version=((& $Codex --version 2>$null)|ForEach-Object{[string]$_})-join' '
  if($Version-notmatch'0\.154\.0'){throw "CODEX_VERSION_MISMATCH path=$Codex version=$Version"}
  $Target=Join-Path (Split-Path -Parent $Codex) 'codex-code-mode-host.exe'
  if(Test-Path -LiteralPath $Target -PathType Leaf){
    $Existing=(Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant()
    if($Existing-cne$Expected){throw "EXISTING_HOST_DRIFT path=$Target sha=$Existing"}
    Write-Host "HOST_ALREADY_CORRECT path=$Target"
  }else{
    Copy-Item -LiteralPath $Tmp -Destination $Target -Force
    $Actual=(Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant()
    if($Actual-cne$Expected){throw "HOST_COPY_VERIFY_FAILED path=$Target sha=$Actual"}
    Write-Host "HOST_INSTALLED path=$Target sha=$Actual"
  }
}
$Smoke=Join-Path $env:RUNNER_TEMP 'codex-host-smoke-ygg'
if(Test-Path -LiteralPath $Smoke){Remove-Item -LiteralPath $Smoke -Recurse -Force}
New-Item -ItemType Directory -Force -Path $Smoke|Out-Null
[IO.File]::WriteAllText((Join-Path $Smoke 'smoke.txt'),'CODEX_HOST_SMOKE_OK',(New-Object Text.UTF8Encoding($false)))
$Codex='C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\bin\codex.exe'
$CodexHome='C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\home'
$OldCodeHome=$env:CODEX_HOME;$OldHome=$env:HOME;$OldProfile=$env:USERPROFILE
try{
  if(Test-Path -LiteralPath $CodexHome -PathType Container){$env:CODEX_HOME=$CodexHome;$env:HOME=$CodexHome;$env:USERPROFILE=$CodexHome}
  $Prompt=Join-Path $Smoke 'prompt.txt';$Out=Join-Path $Smoke 'out.txt'
  [IO.File]::WriteAllText($Prompt,'Read smoke.txt using your repository/file tools. Reply with exactly CODEX_HOST_SMOKE_OK and make no changes.',(New-Object Text.UTF8Encoding($false)))
  $Proc=Start-Process -FilePath $Codex -ArgumentList @('exec','--approve-for-me','--model','gpt-5.6-luna','--output-last-message',$Out,'-') -WorkingDirectory $Smoke -RedirectStandardInput $Prompt -NoNewWindow -Wait -PassThru
  if($Proc.ExitCode-ne0){throw "CODEX_SMOKE_FAILED exit=$($Proc.ExitCode)"}
  if(-not(Test-Path -LiteralPath $Out)){throw 'CODEX_SMOKE_OUTPUT_MISSING'}
  $Text=[IO.File]::ReadAllText($Out).Trim()
  if($Text-cne'CODEX_HOST_SMOKE_OK'){throw "CODEX_SMOKE_OUTPUT_INVALID output=$Text"}
  Write-Host 'CODEX_CODE_MODE_HOST_SMOKE=PASS'
}finally{$env:CODEX_HOME=$OldCodeHome;$env:HOME=$OldHome;$env:USERPROFILE=$OldProfile}
Write-Host 'CODEX_CODE_MODE_HOST_REPAIR=PASS'
