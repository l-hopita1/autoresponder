@echo off
cd /d %~dp0

REM Ejecuta update.py en Windows Terminal, en perfil PowerShell
wt -w 0 nt --title "UPDATE TO MAIN" -p "PowerShell" -d . powershell -NoExit -Command "python ./update.py"
