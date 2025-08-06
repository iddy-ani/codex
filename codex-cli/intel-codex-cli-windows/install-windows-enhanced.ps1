# Intel ExpertGPT Codex CLI Installation Script (Enhanced)
# Checks for all dependencies and provides installation guidance

param(
    [switch]$Force = $false
)

Write-Host "================================================" -ForegroundColor Green
Write-Host "Intel ExpertGPT Codex CLI Installation v1.1.0" -ForegroundColor Green  
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Checking system requirements and dependencies..." -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must be run as Administrator." -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Yellow
    Write-Host "  1. Right-click on PowerShell" -ForegroundColor White
    Write-Host "  2. Select 'Run as administrator'" -ForegroundColor White
    Write-Host "  3. Navigate to this directory and run the script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[✓] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Check Windows version for WSL2 compatibility
Write-Host "[1/4] Checking Windows version..." -ForegroundColor Cyan
$build = [System.Environment]::OSVersion.Version.Build
if ($build -lt 19041) {
    Write-Host "⚠️  WARNING: Windows build $build detected." -ForegroundColor Yellow
    Write-Host "WSL2 requires Windows 10 build 19041+ or Windows 11." -ForegroundColor Yellow
    Write-Host "Some features may not work properly." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "  ✓ Windows build $build supports WSL2" -ForegroundColor Green
}

# Check Node.js
Write-Host "[2/4] Checking Node.js installation..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    
    # Parse major version
    $majorVersion = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
    
    if ($majorVersion -lt 22) {
        Write-Host "❌ ERROR: Node.js version $majorVersion is too old." -ForegroundColor Red
        Write-Host ""
        Write-Host "Required: Node.js 22 or newer" -ForegroundColor Yellow
        Write-Host "Current:  $nodeVersion" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "TO UPDATE NODE.JS:" -ForegroundColor Yellow
        Write-Host "  Option 1 - Download installer:" -ForegroundColor White
        Write-Host "    https://nodejs.org/en/download/" -ForegroundColor White
        Write-Host ""
        Write-Host "  Option 2 - Use winget (if available):" -ForegroundColor White
        Write-Host "    winget install OpenJS.NodeJS" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "  ✓ Node.js $nodeVersion is compatible" -ForegroundColor Green
    
} catch {
    Write-Host "❌ ERROR: Node.js is not installed or not in PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Intel ExpertGPT Codex CLI requires Node.js version 22 or newer." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "TO INSTALL NODE.JS:" -ForegroundColor Yellow
    Write-Host "  Option 1 - Download installer:" -ForegroundColor White
    Write-Host "    1. Visit: https://nodejs.org/en/download/" -ForegroundColor White
    Write-Host "    2. Download 'Windows Installer (.msi)' for your system" -ForegroundColor White
    Write-Host "    3. Run installer with default settings" -ForegroundColor White
    Write-Host "    4. Restart PowerShell and run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "  Option 2 - Use winget (Windows Package Manager):" -ForegroundColor White
    Write-Host "    winget install OpenJS.NodeJS" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "npm not found"
    }
    Write-Host "  ✓ npm $npmVersion is available" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: npm is not available." -ForegroundColor Red
    Write-Host "npm should be installed automatically with Node.js." -ForegroundColor Yellow
    Write-Host "Please reinstall Node.js from: https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check WSL2
Write-Host "[3/4] Checking WSL2 (Windows Subsystem for Linux)..." -ForegroundColor Cyan
try {
    $wslVersion = wsl --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "WSL not found"
    }
    
    # Check if WSL is actually working
    try {
        $wslStatus = wsl --status 2>$null
        Write-Host "  ✓ WSL2 is installed and configured" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️  WSL2 is installed but may need setup" -ForegroundColor Yellow
        Write-Host "  You can configure it later if needed" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "⚠️  WARNING: WSL2 is not installed or configured." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Intel ExpertGPT Codex CLI uses WSL2 for executing Linux commands" -ForegroundColor Yellow
    Write-Host "and shell operations. Without WSL2, some features may not work." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "TO INSTALL WSL2:" -ForegroundColor Yellow
    Write-Host "  Method 1 - Automatic (Recommended):" -ForegroundColor White
    Write-Host "    1. Open PowerShell as Administrator" -ForegroundColor White
    Write-Host "    2. Run: wsl --install" -ForegroundColor White
    Write-Host "    3. Restart computer when prompted" -ForegroundColor White
    Write-Host "    4. Complete Ubuntu setup when it opens" -ForegroundColor White
    Write-Host ""
    Write-Host "  Method 2 - Manual:" -ForegroundColor White
    Write-Host "    Visit: https://learn.microsoft.com/en-us/windows/wsl/install" -ForegroundColor White
    Write-Host ""
    
    if (-not $Force) {
        $continue = Read-Host "Continue installation without WSL2? (y/n)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            Write-Host ""
            Write-Host "Installation cancelled. Install WSL2 for full functionality." -ForegroundColor Yellow
            Write-Host ""
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    
    Write-Host ""
    Write-Host "Continuing without WSL2... Some features may be limited." -ForegroundColor Yellow
}

# Check for existing installation
Write-Host "[4/4] Checking for existing installation..." -ForegroundColor Cyan
try {
    $existing = npm list -g @intel/codex-cli 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ⚠️  Existing installation detected" -ForegroundColor Yellow
        Write-Host "  Removing previous version..." -ForegroundColor Yellow
        npm uninstall -g @intel/codex-cli *>$null
        Write-Host "  ✓ Previous version removed" -ForegroundColor Green
    } else {
        Write-Host "  ✓ No existing installation found" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✓ No existing installation found" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Installing Intel ExpertGPT Codex CLI..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Installing package globally..." -ForegroundColor Yellow
try {
    # Capture npm install output but suppress most of it
    $installOutput = npm install -g . 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Installation failed"
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Installation failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "TROUBLESHOOTING STEPS:" -ForegroundColor Yellow
    Write-Host "  1. Ensure you're running as Administrator" -ForegroundColor White
    Write-Host "  2. Check your internet connection" -ForegroundColor White
    Write-Host "  3. Clear npm cache: npm cache clean --force" -ForegroundColor White
    Write-Host "  4. Try installing again" -ForegroundColor White
    Write-Host ""
    Write-Host "Error details:" -ForegroundColor Yellow
    Write-Host $installOutput -ForegroundColor Red
    Write-Host ""
    Write-Host "If problems persist, contact your IT support team." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ Installation completed successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Intel ExpertGPT Codex CLI v1.1.0 is now installed globally." -ForegroundColor White
Write-Host ""
Write-Host "🚀 GETTING STARTED:" -ForegroundColor Cyan
Write-Host "  1. Open a new PowerShell or Command Prompt window" -ForegroundColor White
Write-Host "  2. Navigate to your project: " -ForegroundColor White -NoNewline
Write-Host "cd `"C:\path\to\your\project`"" -ForegroundColor Yellow
Write-Host "  3. Start coding with AI: " -ForegroundColor White -NoNewline
Write-Host "codex `"explain this codebase`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 COMMON COMMANDS:" -ForegroundColor Cyan
Write-Host "  codex                           # Interactive mode" -ForegroundColor White
Write-Host "  codex `"fix build errors`"        # Direct command" -ForegroundColor White
Write-Host "  codex --help                    # Show all options" -ForegroundColor White
Write-Host ""
Write-Host "🔧 FEATURES INCLUDED:" -ForegroundColor Cyan
Write-Host "  ✓ Pre-configured Azure OpenAI access (no API key needed)" -ForegroundColor Green
Write-Host "  ✓ Automatic updates from Intel network share" -ForegroundColor Green
Write-Host "  ✓ User activity tracking and analytics" -ForegroundColor Green
Write-Host "  ✓ Sandboxed code execution for safety" -ForegroundColor Green
Write-Host ""
Write-Host "📚 DOCUMENTATION:" -ForegroundColor Cyan
Write-Host "  • User Guide: INTEL-CODEX-USER-GUIDE.md" -ForegroundColor White
Write-Host "  • Installation Help: INSTALL-WINDOWS.md" -ForegroundColor White
Write-Host "  • Update System: UPDATE-SYSTEM-ADMIN-GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding with ExpertGPT! 🎉" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
