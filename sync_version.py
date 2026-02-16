import subprocess, os, re, sys, io
from datetime import datetime

# Force UTF-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def log(msg):
    print(f"[{datetime.now():%d/%m/%Y %H:%M:%S}] | SYNC: {msg}")

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(BASE_DIR, "python_backend", "VERSION.txt")

def get_git_version():
    try:
        # Obtener último mensaje de commit
        result_msg = subprocess.run(
            ['git', 'log', '-1', '--pretty=%s'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8' # Forzar UTF-8
        )
        if result_msg.returncode != 0:
            return None, "Error en git log"
        
        commit_msg = result_msg.stdout.strip()

        # Verificar si hay cambios sin commitear (dirty)
        result_status = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        is_dirty = bool(result_status.stdout.strip())
        
        return commit_msg, is_dirty

    except FileNotFoundError:
        return None, "Git no instalado o no encontrado"
    except Exception as e:
        return None, str(e)

def main():
    log("Iniciando sincronización de versión...")
    
    version_msg, is_dirty = get_git_version()
    
    if not version_msg:
        log(f"⚠ No se pudo obtener versión de git: {is_dirty}")
        return

    # Extraer versión entre corchetes si existe, sino usar todo el mensaje
    # Ejemplo: "[2.1.1] - fix bug" -> "[2.1.1]"
    # Ejemplo: "update readme" -> "update readme"
    match = re.search(r'\[.*?\]', version_msg)
    final_version = match.group(0) if match else version_msg

    # Agregar indicador dirty si corresponde
    if is_dirty:
        final_version += " (modificado)"

    # Escribir en VERSION.txt
    try:
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            f.write(final_version)
        log(f"✅ Versión actualizada: {final_version}")
    except Exception as e:
        log(f"❌ Error al escribir VERSION.txt: {e}")

if __name__ == "__main__":
    main()
