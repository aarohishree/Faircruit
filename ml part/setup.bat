@echo off
echo ========================================
echo AI Assessment System - Setup
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Instructions:
echo ========================================
echo 1. Get your Gemini API key from: https://makersuite.google.com/app/apikey
echo 2. Copy .env.example to .env
echo 3. Edit .env and add your API key
echo.
echo Then run: python main.py
echo.
pause
