param(
    [string]$InstallDirectory = (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Baloide\ClinicalRedactor'),
    [string]$DesktopDirectory = ([Environment]::GetFolderPath('Desktop'))
)
$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$executable = Join-Path $packageRoot 'Velide.exe'
if (-not (Test-Path -LiteralPath $executable)) { throw 'Extract the entire ZIP before running Install.cmd.' }
$installRoot = $InstallDirectory
New-Item -ItemType Directory -Path $installRoot -Force | Out-Null
Get-ChildItem -LiteralPath $packageRoot | Where-Object { $_.Name -notin @('Install.cmd', 'Install.ps1') } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $installRoot -Recurse -Force
}
$desktopPath = $DesktopDirectory
New-Item -ItemType Directory -Path $desktopPath -Force | Out-Null
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut((Join-Path $desktopPath 'Velide.lnk'))
$link.TargetPath = Join-Path $installRoot 'Velide.exe'
$link.WorkingDirectory = $installRoot
$link.IconLocation = (Join-Path $installRoot 'velide.ico') + ',0'
$link.Description = 'Velide by Baloide - local document privacy'
$link.Save()
Write-Host 'Installed. Open Velide from your desktop.' -ForegroundColor Cyan
Write-Host "Installation folder: $installRoot"
