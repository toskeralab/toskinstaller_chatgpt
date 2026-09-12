[CmdletBinding()]
param(
    [switch]$SkipInstall,
    [switch]$SkipPackageBuild,
    [string]$Python = "python",
    [string]$PythonArguments = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Step([string]$Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Get-PythonCommand() {
    $arguments = @()
    if (-not [string]::IsNullOrWhiteSpace($PythonArguments)) {
        $arguments = $PythonArguments -split '\s+'
    }
    return @($Python) + $arguments
}

function Require-PythonCommand() {
    $command = Get-PythonCommand
    $cmd = Get-Command $command[0] -ErrorAction SilentlyContinue
    if (-not $cmd) { throw "Comando não encontrado: $($command[0])" }
    Write-Host "PASS: $($command -join ' ') -> $($cmd.Source)" -ForegroundColor Green
}

function Invoke-Python([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments) {
    $command = Get-PythonCommand
    if ($command.Count -gt 1) {
        & $command[0] @($command[1..($command.Count - 1)]) @Arguments
    } else {
        & $command[0] @Arguments
    }
}

if ($env:OS -ne "Windows_NT") {
    throw "Este script deve ser executado no Windows."
}

Step "1. Verificando Windows e Python"
Write-Host "Windows: OK"
Require-PythonCommand
$versionText = Invoke-Python --version 2>&1
Write-Host $versionText
$version = [version](($versionText -replace '^Python\s+', '').Trim())
if ($version.Major -ne 3 -or $version.Minor -lt 12 -or $version.Minor -ge 15) {
    throw "Python 3.12, 3.13 ou 3.14 é necessário. Versão detectada: $version"
}

Step "2. Verificando ambiente Python"
Invoke-Python -m pip --version

if (-not $SkipInstall) {
    Step "3. Instalando TOSKINSTALLER em modo editável"
    Invoke-Python -m pip install --upgrade pip
    Invoke-Python -m pip install -e ".[test,build]"
}

Step "4. Testes automatizados"
Invoke-Python -m pytest -q

Step "5. Smoke test de importação"
Invoke-Python -c "import toskinstaller; print('PASS: import toskinstaller; versão=' + toskinstaller.__version__)"

if (-not $SkipPackageBuild) {
    Step "6. Verificando PyInstaller"
    Invoke-Python -m PyInstaller --version

    Step "7. Gerando TOSKINSTALLER.exe"
    Invoke-Python -m PyInstaller --noconfirm --clean --onefile --name TOSKINSTALLER scripts/build_entry.py

    $exe = Join-Path (Get-Location) "dist\TOSKINSTALLER.exe"
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
        throw "Build terminou sem gerar: $exe"
    }
    $size = (Get-Item -LiteralPath $exe).Length
    if ($size -lt 100KB) {
        throw "TOSKINSTALLER.exe parece pequeno demais ($size bytes)."
    }
    Write-Host "PASS: $exe ($size bytes)" -ForegroundColor Green
}

Step "RESULTADO"
Write-Host "PASS: validação local concluída." -ForegroundColor Green
Write-Host "Observação: este script ainda não automatiza a interface gráfica nem EXE/MSI/portable final; essa etapa virá depois dos testes locais básicos."
