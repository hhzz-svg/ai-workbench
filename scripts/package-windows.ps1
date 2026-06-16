param(
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
if (-not $Version) {
    $packageJson = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $repo "package.json") | ConvertFrom-Json
    $Version = $packageJson.version
}

$releaseRoot = Join-Path $repo "dist\release"
$stage = Join-Path $releaseRoot "ai-workbench-windows-$Version"
$zipPath = Join-Path $releaseRoot "ai-workbench-windows-$Version.zip"

if (Test-Path -LiteralPath $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null

$include = @(
    "backend",
    "frontend",
    "docs",
    "examples",
    "landing-page",
    ".github",
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "package.json",
    "install.bat",
    "start.bat",
    "start.ps1",
    "start-lan.ps1"
)

foreach ($item in $include) {
    $source = Join-Path $repo $item
    if (Test-Path -LiteralPath $source) {
        Copy-Item -LiteralPath $source -Destination $stage -Recurse -Force
    }
}

$remove = @(
    "frontend\node_modules",
    "frontend\dist",
    "backend\__pycache__",
    ".pytest_cache"
)

foreach ($item in $remove) {
    $target = Join-Path $stage $item
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
}

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zipPath -Force
$sizeMb = [math]::Round((Get-Item -LiteralPath $zipPath).Length / 1MB, 2)
Remove-Item -LiteralPath $stage -Recurse -Force
Write-Host "Created $zipPath ($sizeMb MB)"
