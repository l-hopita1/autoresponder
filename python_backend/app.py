import os, yaml, json, asyncio, time, psutil, sys, io
from flask import Flask, request, jsonify
from datetime import datetime
from threading import Thread

app = Flask(__name__)

CHAT_BOT_LEVEL = 'CHAT_BOT_LEVEL'
USER_DATA_FILE_NAME = 'users_data.json'
user_data_path = os.path.join(os.path.dirname(__file__), USER_DATA_FILE_NAME)
users_data = {}
save_lock = asyncio.Lock()
last_answer = None

# Forzar UTF-8 en consola
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

if os.name == "nt":
    os.system("chcp 65001 >nul")

def current_time_str():
    return f"[{datetime.now():%d/%m/%Y %H:%M:%S}]"

initialization_time = current_time_str()

# Cargar versión del programa desde VERSION.txt
version_file = os.path.join(os.path.dirname(__file__), "VERSION.txt")
if os.path.exists(version_file):
    with open(version_file, "r", encoding="utf-8") as f:
        APP_VERSION = f.read().strip()
else:
    APP_VERSION = "Versión desconocida"

# Cargar menú
with open(os.path.join(os.path.dirname(__file__), 'menu.yaml'), encoding='utf-8') as f:
    MENU = yaml.safe_load(f)

# Cargar usuarios
if os.path.exists(user_data_path):
    try:
        with open(user_data_path, 'r', encoding='utf-8') as f:
            users_data = dict(json.load(f))
        print(f"app.py | ✅ {len(users_data)} usuarios cargados correctamente.")
    except Exception as e:
        print(f"❌ Error al cargar datos-> {e.__class__.__name__}: {e}")

# --- Funciones auxiliares ---
def normalize(text):
    return ' '.join(text.strip().lower().split())

async def save_user_data():
    async with save_lock:
        try:
            if users_data:
                with open(user_data_path, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                print(f"save_user_data | ✅ {len(users_data)} usuarios guardados correctamente")
        except Exception as e:
            print(f"save_user_data | ❌ Error al guardar datos: {e}")

async def backup_loop():
    try:
        while True:
            print("backup_loop | Ejecutando...")
            await save_user_data()
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("backup_loop | Cancelado")

# --- Endpoints ---
@app.route('/status', methods=['POST'])
def status():
    global last_answer
    data = request.get_json(force=True)
    contact_name = data.get('contact_name').strip()
    msg_timestamp = data.get('msg_timestamp', time.time())

    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.5)

    sys_mem = psutil.virtual_memory()
    sys_mem_percent = sys_mem.percent
    total_mem_mb  = sys_mem.total / (1024 * 1024)
    sys_cpu_percent = psutil.cpu_percent(interval=0.5)

    answer = f"""*{contact_name}*:
✅ *Datos del Backend:*
- Versión: {APP_VERSION}
- Fecha de inicio: {initialization_time}
- Última respuesta automática: {last_answer}
- Contador de clientes: {len(users_data)}
- Tiempo de esta respuesta: {(time.time()-msg_timestamp):.1f} segundos

📊 *Especificaciones del Backend*
- Uso de RAM (backend): {mem_mb:.1f} MB de {total_mem_mb:.0f} MB
- Uso de CPU (backend): {cpu_percent:.1f} %

💻 *Especificaciones del Sistema*
- Uso de RAM: {sys_mem_percent:.1f} %
- Uso de CPU: {sys_cpu_percent:.1f} %
"""
    return jsonify({'respuesta': answer})

@app.route('/responder', methods=['POST'])
def responder():
    global last_answer
    data = request.get_json(force=True)
    message = data.get('message', '').strip()
    number = data.get('number', '').strip()
    messageHistory = data.get('messageHistory')

    if messageHistory:
        menu_messages = {nodo['message'] for nodo in MENU.values()}
        for m in messageHistory:
            if m.get("fromMe") and m.get("body"):
                contenido = m["body"].strip()
                contenido_normalizado = normalize(contenido)
                menu_normalizados = [normalize(msg) for msg in menu_messages]
                if contenido_normalizado not in menu_normalizados:
                    print(f"responder | 🤖 Chat intervenido por humano, no se responderá a {number}. Último mensaje de humano: {contenido}")
                    return jsonify({'respuesta': ''})
    if not number:
        print("responder | ❌ Número no proporcionado")
        return jsonify({'error': 'Número no proporcionado'}), 400

    print(f"responder | 📨 {number}: {message}")
    
    answer = ''    
    if not users_data.get(number):
        users_data[number] = {CHAT_BOT_LEVEL: 'root'}
        answer = MENU['root']['message']
        last_answer = current_time_str()
        
    user_data = users_data.get(number)
    current_level = user_data.get(CHAT_BOT_LEVEL, 'root')
    current_node = MENU.get(current_level, {})
    options = current_node.get('options', {})

    if message in options:
        next_level = options[message]
        if next_level in MENU:
            users_data[number][CHAT_BOT_LEVEL] = next_level
            answer = MENU[next_level]['message']
            last_answer = current_time_str()
    elif message == '0':
        users_data[number][CHAT_BOT_LEVEL] = 'root'
        answer = MENU['root']['message']
        last_answer = current_time_str()
    elif message == '9':
        back_level = current_node.get('back')
        if back_level and back_level in MENU:
            users_data[number][CHAT_BOT_LEVEL] = back_level
            answer = MENU[back_level]['message']
        last_answer = current_time_str()
    else:
        print(f"responder | ⚠️ Ignorando mensaje de {number}, el mensaje no es una opción del menú")

    return jsonify({'respuesta': answer})

# --- Main ---
async def main():
    # Lanzar loops de backup
    backup_task = asyncio.create_task(backup_loop())

    # Lanzar Flask en thread separado
    def run_flask():
        app.run(debug=True, port=5000, use_reloader=False)
    Thread(target=run_flask, daemon=True).start()

    # Esperar indefinidamente
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        print("main | Cancelado, iniciando shutdown...")
        backup_task.cancel()
        await save_user_data()
        print("👋 Datos guardados. Saliendo...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 KeyboardInterrupt recibido, cancelando main...")
