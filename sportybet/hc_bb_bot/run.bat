@echo off
chcp 65001 >nul
echo 🏀 Starting Basketball Betting Bot...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Check environment variables
if "%TELEGRAM_BOT_TOKEN%"=="" (
    if exist ".env" (
        echo 📄 Loading environment from .env file...
        for /f "tokens=1,2 delims==" %%a in (.env) do (
            set "%%a=%%b"
        )
    ) else (
        echo ❌ Error: TELEGRAM_BOT_TOKEN not set and .env file not found!
        echo Please set up your .env file first:
        echo   copy .env.example .env
        echo   REM Edit .env with your credentials
        pause
        exit /b 1
    )
)

REM Run the bot
echo 🚀 Bot is starting...
python bot.py

pause
