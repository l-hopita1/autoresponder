@echo off
cd /d %~dp0

REM Ejecuta update_and_run.py en Windows Terminal, en perfil PowerShell
wt -w 0 nt --title "Actualizador" -p "PowerShell" -d . powershell -NoExit -Command "python ./run.py"
