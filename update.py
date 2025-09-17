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

# Obtener solo el mensaje del último commit (sin hash)
result = subprocess.run(
    ['git', 'log', '-1', '--pretty=%s'],
    capture_output=True, text=True
)
current_commit = result.stdout.strip()

# Mostrar en consola
log(f"update.py | ✅ Versión actual: {current_commit}")

# Guardar en VERSION.txt
version_file = os.path.join(project_path, "python_backend/VERSION.txt")
with open(version_file, "w", encoding="utf-8") as f:
    f.write(current_commit + "\n")

log(f"update.py | 💾 Guardado en {version_file}")