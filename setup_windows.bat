@echo off
REM setup_windows.bat - one-time setup for UniGrid on Windows.
REM Installs the compiled package and dependencies into a Python 3.9-3.12.
setlocal
cd /d "%~dp0"

echo [UniGrid] Windows setup starting...

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
    echo.
    echo *** SETUP FAILED ***
    echo [UniGrid] No Python found on this PC.
    echo   Install Python 3.12 from https://www.python.org/downloads/
    echo   and tick "Add python.exe to PATH" during setup.
    echo.
    pause
    exit /b 1
)

echo [UniGrid] Using %PYEXE%
%PYEXE% --version
echo.

%PYEXE% -m pip install ".\unigrid_pkg_win\for_redistribution_files_only"
if errorlevel 1 goto :failed
%PYEXE% -m pip install pandas openpyxl
if errorlevel 1 goto :failed

echo.
echo *** SETUP OK ***
echo [UniGrid] Now run:  run_windows.bat
echo.
pause
exit /b 0

:failed
echo.
echo *** SETUP FAILED ***
echo [UniGrid] pip install did not finish - see the messages above.
echo   MATLAB R2024b supports Python 3.9 - 3.12 only.
echo   If the version printed above is 3.13 or newer, install Python 3.12
echo   from https://www.python.org/downloads/ and run this file again.
echo.
pause
exit /b 1
