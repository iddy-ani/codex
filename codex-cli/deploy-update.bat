@echo off
setlocal enabledelayedexpansion

echo ================================
echo Intel Codex CLI Update Deployment
echo ================================
echo.

:: Check if we're in the right directory
if not exist "package.json" (
    echo ERROR: package.json not found. Please run this from the codex-cli directory.
    pause
    exit /b 1
)

:: Get version from package.json
for /f "tokens=2 delims=:" %%a in ('findstr "version" package.json') do (
    set VERSION_LINE=%%a
)
:: Clean up the version string (remove quotes, spaces, commas)
set VERSION=!VERSION_LINE:"=!
set VERSION=!VERSION:,=!
set VERSION=!VERSION: =!
echo Current version: !VERSION!

:: Network share path
set NETWORK_SHARE=\\IREGPT1\Codex
echo Network share: %NETWORK_SHARE%

:: Check network share access
echo.
echo Checking network share access...
if not exist "%NETWORK_SHARE%" (
    echo ERROR: Cannot access network share %NETWORK_SHARE%
    echo Please ensure:
    echo   1. You have network connectivity
    echo   2. You have read/write access to the share
    echo   3. The share exists and is mounted
    pause
    exit /b 1
)
echo ✓ Network share is accessible

:: Create distribution package
echo.
echo Creating distribution package...
call create-distribution.bat
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create distribution package
    pause
    exit /b 1
)

:: Check if distribution was created
if not exist "intel-codex-cli-windows" (
    echo ERROR: Distribution directory not found
    pause
    exit /b 1
)

:: Create zip file
echo.
echo Creating zip package...
set ZIP_FILE=intel-codex-cli-windows-v!VERSION!.zip
powershell -Command "Compress-Archive -Path 'intel-codex-cli-windows' -DestinationPath '!ZIP_FILE!' -Force"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create zip file
    pause
    exit /b 1
)
echo ✓ Created !ZIP_FILE!

:: Copy to network share
echo.
echo Deploying to network share...

:: Copy the zip file
copy "!ZIP_FILE!" "%NETWORK_SHARE%\intel-codex-cli-windows.zip"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to copy zip file to network share
    pause
    exit /b 1
)
echo ✓ Copied zip file to network share

:: Create update info
echo.
echo Creating update info file...
echo { > update-info.json
echo   "version": "!VERSION!", >> update-info.json
echo   "releaseDate": "%DATE%", >> update-info.json
echo   "downloadUrl": "\\\\IREGPT1\\Codex\\intel-codex-cli-windows.zip", >> update-info.json
echo   "changelog": [ >> update-info.json
echo     "Updated to version !VERSION!", >> update-info.json
echo     "See DISTRIBUTION-SUMMARY.md for detailed changes" >> update-info.json
echo   ], >> update-info.json
echo   "required": false >> update-info.json
echo } >> update-info.json

:: Copy update info to network share
copy "update-info.json" "%NETWORK_SHARE%\update-info.json"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to copy update info to network share
    pause
    exit /b 1
)
echo ✓ Copied update info to network share

:: Clean up local files
echo.
echo Cleaning up...
del "!ZIP_FILE!"
del "update-info.json"
rmdir /s /q "intel-codex-cli-windows"

echo.
echo ================================
echo Deployment completed successfully!
echo ================================
echo.
echo Deployed files:
echo   - %NETWORK_SHARE%\intel-codex-cli-windows.zip
echo   - %NETWORK_SHARE%\update-info.json
echo.
echo Version deployed: !VERSION!
echo.
echo Users will be prompted to update when they next run Codex CLI.
echo To make an update required, edit update-info.json and set "required": true
echo.
pause
