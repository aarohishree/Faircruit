@echo off
echo ========================================
echo AI Assessment System - Starting...
echo ========================================
echo.
echo Running setup test first...
echo.

python test_setup.py

echo.
echo ========================================
echo Starting Main System...
echo ========================================
echo.

python main.py

pause
