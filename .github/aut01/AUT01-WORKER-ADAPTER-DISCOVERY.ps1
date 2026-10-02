$ErrorActionPreference='Stop'
Set-StrictMode -Version 2.0
$Plane='C:\Users\camar\GolandProjects\ckb-plane'
$Files=Get-ChildItem -LiteralPath (Join-Path $Plane 'internal\plane') -File -Filter '*.go'
$Regex='Preferred|worker.*adapter|adapter.*worker|codex|qwen|nemotron|powershell|exec.Command|Start-Process|Worker struct|type Worker'
$Hits=@($Files|Select-String -Pattern $Regex -CaseSensitive:$false -ErrorAction SilentlyContinue)
foreach($h in $Hits|Select-Object -First 500){Write-Host "$($h.Path):$($h.LineNumber):$($h.Line.Trim())"}
Write-Host "hit_count=$($Hits.Count)"
Write-Host 'result=AUT01_WORKER_ADAPTER_DISCOVERY_COMPLETE'
