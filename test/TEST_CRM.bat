@echo off
echo ==============================
echo Ejecutando TEST CRM
echo ==============================

REM Ir al directorio del proyecto (1 nivel arriba de test)
cd /d %~dp0..

REM Ejecutar el test
python test\test_crm.py

echo.
echo ==============================
echo Test finalizado
echo ==============================

pause
