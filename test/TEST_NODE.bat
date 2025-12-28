@echo off
cd /d "%~dp0\.."

echo ==============================
echo 🧪 TEST NODE + WWEBJS
echo ==============================

python test\test_node.py

echo.
echo ==============================
echo Test finalizado
echo ==============================

pause
