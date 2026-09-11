[CmdletBinding()]
param(
    [switch]$SkipInstall,
    [switch]$SkipPackageBuild,
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Step([string]$Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Require-Command([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) { throw "Comando não encontrado: $Name" }
    Write-Host "PASS: $Name -> $($cmd.Source)" -ForegroundColor Green
}

if ($env:OS -ne "Windows_NT") {
    throw "Este script deve ser executado no Windows."
}

Step "1. Verificando Windows e Python"
Write-Host "Windows: OK"
Require-Command $Python
$versionText = & $Python --version 2>&1
Write-Host $versionText
$version = [version](($versionText -replace '^Python\s+', '').Trim())
if ($version.Major -ne 3 -or $version.Minor -lt 12) {
    throw "Python 3.12+ é necessário. Versão detectada: $version"
}

Step "2. Verificando ambiente Python"
& $Python -m pip --version

if (-not $SkipInstall) {
    Step "3. Instalando TOSKINSTALLER em modo editável"
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -e ".[test,build]"
}

Step "4. Testes automatizados"
& $Python -m pytest -q

Step "5. Smoke test de importação"
& $Python -c "import toskinstaller; print('PASS: import toskinstaller; versão=' + toskinstaller.__version__)"

if (-not $SkipPackageBuild) {
    Step "6. Verificando PyInstaller"
    & $Python -m PyInstaller --version

    Step "7. Gerando TOSKINSTALLER.exe"
    & $Python -m PyInstaller --noconfirm --clean --onefile --name TOSKINSTALLER scripts/build_entry.py

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
