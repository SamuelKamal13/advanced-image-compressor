@echo off
REM Advanced Image Compressor - Windows Batch Launcher
REM Usage: compressor.bat [mode] [args...]

setlocal

REM Set the Python path
set PYTHON_PATH="E:/Codes/Image compresd/.venv/Scripts/python.exe"

REM Check if Python exists
if not exist %PYTHON_PATH% (
    echo Error: Python virtual environment not found!
    echo Please run setup first or check the path.
    pause
    exit /b 1
)

REM Check if arguments provided
if "%1"=="" (
    echo Advanced Image Compressor
    echo =========================
    echo.
    echo Usage: compressor.bat [mode] [args...]
    echo.
    echo Available modes:
    echo   gui         - Launch graphical interface
    echo   cli         - Command line interface
    echo   convert     - Format conversion tool
    echo.
    echo Examples:
    echo   compressor.bat gui
    echo   compressor.bat cli image.jpg
    echo   compressor.bat convert image.png webp
    echo.
    pause
    exit /b 0
)

REM Run the main launcher with all arguments
%PYTHON_PATH% main.py %*

REM Keep window open if there was an error
if errorlevel 1 pause