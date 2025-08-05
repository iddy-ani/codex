@echo off
echo ================================
echo Intel Codex CLI Uninstallation
echo ================================
echo.

echo Removing Intel Codex CLI...
npm uninstall -g @intel/codex-cli

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Uninstallation failed
    echo Please try running as Administrator or check your npm configuration
    echo.
    pause
    exit /b 1
)

echo.
echo ================================
echo Uninstallation completed successfully!
echo ================================
echo.
echo The 'codex' command has been removed from your system.
echo.
pause
