import subprocess, os
from datetime import datetime

def log(msg):
    print(f"[{datetime.now():%d/%m/%Y %H:%M:%S}] | {msg}")
    
# Ruta del proyecto relativa a este script
project_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_path)

# Comandos Git
commands = [
    'git fetch --all',
    'git reset --hard origin/main'
]

for cmd in commands:
    log(f"update.py | 📦 Ejecutando: {cmd}")
    subprocess.run(cmd, shell=True, check=True)