$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
if (-not $root) {
  $root = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike "169.254.*" -and $_.IPAddress -ne "127.0.0.1" } |
  Select-Object -First 1 -ExpandProperty IPAddress)

Write-Host "Starting API on http://127.0.0.1:8000"
Start-Process powershell -WindowStyle Hidden -ArgumentList @(
  "-NoExit",
  "-Command",
  "Set-Location -LiteralPath '$root'; python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
)

Write-Host "Starting LAN UI on http://0.0.0.0:5173"
Start-Process powershell -WindowStyle Hidden -ArgumentList @(
  "-NoExit",
  "-Command",
  "Set-Location -LiteralPath '$root\frontend'; & npm.cmd run dev -- --host 0.0.0.0"
)

for ($i = 0; $i -lt 30; $i++) {
  try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 2
    if ($resp.StatusCode -eq 200) { break }
  } catch {
    Start-Sleep -Seconds 1
  }
}

if ($ip) {
  Write-Host "Other devices on the same network can open: http://$ip:5173"
}
