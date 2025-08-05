@echo off
echo ================================
echo Intel Codex CLI Installation
echo ================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 22+ from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

REM Check Node.js version (basic check)
echo Checking Node.js version compatibility...
for /f "tokens=1 delims=." %%a in ('node --version') do set "major=%%a"
set "major=%major:v=%"
if %major% lss 22 (
    echo ERROR: Node.js version 22 or higher is required
    echo Current version: 
    node --version
    echo Please upgrade Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Node.js version is compatible.
echo.

REM Install the CLI globally
echo Installing Intel Codex CLI globally...
echo Running: npm install -g .
echo.

npm install -g .

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed
    echo Please try running as Administrator or check your npm configuration
    echo.
    pause
    exit /b 1
)

echo.
echo ================================
echo Installation completed successfully!
echo ================================
echo.
echo You can now use 'codex' from any directory in your terminal.
echo.
echo Quick start:
echo   1. Open a new Command Prompt or PowerShell window
echo   2. Navigate to your project directory: cd "C:\path\to\your\project"
echo   3. Run: codex "explain this codebase"
echo.
echo Examples:
echo   codex "help me fix this bug"
echo   codex "add error handling to this function"
echo   codex "write unit tests for this module"
echo.
echo The CLI uses Intel's internal Azure OpenAI service automatically.
echo No additional API key configuration required.
echo.
pause
