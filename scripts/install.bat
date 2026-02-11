
@echo off
setlocal

:: --- Configuration ---
set "AppName=KeyConstruct"
set "ScriptName=keygen.py"
set "WrapperName=keygen.bat"
:: Install to the user's AppData\Roaming directory for portability and no admin rights needed.
set "InstallDir=%APPDATA%\%AppName%"
set "SourceScriptPath=%~dp0..\src\%ScriptName%"

:: --- Installation ---
echo.
echo  Installing %AppName%...
echo  ================================
echo.

:: 1. Create installation directory
if not exist "%InstallDir%" (
    echo  [+] Creating installation directory: %InstallDir%
    mkdir "%InstallDir%"
    if errorlevel 1 (
        echo  [!] ERROR: Failed to create directory. Aborting.
        goto :eof
    )
) else (
    echo  [*] Installation directory already exists.
)

:: 2. Copy the main Python script and requirements.txt
echo  [+] Copying script and requirements.txt to installation directory...
copy /Y "%SourceScriptPath%" "%InstallDir%" > nul
if errorlevel 1 (
    echo  [!] ERROR: Failed to copy script file. Make sure it exists at %SourceScriptPath%.
    goto :eof
)
copy /Y "%~dp0..\requirements.txt" "%InstallDir%" > nul
if errorlevel 1 (
    echo  [!] ERROR: Failed to copy requirements.txt. Make sure it exists at %~dp0..\requirements.txt.
    goto :eof
)

:: 2.1. Install Python dependencies
echo  [+] Installing Python dependencies from requirements.txt...
python -m pip install -r "%InstallDir%\requirements.txt"
if errorlevel 1 (
    echo  [!] ERROR: Failed to install Python dependencies. Please ensure pip is installed and accessible.
    goto :eof
)

:: 3. Create the batch wrapper to call the Python script
echo  [+] Creating command-line wrapper (%WrapperName%)...
(
    echo @echo off
    echo python "%%~dp0\%ScriptName%" %%*
) > "%InstallDir%\%WrapperName%"

if errorlevel 1 (
    echo  [!] ERROR: Failed to create wrapper file.
    goto :eof
)

:: 4. Add the installation directory to the user's PATH
echo  [+] Checking user PATH environment variable...
set "AlreadyInPath="
for /f "tokens=2,*" %%a in ('reg query HKCU\Environment /v PATH') do (
    echo "%%b" | find /I "%InstallDir%" > nul && set AlreadyInPath=true
)

if defined AlreadyInPath (
    echo  [*] %AppName% is already in your PATH.
) else (
    echo  [+] Adding %InstallDir% to your PATH.
    echo  [!] This will only affect new terminal sessions.
    
    rem Use setx to permanently add the directory to the user's PATH.
    setx PATH "%%PATH%%;%InstallDir%"
    if errorlevel 1 (
        echo  [!] ERROR: Failed to update PATH with setx.
    )
)


:: 5. Ensure Python is in the PATH (if not already found by where.exe)
echo  [+] Ensuring Python is in system PATH...
set "PythonPath1=%APPDATA%\Local\Programs\Python\Python39\Scripts\"
set "PythonPath2=%APPDATA%\Local\Programs\Python\Python39\"
set "PythonPath3=%LOCALAPPDATA%\Programs\Python\Python39\Scripts\"
set "PythonPath4=%LOCALAPPDATA%\Programs\Python\Python39\"
set "PythonPath5=%LOCALAPPDATA%\Python\bin\"
set "PythonPath6=%LOCALAPPDATA%\Python\Scripts\"

set "PythonFound=false"
where python >nul 2>&1 && set "PythonFound=true"

if not "%PythonFound%"=="true" (
    echo  [!] Python executable not found directly in PATH. Attempting to add common Python install paths.
    setlocal enabledelayedexpansion
    set "CurrentPath=!PATH!"

    rem Check and add PythonPath1
    echo !CurrentPath! | find /I "%PythonPath1%" > nul || (
        if exist "%PythonPath1%" (
            setx PATH "!CurrentPath!;%PythonPath1%"
            set "CurrentPath=!CurrentPath!;%PythonPath1%"
            echo  [+] Added "%PythonPath1%" to PATH.
        )
    )

    rem Check and add PythonPath2
    echo !CurrentPath! | find /I "%PythonPath2%" > nul || (
        if exist "%PythonPath2%" (
            setx PATH "!CurrentPath!;%PythonPath2%"
            set "CurrentPath=!CurrentPath!;%PythonPath2%"
            echo  [+] Added "%PythonPath2%" to PATH.
        )
    )

    rem Check and add PythonPath3
    echo !CurrentPath! | find /I "%PythonPath3%" > nul || (
        if exist "%PythonPath3%" (
            setx PATH "!CurrentPath!;%PythonPath3%"
            set "CurrentPath=!CurrentPath!;%PythonPath3%"
            echo  [+] Added "%PythonPath3%" to PATH.
        )
    )

    rem Check and add PythonPath4
    echo !CurrentPath! | find /I "%PythonPath4%" > nul || (
        if exist "%PythonPath4%" (
            setx PATH "!CurrentPath!;%PythonPath4%"
            set "CurrentPath=!CurrentPath!;%PythonPath4%"
            echo  [+] Added "%PythonPath4%" to PATH.
        )
    )

    rem Check and add PythonPath5
    echo !CurrentPath! | find /I "%PythonPath5%" > nul || (
        if exist "%PythonPath5%" (
            setx PATH "!CurrentPath!;%PythonPath5%"
            set "CurrentPath=!CurrentPath!;%PythonPath5%"
            echo  [+] Added "%PythonPath5%" to PATH.
        )
    )
    
    rem Check and add PythonPath6
    echo !CurrentPath! | find /I "%PythonPath6%" > nul || (
        if exist "%PythonPath6%" (
            setx PATH "!CurrentPath!;%PythonPath6%"
            set "CurrentPath=!CurrentPath!;%PythonPath6%"
            echo  [+] Added "%PythonPath6%" to PATH.
        )
    )
    endlocal

    if "%PythonFound%"=="false" (
        echo  [!] Could not automatically find or add Python to PATH. Please ensure Python is installed and manually added to your system PATH.
    ) else (
        echo  [*] Python should now be in your PATH.
    )
) else (
    echo  [*] Python is already in the system PATH.
)

echo.
echo  ================================
echo  %AppName% installation complete!
echo.
echo  IMPORTANT: You must restart your terminal (Command Prompt, PowerShell, etc.)
echo             for the 'keygen' command to be available.
echo.
endlocal
pause
exit /b
