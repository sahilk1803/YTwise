@echo off
echo ==============================================
echo   Starting YouTubeWise Full System...
echo ==============================================
start "YouTubeWise Backend" "%~dp0start_backend.bat"
start "YouTubeWise Dashboard" "%~dp0start_frontend.bat"
echo.
echo Both Backend (port 8000) and Dashboard (port 5173) are starting!
echo Next: Load the extension folder in chrome://extensions
echo.
timeout /t 5
start http://localhost:5173
