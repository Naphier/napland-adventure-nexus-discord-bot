@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"

call :find_requirements
if "%REQ_FILE%"=="" (
    echo Could not find requirements.txt
    exit /b 1
)

for %%I in ("%REQ_FILE%") do set "REQ_DIR=%%~dpI"
set "VENV_DIR=%REQ_DIR%.venv"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    py -3 -m venv "%VENV_DIR%"
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Could not find activate.bat under "%VENV_DIR%\Scripts"
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

pip install -r "%REQ_FILE%"
if errorlevel 1 exit /b 1

set "DEV_REQ_FILE=%REQ_DIR%requirements_dev.txt"
if not exist "%DEV_REQ_FILE%" (
    if exist "%ROOT_DIR%requirements_dev.txt" (
        set "DEV_REQ_FILE=%ROOT_DIR%requirements_dev.txt"
    ) else if exist "%ROOT_DIR%app\requirements_dev.txt" (
        set "DEV_REQ_FILE=%ROOT_DIR%app\requirements_dev.txt"
    ) else (
        echo Could not find requirements_dev.txt
        exit /b 1
    )
)

pip install -r "%DEV_REQ_FILE%"

endlocal
exit /b 0

:find_requirements
if exist "%ROOT_DIR%requirements.txt" (
    set "REQ_FILE=%ROOT_DIR%requirements.txt"
    exit /b 0
)
if exist "%ROOT_DIR%app\requirements.txt" (
    set "REQ_FILE=%ROOT_DIR%app\requirements.txt"
    exit /b 0
)
set "REQ_FILE="
exit /b 0
