@echo off
cd /d "%~dp0backend"
if "%GEMINI_API_KEY%"=="" (
  set /p GEMINI_API_KEY=Paste your Gemini API key and press Enter: 
)
start "" "%~dp0index.html"
echo.
echo Server starting. Leave this window open while you use the site.
echo Close this window to stop it.
echo.
python server.py
pause