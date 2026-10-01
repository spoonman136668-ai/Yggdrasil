Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Codex='C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\bin\codex.exe'
$Host='C:\ProgramData\CKBR\research-sidecar-yggdrasil\codex\bin\codex-code-mode-host.exe'
$Expected='7b4987007702973dfeb49ec9a0c11f737488890e208ccb04f7a147769c4bb1f1'
foreach($P in @($Codex,$Host)){if(-not(Test-Path -LiteralPath $P -PathType Leaf)){throw "MISSING path=$P"}}
$Hash=(Get-FileHash -LiteralPath $Host -Algorithm SHA256).Hash.ToLowerInvariant()
if($Hash-cne$Expected){throw "HOST_HASH_MISMATCH expected=$Expected actual=$Hash"}
$Sig=Get-AuthenticodeSignature -LiteralPath $Host
if([string]$Sig.Status-cne'Valid'){throw "HOST_SIGNATURE_INVALID status=$($Sig.Status)"}
Write-Host "HOST_VERIFIED sha256=$Hash signer=$($Sig.SignerCertificate.Subject)"
$Root=Join-Path $env:RUNNER_TEMP 'codex-host-smoke-b'
if(Test-Path -LiteralPath $Root){Remove-Item -LiteralPath $Root -Recurse -Force}
New-Item -ItemType Directory -Force -Path $Root|Out-Null
[IO.File]::WriteAllText((Join-Path $Root 'smoke.txt'),'CODEX_HOST_SMOKE_OK',(New-Object Text.UTF8Encoding($false)))
$PromptPath=Join-Path $Root 'prompt.txt'
$Out=Join-Path $Root 'out.txt'
[IO.File]::WriteAllText($PromptPath,'Use your repository/file tools to read smoke.txt. Reply with exactly CODEX_HOST_SMOKE_OK and make no changes.',(New-Object Text.UTF8Encoding($false)))
$Proc=Start-Process -FilePath $Codex -ArgumentList @('exec','--approve-for-me','--model','gpt-5.6-luna','--output-last-message',$Out,'-') -WorkingDirectory $Root -RedirectStandardInput $PromptPath -NoNewWindow -Wait -PassThru
if($Proc.ExitCode-ne0){throw "CODEX_SMOKE_FAILED exit=$($Proc.ExitCode)"}
if(-not(Test-Path -LiteralPath $Out -PathType Leaf)){throw 'CODEX_SMOKE_OUTPUT_MISSING'}
$Text=[IO.File]::ReadAllText($Out).Trim()
if($Text-cne'CODEX_HOST_SMOKE_OK'){throw "CODEX_SMOKE_OUTPUT_INVALID output=$Text"}
Write-Host 'CODEX_CODE_MODE_HOST_SMOKE=PASS'
