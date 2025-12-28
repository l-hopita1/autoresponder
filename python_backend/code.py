# Import modules:
import asyncio, logging, sys, io, os,json
from threading import Thread
# Import class:
from .chatbot import chatBotWorker
from .crm import crmWorker
from .performance import performanceWorker
# Import others:
from flask import Flask, request, jsonify

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

config_server      = config.get("Server", {})
config_chatbot     = config.get("Chatbot", {})
config_crm         = config.get("CRM", {})
config_performance = config.get("Performance", {})

# ─────────────────────────────────────────────
# UTF-8 FORZADO
# ─────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

if os.name == "nt":
    os.system("chcp 65001 >nul")

# ─────────────────────────────────────────────
# LOGGER
# ─────────────────────────────────────────────
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

log_level = LOG_LEVELS.get(
    config_server.get("debug_level", "INFO"),
    logging.INFO
)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("SERVER")

# Mutear loggeos de servicios en 2° plano:
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("urllib3.util.retry").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.WARNING)
logging.getLogger("oauth2client").setLevel(logging.WARNING)

# ─────────────────────────────────────────────
# WORKERS
# ─────────────────────────────────────────────
if config_chatbot.get('enabled'):
    chatbot_worker= chatBotWorker(logger)
    chatbot_worker.init(config_chatbot)
else:
    chatbot_worker = None

if config_crm.get('enabled'):
    crm_worker = crmWorker(logger)
    crm_worker.init(config_crm)
else:
    crm_worker = None

if config_performance.get('enabled'):
    performance_worker = performanceWorker(logger)
    performance_worker.init(config_performance, chatbot_worker, crm_worker)
else:
    performance_worker = None

# ─────────────────────────────────────────────
# FLASK
# ─────────────────────────────────────────────
app = Flask(__name__)

if config_chatbot.get('enabled'):
    @app.route('/responder', methods=['POST'])
    def responder():
        data = request.get_json(force=True)
        return jsonify(chatbot_worker.handle_message(data))

if config_performance.get('enabled'):
    @app.route('/status', methods=['POST'])
    def performance():
        data = request.get_json(force=True)
        return jsonify(performance_worker.build_status(data))

if config_crm.get('enabled'):
    @app.route('/crm', methods=['POST'])
    def crm():
        data = request.get_json(force=True)
        return jsonify(crm_worker.handle_crm(data))

SERVER_HOST = config_server.get("host", "0.0.0.0")
SERVER_PORT = int(config_server.get("port", 5000))
def run_flask():
    logger.info(f"🚀 Flask iniciado en {SERVER_HOST}:{SERVER_PORT}")
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=False,
        use_reloader=False
    )



# ─────────────────────────────────────────────
# MAIN ASYNC
# ─────────────────────────────────────────────
async def main():
    logger.info("⚙️ Iniciando workers async")

    tasks = [
        asyncio.create_task(chatbot_worker.run(), name="chatbot"),
        asyncio.create_task(crm_worker.run(), name="crm"),
        asyncio.create_task(performance_worker.run(), name="performance"),
    ]

    # Flask en thread separado
    Thread(target=run_flask, daemon=True).start()

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.warning("⛔ Cancelación recibida, apagando workers...")
    finally:
        for t in tasks:
            t.cancel()
        logger.info("👋 Server finalizado correctamente")

# ─────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error("🛑 KeyboardInterrupt — apagando servidor")
