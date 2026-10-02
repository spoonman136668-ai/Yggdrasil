$ErrorActionPreference='Stop'
Set-StrictMode -Version 2.0
$Plane='C:\Users\camar\GolandProjects\ckb-plane'
Write-Host "runner=$env:RUNNER_NAME identity=$([Security.Principal.WindowsIdentity]::GetCurrent().Name)"
$Roots=@((Join-Path $Plane 'cmd'),(Join-Path $Plane 'internal\plane'))
$Files=@();foreach($r in $Roots){if(Test-Path -LiteralPath $r){$Files+=Get-ChildItem -LiteralPath $r -Recurse -File -Filter '*.go'}}
$Regex='api/native|run-pending|workorders|HandleFunc|ServeMux|/v1/|/api/|RunLocalOperation|ExternalOrchestrator|controller stop|controller run'
$Hits=@($Files|Select-String -Pattern $Regex -CaseSensitive:$false -ErrorAction SilentlyContinue)
foreach($h in $Hits|Select-Object -First 400){Write-Host "$($h.Path):$($h.LineNumber):$($h.Line.Trim())"}
Write-Host "hit_count=$($Hits.Count)"
Write-Host 'result=AUT01_CONTROLLER_TARGETED_API_DISCOVERY_COMPLETE'
