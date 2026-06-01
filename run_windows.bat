@echo off
REM run_windows.bat - run UniGrid on Windows.
setlocal
cd /d "%~dp0"

set "PYEXE="
for %%V in (3.12 3.11 3.10 3.9) do (
    if not defined PYEXE (
        py -%%V -c "import sys" >nul 2>&1 && set "PYEXE=py -%%V"
    )
)
if not defined PYEXE (
    echo [UniGrid] Python 3.9-3.12 not found. Run setup_windows.bat first.
    pause
    exit /b 1
)
%PYEXE% run_unigrid.py
pause
