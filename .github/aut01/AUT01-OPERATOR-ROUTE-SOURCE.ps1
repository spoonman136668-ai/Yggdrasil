$ErrorActionPreference='Stop'
Set-StrictMode -Version 2.0
$Plane='C:\Users\camar\GolandProjects\ckb-plane'
function ShowRange([string]$Path,[int]$Start,[int]$End){$i=0;Get-Content -LiteralPath $Path|ForEach-Object{$i++;if($i -ge $Start -and $i -le $End){Write-Host ('{0,4}: {1}' -f $i,$_ )}}}
Write-Host '=== server.go 80-230 ==='
ShowRange (Join-Path $Plane 'internal\plane\server.go') 80 230
Write-Host '=== autonomy_controls.go 250-360 ==='
ShowRange (Join-Path $Plane 'internal\plane\autonomy_controls.go') 250 360
Write-Host '=== cmd autonomy.go 140-220 ==='
ShowRange (Join-Path $Plane 'cmd\ckb-plane\autonomy.go') 140 220
Write-Host 'result=AUT01_OPERATOR_ROUTE_SOURCE_COMPLETE'
