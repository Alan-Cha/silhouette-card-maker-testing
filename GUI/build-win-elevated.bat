@echo off
REM This script runs electron-builder with elevated privileges
REM Right-click and "Run as Administrator" or it will prompt for elevation

cd /d "%~dp0"
npm run dist:win
pause
