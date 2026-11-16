@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   Check Python Environment
echo ============================================================

REM Find a Python with tkinter
set "PYTHON_EXE="

REM 1. PYTHON env var
if defined PYTHON (
    "%PYTHON%" -c "import tkinter" >nul 2>&1
    if !ERRORLEVEL! == 0 (
        set "PYTHON_EXE=%PYTHON%"
        echo   Found Python ^(from PYTHON env^): %PYTHON%
    )
)

REM 2. Common install locations
if not defined PYTHON_EXE (
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "C:\Python312\python.exe"
        "C:\Python311\python.exe"
        "C:\Python313\python.exe"
        "C:\Python310\python.exe"
    ) do (
        if not defined PYTHON_EXE (
            if exist %%P (
                %%P -c "import tkinter" >nul 2>&1
                if !ERRORLEVEL! == 0 (
                    set "PYTHON_EXE=%%~P"
                )
            )
        )
    )
)

REM 3. python from PATH
if not defined PYTHON_EXE (
    python -c "import tkinter" >nul 2>&1
    if !ERRORLEVEL! == 0 (
        set "PYTHON_EXE=python"
    )
)

REM 4. py launcher
if not defined PYTHON_EXE (
    py -3 -c "import tkinter" >nul 2>&1
    if !ERRORLEVEL! == 0 (
        set "PYTHON_EXE=py -3"
    )
)

if not defined PYTHON_EXE (
    echo.
    echo   ERROR: No Python with tkinter found!
    echo   Please install Python 3.10+ and check "tcl/tk" during install.
    echo   Or set PYTHON env var to correct python.exe path.
    echo.
    pause
    exit /b 1
)

echo   Python: %PYTHON_EXE%
"%PYTHON_EXE%" --version

echo.
echo ============================================================
echo   Check pip Dependencies
echo ============================================================

set "MISSING="
for %%P in (pyinstaller psutil Appium-Python-Client selenium) do (
    "%PYTHON_EXE%" -m pip show %%P >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo   %%P: MISSING
        set "MISSING=1"
    ) else (
        echo   %%P: OK
    )
)

if defined MISSING (
    echo.
    echo   ERROR: Some dependencies are missing!
    echo   Please install them manually:
    echo     "%PYTHON_EXE%" -m pip install pyinstaller psutil Appium-Python-Client selenium
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Clean previous build output
echo ============================================================

if exist "build" (
    rmdir /s /q "build"
    echo   Removed: build\
) else (
    echo   build\ not found, skip
)
if exist "dist" (
    rmdir /s /q "dist"
    echo   Removed: dist\
) else (
    echo   dist\ not found, skip
)

echo.
echo ============================================================
echo   Run build.py
echo ============================================================
echo.
"%PYTHON_EXE%" build.py
set "BUILD_RC=!ERRORLEVEL!"

echo.
if !BUILD_RC! == 0 (
    echo ============================================================
    echo   BUILD OK!
    echo ============================================================
    explorer "dist"
) else (
    echo ============================================================
    echo   BUILD FAILED! Exit code: !BUILD_RC!
    echo   Check error output above.
    echo ============================================================
    pause
)
