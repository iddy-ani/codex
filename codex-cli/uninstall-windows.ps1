# Intel ExpertGPT Codex CLI Uninstallation Script
# PowerShell version

Write-Host "================================" -ForegroundColor Red
Write-Host "Intel ExpertGPT Codex CLI Uninstallation" -ForegroundColor Red
Write-Host "================================" -ForegroundColor Red
Write-Host ""

Write-Host "Removing Intel ExpertGPT Codex CLI..." -ForegroundColor Yellow
Write-Host "Running: npm uninstall -g @intel/codex-cli" -ForegroundColor Gray
Write-Host ""

try {
    npm uninstall -g @intel/codex-cli
    if ($LASTEXITCODE -ne 0) {
        throw "Uninstallation failed"
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Uninstallation failed" -ForegroundColor Red
    Write-Host "Please try running as Administrator or check your npm configuration" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Uninstallation completed successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "The 'codex' command has been removed from your system." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
