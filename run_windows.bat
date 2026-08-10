@echo off
REM run_windows.bat - run UniGrid on Windows.
setlocal
cd /d "%~dp0"

REM --- find Python: the py launcher first, then a plain python on PATH ---
set "PYEXE="
for %%V in (3.12 3.11 3.10 3.9) do (
    if not defined PYEXE (
        py -%%V -c "import sys" >nul 2>&1 && set "PYEXE=py -%%V"
    )
)
if not defined PYEXE python -c "import sys" >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE python3 -c "import sys" >nul 2>&1 && set "PYEXE=python3"

if not defined PYEXE (
    echo [UniGrid] No Python found. Run setup_windows.bat first.
    pause
    exit /b 1
)

%PYEXE% run_unigrid.py
echo.
pause
