@echo off
setlocal enabledelayedexpansion

echo ================================
echo Creating Intel ExpertGPT Codex CLI Distribution Package
echo ================================
echo.

:: Check if we're in the right directory
if not exist "package.json" (
    echo ERROR: package.json not found. Please run this from the codex-cli directory.
    pause
    exit /b 1
)

:: Create distribution directory
set DIST_DIR=intel-codex-cli-windows
if exist "%DIST_DIR%" (
    echo Removing existing distribution directory...
    rmdir /s /q "%DIST_DIR%"
)

echo Creating distribution directory...
mkdir "%DIST_DIR%"

:: Build the project
echo.
echo Building the project...
call pnpm build
if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

:: Copy necessary files
echo.
echo Copying files to distribution package...

:: Core files
copy package.json "%DIST_DIR%\"
copy pnpm-lock.yaml "%DIST_DIR%\"
if exist yarn.lock copy yarn.lock "%DIST_DIR%\"

:: Installation scripts
copy install-windows.bat "%DIST_DIR%\"
copy install-windows.ps1 "%DIST_DIR%\"
copy install-windows-enhanced.bat "%DIST_DIR%\"
copy install-windows-enhanced.ps1 "%DIST_DIR%\"
copy uninstall-windows.bat "%DIST_DIR%\"
copy uninstall-windows.ps1 "%DIST_DIR%\"

:: Documentation
copy INSTALL-WINDOWS.md "%DIST_DIR%\"
copy INTEL-CODEX-USER-GUIDE.md "%DIST_DIR%\"
copy UPDATE-SYSTEM-ADMIN-GUIDE.md "%DIST_DIR%\"
copy sample-update-info.json "%DIST_DIR%\"
if exist README.md copy README.md "%DIST_DIR%\README-ORIGINAL.md"

:: Built application
xcopy /E /I bin "%DIST_DIR%\bin"
if exist dist xcopy /E /I dist "%DIST_DIR%\dist"

:: Node modules (production only)
echo.
echo Installing production dependencies...
pushd "%DIST_DIR%"
call npm install --production --no-optional
if %ERRORLEVEL% neq 0 (
    echo WARNING: npm install had issues, but continuing...
)
popd

:: Create a simple start script
echo @echo off > "%DIST_DIR%\QUICK-INSTALL.bat"
echo echo ================================ >> "%DIST_DIR%\QUICK-INSTALL.bat"
echo echo Intel ExpertGPT Codex CLI Quick Install >> "%DIST_DIR%\QUICK-INSTALL.bat"
echo echo ================================ >> "%DIST_DIR%\QUICK-INSTALL.bat"
echo echo. >> "%DIST_DIR%\QUICK-INSTALL.bat"
echo echo This will install the Intel ExpertGPT Codex CLI globally on your system. >> "%DIST_DIR%\QUICK-INSTALL.bat"
echo echo. >> "%DIST_DIR%\QUICK-INSTALL.bat"
echo pause >> "%DIST_DIR%\QUICK-INSTALL.bat"
echo call install-windows.bat >> "%DIST_DIR%\QUICK-INSTALL.bat"

echo.
echo ================================
echo Distribution package created successfully!
echo ================================
echo.
echo Package location: %DIST_DIR%\
echo.
echo To distribute:
echo   1. Zip the '%DIST_DIR%' folder
echo   2. Send to Intel engineers
echo   3. They extract and run QUICK-INSTALL.bat
echo.
echo The package contains:
echo   - Built CLI application
echo   - Installation scripts (bat and ps1)
echo   - Uninstallation scripts
echo   - Complete installation guide
echo   - Comprehensive user guide
echo   - All required dependencies
echo.
pause
