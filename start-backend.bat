@echo off
echo Starting FinPal Backend...
echo Server will be available at: http://localhost:3001

cd backend
python src/index.py

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo ERROR: Backend startup failed!
  echo Please check the error message above.
  echo.
  echo Common issues:
  echo 1. Make sure you have installed all required packages
  echo 2. Check that the paths in mcp_config.json are correct
  echo 3. Verify your API keys in .env file
  echo.
)

pause 