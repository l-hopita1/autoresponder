import sys, io, subprocess, os, threading
from datetime import datetime

# Forzar UTF-8 en consola de Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def log(prefix, msg):
    """Log con timestamp y prefijo del proceso"""
    print(f"[{datetime.now():%d/%m/%Y %H:%M:%S}] | {prefix}: {msg}", flush=True)


def stream_reader(prefix, stream):
    for line in iter(stream.readline, ''):
        log(prefix, line.rstrip())
    stream.close()

# Cargar versión del programa desde VERSION.txt
version_file = os.path.join(os.path.dirname(__file__), "python_backend/VERSION.txt")
if os.path.exists(version_file):
    with open(version_file, "r", encoding="utf-8") as f:
        APP_VERSION = f.read().strip()
else:
    APP_VERSION = "Versión desconocida"


def launch_process(name, cmd, cwd):
    """Lanza un proceso y loguea stdout/stderr en hilos separados"""
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )
    threading.Thread(target=stream_reader, args=(name, proc.stdout), daemon=True).start()
    threading.Thread(target=stream_reader, args=(name, proc.stderr), daemon=True).start()
    return proc


def terminate_process(proc, name):
    """Termina un proceso de manera segura"""
    if proc.poll() is None:
        log("LAUNCHER", f"⏹ Terminando {name}...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
            log("LAUNCHER", f"✅ {name} terminado correctamente.")
        except subprocess.TimeoutExpired:
            log("LAUNCHER", f"⚠️ {name} no respondió a terminate(), forzando kill...")
            proc.kill()
            proc.wait()
            log("LAUNCHER", f"✅ {name} forzado a finalizar.")


def main():
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    log(f"LAUNCHER", f"🚀 Ejecutando versión {APP_VERSION}")

    backend_path = os.path.join(base_path, "python_backend", "app.py")
    bot_path = os.path.join(base_path, "nodejs", "bot.js")

    backend_proc = launch_process("PYTHON", ["python", backend_path], os.path.dirname(backend_path))
    bot_proc = launch_process("NODEJS", ["node", bot_path], os.path.dirname(bot_path))

    log("LAUNCHER", "✅ Backend y Bot iniciados. Logs combinados aquí.")

    try:
        # Espera que ambos procesos terminen de forma natural
        backend_proc.wait()
        bot_proc.wait()
    except KeyboardInterrupt:
        log("LAUNCHER", "🛑 KeyboardInterrupt detectado, cerrando procesos...")
        terminate_process(backend_proc, "PYTHON")
        terminate_process(bot_proc, "NODEJS")

    log("LAUNCHER", "👋 Todos los procesos finalizados. Saliendo.")


if __name__ == "__main__":
    main()
