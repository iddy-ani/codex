# Intel Codex CLI Installation Script
# PowerShell version

Write-Host "================================" -ForegroundColor Green
Write-Host "Intel Codex CLI Installation" -ForegroundColor Green  
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Yellow
} catch {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 22+ from: https://nodejs.org/" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js version
$major = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
if ($major -lt 22) {
    Write-Host "ERROR: Node.js version 22 or higher is required" -ForegroundColor Red
    Write-Host "Current version: $nodeVersion" -ForegroundColor Red
    Write-Host "Please upgrade Node.js from: https://nodejs.org/" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Node.js version is compatible." -ForegroundColor Green
Write-Host ""

# Install the CLI globally
Write-Host "Installing Intel Codex CLI globally..." -ForegroundColor Yellow
Write-Host "Running: npm install -g ." -ForegroundColor Gray
Write-Host ""

try {
    npm install -g .
    if ($LASTEXITCODE -ne 0) {
        throw "Installation failed"
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Installation failed" -ForegroundColor Red
    Write-Host "Please try running as Administrator or check your npm configuration" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use 'codex' from any directory in your terminal." -ForegroundColor Yellow
Write-Host ""
Write-Host "Quick start:" -ForegroundColor Cyan
Write-Host "  1. Open a new Command Prompt or PowerShell window" -ForegroundColor White
Write-Host "  2. Navigate to your project directory: cd `"C:\path\to\your\project`"" -ForegroundColor White  
Write-Host "  3. Run: codex `"explain this codebase`"" -ForegroundColor White
Write-Host ""
Write-Host "Examples:" -ForegroundColor Cyan
Write-Host "  codex `"help me fix this bug`"" -ForegroundColor White
Write-Host "  codex `"add error handling to this function`"" -ForegroundColor White
Write-Host "  codex `"write unit tests for this module`"" -ForegroundColor White
Write-Host ""
Write-Host "The CLI uses Intel's internal Azure OpenAI service automatically." -ForegroundColor Yellow
Write-Host "No additional API key configuration required." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
