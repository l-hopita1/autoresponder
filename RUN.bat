@echo off
cd /d %~dp0
echo 🚀 Ejecutando versión 1.2.14
REM Abrir backend Python en nueva ventana CMD
start "Backend Python" cmd /k "cd python_backend && python app.py"

REM Abrir bot Node.js en nueva ventana CMD
start "Bot Node.js" cmd /k "cd nodejs && node bot.js"

REM Mensaje final para saber que todo arrancó
echo ✅ Backend y Bot iniciados en ventanas separadas.
pause