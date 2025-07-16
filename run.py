import subprocess, os
from datetime import datetime

version = '1.2.8'

def log(msg):
    log(f"[{datetime.now():%d/%m/%Y %H:%M:%S}] | {msg}")
log(f'run.py | 👨🏼‍💻 version: ${version}')
    
# Ruta del proyecto relativa a este script
project_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_path)

# Abrir Windows Terminal para el backend
log("run.py | 🚀 Ejecutando backend...")
subprocess.Popen('wt -w 0 nt -p "PowerShell" -d . python python_backend/app.py', shell=True)

# Abrir Windows Terminal para el bot de Node.js
log("run.py | 🤖 Ejecutando bot...")
subprocess.Popen('wt -w 0 nt -p "PowerShell" -d . node nodejs/bot.js', shell=True)

log("run.py | ✅ Todo iniciado. Cerrando script.")
