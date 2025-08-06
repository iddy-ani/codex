@echo off
setlocal EnableDelayedExpansion
echo ================================================
echo Intel ExpertGPT Codex CLI Installation v1.1.0
echo ================================================
echo.
echo Checking system requirements and dependencies...
echo.

REM Check if running as Administrator
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: This script must be run as Administrator.
    echo.
    echo To run as Administrator:
    echo   1. Right-click on this file
    echo   2. Select "Run as administrator"
    echo   3. Click "Yes" when prompted by Windows
    echo.
    pause
    exit /b 1
)

echo [✓] Running with Administrator privileges
echo.

REM Check Windows version (WSL2 requires Windows 10 build 19041 or Windows 11)
echo [1/4] Checking Windows version...
for /f "tokens=3" %%i in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild ^| find "CurrentBuild"') do set BUILD=%%i
if !BUILD! LSS 19041 (
    echo WARNING: Windows build !BUILD! detected.
    echo WSL2 requires Windows 10 build 19041 or newer, or Windows 11.
    echo Some features may not work properly on older Windows versions.
    echo.
) else (
    echo   ✓ Windows build !BUILD! supports WSL2
)

REM Check Node.js installation
echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ ERROR: Node.js is not installed or not in PATH.
    echo.
    echo Intel ExpertGPT Codex CLI requires Node.js version 22 or newer.
    echo.
    echo TO INSTALL NODE.JS:
    echo   1. Visit: https://nodejs.org/en/download/
    echo   2. Download "Windows Installer (.msi)" for your system
    echo   3. Run the installer with default settings
    echo   4. Restart your computer
    echo   5. Run this installation script again
    echo.
    echo QUICK INSTALL (if you have winget^):
    echo   winget install OpenJS.NodeJS
    echo.
    pause
    exit /b 1
)

REM Check Node.js version
for /f "tokens=1 delims=." %%a in ('node --version 2^>nul') do (
    set NODE_VERSION=%%a
    set NODE_MAJOR=%%a
    set NODE_MAJOR=!NODE_MAJOR:v=!
)

if !NODE_MAJOR! LSS 22 (
    echo ❌ ERROR: Node.js version !NODE_MAJOR! is too old.
    echo.
    echo Required: Node.js 22 or newer
    echo Current:  !NODE_VERSION!
    echo.
    echo TO UPDATE NODE.JS:
    echo   1. Visit: https://nodejs.org/en/download/
    echo   2. Download the latest LTS version
    echo   3. Install over your existing version
    echo.
    pause
    exit /b 1
)

echo   ✓ Node.js !NODE_VERSION! is compatible

REM Check npm
npm --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ ERROR: npm is not available.
    echo npm should be installed automatically with Node.js.
    echo Please reinstall Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

for /f %%i in ('npm --version 2^>nul') do set NPM_VERSION=%%i
echo   ✓ npm !NPM_VERSION! is available

REM Check WSL2
echo [3/4] Checking WSL2 (Windows Subsystem for Linux^)...
wsl --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️  WARNING: WSL2 is not installed or not properly configured.
    echo.
    echo Intel ExpertGPT Codex CLI uses WSL2 for executing Linux commands
    echo and shell operations. Without WSL2, some features may not work.
    echo.
    echo TO INSTALL WSL2:
    echo   1. Open PowerShell as Administrator
    echo   2. Run: wsl --install
    echo   3. Restart your computer when prompted
    echo   4. Complete Ubuntu setup when it opens
    echo.
    echo ALTERNATIVE METHOD:
    echo   1. Visit: https://learn.microsoft.com/en-us/windows/wsl/install
    echo   2. Follow the manual installation guide
    echo.
    echo.
    set /p CONTINUE_WITHOUT_WSL="Continue installation without WSL2? (y/n): "
    if /i "!CONTINUE_WITHOUT_WSL!" neq "y" (
        echo.
        echo Installation cancelled. Please install WSL2 first for full functionality.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Continuing installation without WSL2...
    echo Note: Some advanced features may not work properly.
) else (
    wsl --status >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ WSL2 is installed and running
    ) else (
        echo   ⚠️  WSL2 is installed but may need configuration
        echo   You can set it up later if needed
    )
)

REM Check for existing installation
echo [4/4] Checking for existing installation...
npm list -g @intel/codex-cli >nul 2>&1
if !errorlevel! equ 0 (
    echo   ⚠️  Existing installation detected
    echo   Uninstalling previous version...
    npm uninstall -g @intel/codex-cli >nul 2>&1
    echo   ✓ Previous version removed
) else (
    echo   ✓ No existing installation found
)

echo.
echo ================================================
echo Installing Intel ExpertGPT Codex CLI...
echo ================================================
echo.

echo Installing package globally...
npm install -g . --silent

if !errorlevel! neq 0 (
    echo.
    echo ❌ ERROR: Installation failed!
    echo.
    echo TROUBLESHOOTING STEPS:
    echo   1. Ensure you're running as Administrator
    echo   2. Check your internet connection
    echo   3. Clear npm cache: npm cache clean --force
    echo   4. Try installing again
    echo.
    echo If problems persist, contact your IT support team.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✅ Installation completed successfully!
echo ================================================
echo.
echo Intel ExpertGPT Codex CLI v1.1.0 is now installed globally.
echo.
echo 🚀 GETTING STARTED:
echo   1. Open a new Command Prompt or PowerShell window
echo   2. Navigate to your project: cd "C:\path\to\your\project"
echo   3. Start coding with AI: codex "explain this codebase"
echo.
echo 📖 COMMON COMMANDS:
echo   codex                           # Interactive mode
echo   codex "fix build errors"        # Direct command
echo   codex --help                    # Show all options
echo.
echo 🔧 FEATURES INCLUDED:
echo   ✓ Pre-configured Azure OpenAI access (no API key needed)
echo   ✓ Automatic updates from Intel network share
echo   ✓ User activity tracking and analytics
echo   ✓ Sandboxed code execution for safety
echo.
echo 📚 DOCUMENTATION:
echo   • User Guide: INTEL-CODEX-USER-GUIDE.md
echo   • Installation Help: INSTALL-WINDOWS.md
echo   • Update System: UPDATE-SYSTEM-ADMIN-GUIDE.md
echo.
echo Happy coding with ExpertGPT! 🎉
echo.
pause
