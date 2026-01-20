@echo off
echo Starting Neo Alexandria 2.0 Backend Server...
echo.

REM Start the server in the background
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1

REM Wait a moment for server to start
timeout /t 5 /nobreak > nul

echo Running comprehensive endpoint tests...
echo.

REM Run the tests
python test_all_endpoints.py

REM Capture exit code
set TEST_EXIT_CODE=%ERRORLEVEL%

REM Kill the server
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a > nul 2>&1

echo.
echo Server stopped.

exit /b %TEST_EXIT_CODE%
