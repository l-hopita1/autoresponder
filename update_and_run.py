import subprocess, os

# Ruta del proyecto relativa a este script
project_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_path)

# Comandos Git
commands = [
    'git fetch --all',
    'git reset --hard origin/main'
]

for cmd in commands:
    print(f"update_and_run | 📦 Ejecutando: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

# Abrir una consola para el backend
print("update_and_run | 🚀 Ejecutando backend...")
subprocess.Popen('start cmd /k python python_backend/app.py', shell=True)

# Abrir otra consola para el bot de Node.js
print("update_and_run | 🤖 Ejecutando bot...")
subprocess.Popen('start cmd /k node nodejs/bot.js', shell=True)

# Mensaje final y cierre automático
print("update_and_run | ✅ Todo iniciado. Cerrando script.")