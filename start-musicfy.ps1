# Script para iniciar backend y frontend de Musicfy en terminales separadas
# PARA USARLO EN UNA TERMINA EN LA RAIZ DEL REPO ESCRIBE .\start-musicfy.ps1
$ErrorActionPreference = "Stop"

$rootDir = $PSScriptRoot
$backendDir = Join-Path $rootDir "app1-Musicfy\backend"
$frontendDir = Join-Path $rootDir "app1-Musicfy\frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      Iniciando Musicfy en Local        " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Comprobar virtualenv de Python
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[AVISO] No se detectó .venv. Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv (Join-Path $backendDir ".venv")
    & (Join-Path $backendDir ".venv\Scripts\pip.exe") install -r (Join-Path $backendDir "requirements.txt")
}

# Comprobar node_modules
$nodeModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "[AVISO] Instalando paquetes de frontend (npm install)..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
}

# Iniciar Backend
Write-Host "[1/2] Iniciando Backend FastAPI (http://localhost:8000)..." -ForegroundColor Green
$backendCmd = "Set-Location '$backendDir'; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Iniciar Frontend
Write-Host "[2/2] Iniciando Frontend Vite (http://localhost:5173)..." -ForegroundColor Green
$frontendCmd = "Set-Location '$frontendDir'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "`nServicios lanzados:" -ForegroundColor Cyan
Write-Host "- Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "- Swagger:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "- Frontend: http://localhost:5173" -ForegroundColor White

