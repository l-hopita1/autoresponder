@echo off
REM Cambiar al directorio del script
cd /d "%~dp0"

REM Ejecutar el launcher
start "Autoresponder" cmd /k "python launcher.py"
