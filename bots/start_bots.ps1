# ========================================
# Discord Bot Startup Script
# ========================================
# Run this script to start ALL bots and verify they're online
# Usage: Right-click → Run with PowerShell
# ========================================

$Host.UI.RawUI.WindowTitle = "Apptivators Academy - Bot Launcher"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  APPTIVATORS ACADEMY - BOT LAUNCHER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set the bot directory
$BotDir = "C:\Users\Gam3rGoon\Documents\GitHub\Discord-Build-Plan-Apptivators-Coding-Academy\Apptivators-Coding-Academy"

# Change to bot directory
Set-Location $BotDir

Write-Host "[INFO] Bot Directory: $BotDir" -ForegroundColor Gray
Write-Host ""

# Check Python is installed
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Host "[ERROR] Python not found. Install Python 3.10+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Python found: $($PythonCmd.Source)" -ForegroundColor Green
Write-Host ""

# Bots to start
$Bots = @(
    @{Name="StrikeSource_Clawbot"; Script="StrikeSource_Clawbot.py"; Dir="."},
    @{Name="S.A.M.P.I.RT"; Script="sampi_rt_bot.py"; Dir="S.A.M.P.I.RT"},
    @{Name="SonicForge"; Script="sonic_forge_bot.py"; Dir="SonicForge"},
    @{Name="SyncFlux"; Script="sync_flux_bot.py"; Dir="SyncFlux"}
)

# Stop any existing Python processes for bots
Write-Host "[INFO] Stopping existing bot processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start bots
Write-Host ""
Write-Host "[STARTING] Launching all bots..." -ForegroundColor Cyan
Write-Host ""

$Processes = @()

foreach ($Bot in $Bots) {
    $BotPath = Join-Path $BotDir $Bot.Dir
    $BotFile = Join-Path $BotPath $Bot.Script
    
    Write-Host "  Starting: $($Bot.Name)" -NoNewline
    
    if (Test-Path $BotFile) {
        $Proc = Start-Process -FilePath "python" -ArgumentList $Bot.Script -WorkingDirectory $BotPath -WindowStyle Hidden -PassThru
        $Processes += $Proc
        Write-Host " [OK] PID: $($Proc.Id)" -ForegroundColor Green
    } else {
        Write-Host " [ERROR] File not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  $($Processes.Count) BOTS STARTED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Sanity Check - Wait for bots to connect
Write-Host "[SANITY CHECK] Verifying bot connections..." -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 5

# Run sanity check
Write-Host "Running sanity_check.py..." -ForegroundColor Gray
python "$BotDir\sanity_check.py"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ALL TASKS COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Bots are now ONLINE in Discord!" -ForegroundColor Green
Write-Host "Close this window to stop bots (they will go offline)" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit (bots will remain running)"