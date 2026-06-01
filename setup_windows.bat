@echo off
REM setup_windows.bat - one-time setup for UniGrid on Windows.
REM Installs the compiled package and dependencies into a Python 3.9-3.12.
setlocal
cd /d "%~dp0"

echo [UniGrid] Windows setup starting...

set "PYEXE="
for %%V in (3.12 3.11 3.10 3.9) do (
    if not defined PYEXE (
        py -%%V -c "import sys" >nul 2>&1 && set "PYEXE=py -%%V"
    )
)
if not defined PYEXE (
    echo [UniGrid] ERROR: Python 3.9-3.12 not found.
    echo   Install Python 3.12 from https://www.python.org/downloads/ and check "Add Python to PATH".
    pause
    exit /b 1
)
echo [UniGrid] Using %PYEXE%

%PYEXE% -m pip install ".\runpfacdc_pkg_win\for_redistribution_files_only"
%PYEXE% -m pip install pandas openpyxl

echo.
echo [UniGrid] Setup complete. Run it with:  run_windows.bat
pause
