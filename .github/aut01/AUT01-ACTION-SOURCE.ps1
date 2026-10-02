$ErrorActionPreference='Stop'
Set-StrictMode -Version 2.0
$Plane='C:\Users\camar\GolandProjects\ckb-plane'
$Files=Get-ChildItem -LiteralPath (Join-Path $Plane 'internal\plane') -File -Filter '*.go'
$Hits=@($Files|Select-String -Pattern '^func \(p \*Engine\) Action\(' -CaseSensitive:$false)
foreach($h in $Hits){$path=$h.Path;$start=[Math]::Max(1,$h.LineNumber-10);$end=$h.LineNumber+180;$i=0;Get-Content -LiteralPath $path|ForEach-Object{$i++;if($i -ge $start -and $i -le $end){Write-Host ('{0,4}: {1}' -f $i,$_ )}}}
Write-Host 'result=AUT01_ACTION_SOURCE_COMPLETE'
