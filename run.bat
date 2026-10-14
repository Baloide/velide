@echo off
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
    python -m venv backend\.venv
    if errorlevel 1 goto failed
)
"backend\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 goto failed
pushd desktop\electron
call npm ci --no-audit --no-fund
if errorlevel 1 goto failed
call npm start
popd
if errorlevel 1 goto failed
exit /b 0
:failed
echo Could not start Velide. Check Python, Node.js and dependencies.
pause
exit /b 1
