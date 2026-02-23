# Unreal Engine compile_commands.json generator for clangd LSP
# Session start hook script

param(
    [string]$WorkingDir = (Get-Location).Path
)

# Check if compile_commands.json already exists
$compileCommandsPath = Join-Path $WorkingDir "compile_commands.json"
if (Test-Path $compileCommandsPath) {
    Write-Host "compile_commands.json already exists"
    exit 0
}

# Find .uproject file
$uprojectFile = Get-ChildItem -Path $WorkingDir -Filter "*.uproject" -Depth 1 -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $uprojectFile) {
    # Not an Unreal project
    exit 0
}

Write-Host "Found Unreal project: $($uprojectFile.FullName)"

# Run Python generator script
$scriptPath = Join-Path $env:USERPROFILE ".claude\scripts\generate-compile-commands.py"

if (Test-Path $scriptPath) {
    Write-Host "Generating compile_commands.json..."
    python $scriptPath $WorkingDir
} else {
    Write-Host "Python generator script not found: $scriptPath"
    exit 1
}

exit 0
