@echo off
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
    python -m venv backend\.venv
    if errorlevel 1 goto failed
)
"backend\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt -r desktop\requirements-build.txt
if errorlevel 1 goto failed
"backend\.venv\Scripts\python.exe" scripts\build_windows.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Windows build failed.
pause
exit /b 1
