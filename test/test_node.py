import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
NODE_DIR = BASE_DIR / "nodejs"
TEST_JS = NODE_DIR / "test_node.js"

TIMEOUT_READY = 60  # segundos

def log(msg):
    print(f"[{datetime.now():%d/%m/%Y %H:%M:%S}] | TEST_NODE | {msg}", flush=True)

def main():
    if not TEST_JS.exists():
        log("❌ No existe test_node.js")
        sys.exit(1)

    log("🚀 Iniciando test de WhatsApp Web (Node.js)")
    log(f"📂 Working dir: {NODE_DIR}")

    proc = subprocess.Popen(
        ["node", str(TEST_JS)],
        cwd=NODE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )

    start = time.time()
    ready = False

    try:
        for line in proc.stdout:
            print(line.rstrip())

            if "EVENT_READY" in line:
                ready = True
                log("✅ READY detectado correctamente")
                break

            if time.time() - start > TIMEOUT_READY:
                log("⏱️ TIMEOUT: nunca llegó READY")
                proc.terminate()
                break

    except KeyboardInterrupt:
        log("🛑 Cancelado por usuario")
        proc.terminate()

    finally:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    if not ready:
        log("❌ TEST FALLÓ")
        sys.exit(1)

    log("🎉 TEST OK — WhatsApp Web funciona correctamente")
    sys.exit(0)

if __name__ == "__main__":
    main()
