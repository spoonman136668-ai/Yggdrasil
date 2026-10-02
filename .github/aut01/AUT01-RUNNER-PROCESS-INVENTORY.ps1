$ErrorActionPreference='Continue'
Set-StrictMode -Version 2.0
Write-Host "probe_runner=$env:RUNNER_NAME"
$ps=@(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @('Runner.Listener.exe','Runner.Worker.exe') })
foreach($p in $ps){
  Write-Host "name=$($p.Name) pid=$($p.ProcessId) ppid=$($p.ParentProcessId) session=$($p.SessionId) path=$($p.ExecutablePath)"
  try{$o=Invoke-CimMethod -InputObject $p -MethodName GetOwner -ErrorAction Stop;Write-Host "owner_rc=$($o.ReturnValue) owner=$($o.Domain)\$($o.User)"}catch{Write-Host "owner=UNREADABLE"}
}
Write-Host 'result=AUT01_RUNNER_PROCESS_INVENTORY_COMPLETE'
