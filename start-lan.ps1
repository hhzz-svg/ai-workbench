$ErrorActionPreference = "Stop"

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike "169.254.*" -and $_.IPAddress -ne "127.0.0.1" } |
  Select-Object -First 1 -ExpandProperty IPAddress)

Write-Host "Starting API on http://127.0.0.1:8000"
Start-Process powershell -WindowStyle Hidden -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$PSScriptRoot'; python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
)

Write-Host "Starting LAN UI on http://0.0.0.0:5173"
npm --prefix "$PSScriptRoot\frontend" install
npm --prefix "$PSScriptRoot\frontend" run dev -- --host 0.0.0.0

if ($ip) {
  Write-Host "Other devices on the same network can open: http://$ip:5173"
}
