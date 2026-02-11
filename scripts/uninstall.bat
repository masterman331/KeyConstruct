
@echo off
setlocal enabledelayedexpansion

:: --- Configuration ---
set "AppName=KeyConstruct"
set "InstallDir=%APPDATA%\%AppName%"

:: --- Uninstallation ---
echo.
echo  Uninstalling %AppName%...
echo  ================================
echo.

:: 1. Remove the installation directory
if exist "%InstallDir%" (
    echo  [+] Deleting installation directory: %InstallDir%
    rd /s /q "%InstallDir%"
    if errorlevel 1 (
        echo  [!] WARNING: Failed to delete directory. You may need to delete it manually.
    ) else (
        echo  [*] Directory deleted successfully.
    )
) else (
    echo  [*] Installation directory not found. Nothing to delete.
)

:: 2. Remove the installation directory from the user's PATH
echo  [+] Removing "%InstallDir%" from system PATH...
set "CurrentPath="
for /f "tokens=2,*" %%a in ('reg query HKCU\Environment /v PATH') do set "CurrentPath=%%b"

if defined CurrentPath (
    :: Replace all occurrences of ";%InstallDir%" with ""
    set "NewPath=!CurrentPath:%InstallDir%=!"
    :: Handle cases where the path might be at the beginning or end or a standalone entry
    set "NewPath=!NewPath:;;=;!"
    set "NewPath=!NewPath:;%InstallDir%=!"
    set "NewPath=!NewPath:%InstallDir%;=!"
    set "NewPath=!NewPath! "
    set "NewPath=!NewPath:; ;=;!"
    set "NewPath=!NewPath:;=;!"

    :: Remove leading/trailing semicolons if they result from the removal
    if "!NewPath:~0,1!"==";" set "NewPath=!NewPath:~1!"
    if "!NewPath:~-1!"==";" set "NewPath=!NewPath:~0,-1!"
    
    :: Remove trailing spaces
    for /f "delims=" %%i in ("!NewPath!") do set "NewPath=%%i"

    if "%CurrentPath%"=="%NewPath%" (
        echo  [*] "%InstallDir%" was not found in PATH.
    ) else (
        setx PATH "%NewPath%" > nul
        if errorlevel 1 (
            echo  [!] WARNING: Failed to update PATH. You may need to remove it manually.
        ) else (
            echo  [*] PATH updated successfully.
            echo  [!] This change will take effect in new terminal sessions.
        )
    )
) else (
    echo  [*] PATH environment variable not found or is empty.
)

echo.
echo  ================================
echo  %AppName% uninstallation complete!
echo  Please restart your terminal sessions to ensure all changes take effect.
echo  ================================
echo.
pause
echo.
endlocal
exit /b
