import os, yaml, json, asyncio, signal
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
CHAT_BOT_LEVEL = 'CHAT_BOT_LEVEL'
USER_DATA_FILE_NAME = 'users_data.json'
user_data_path = os.path.join(os.path.dirname(__file__), USER_DATA_FILE_NAME)
users_data = {}
backup_task = None
save_lock = asyncio.Lock()
__version__ = '1.0.4'

def log(msg):
    print(f"[{datetime.now():%d/%m/%Y %H:%M:%S}] | {msg}")

# Cargar menú
with open(os.path.join(os.path.dirname(__file__), 'menu.yaml'), encoding='utf-8') as f:
    MENU = yaml.safe_load(f)

# Cargar usuarios
if os.path.exists(user_data_path):
    try:
        with open(user_data_path, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        log(f"✅ Datos de usuarios cargados correctamente: {users_data}")
    except Exception as e:
        log(f"❌ Error al cargar datos: {e}")

# Guardar usuarios
async def save_user_data():
    async with save_lock:
        try:
            if users_data:
                with open(user_data_path, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                log(f"✅ Datos guardados correctamente: {users_data}")
        except Exception as e:
            log(f"❌ Error al guardar datos: {e}")

# Backup loop asincrónico
async def backup_loop():
    while True:
        await asyncio.sleep(300)
        await save_user_data()

# Ruta principal
@app.route('/responder', methods=['POST'])
def responder():
    data = request.get_json(force=True)
    mensaje = data.get('mensaje', '').strip()
    numero = data.get('numero', '').strip()

    if not numero:
        log("❌ Número no proporcionado")
        return jsonify({'error': 'Número no proporcionado'}), 400

    log(f"📨 {numero}: {mensaje}")
    user_data = users_data.setdefault(numero, {CHAT_BOT_LEVEL: 'root'})

    current_level = user_data.get(CHAT_BOT_LEVEL, 'root')
    current_node = MENU.get(current_level, {})
    options = current_node.get('options', {})
    answer = ''

    if mensaje in options:
        next_level = options[mensaje]
        if next_level in MENU:
            users_data[numero][CHAT_BOT_LEVEL] = next_level
            answer = MENU[next_level]['message']
    elif mensaje == '0':
        users_data[numero][CHAT_BOT_LEVEL] = 'root'
        answer = MENU['root']['message']
    elif mensaje == '9':
        back_level = current_node.get('back')
        if back_level and back_level in MENU:
            users_data[numero][CHAT_BOT_LEVEL] = back_level
            answer = MENU[back_level]['message']
        else:
            log(f"⚠️ Menú sin 'back': {current_level}")
    else:
        log(f"⚠️ Ignorando mensaje de {numero}: {mensaje}")

    #asyncio.run(save_user_data())
    return jsonify({'respuesta': answer})

# Manejo de salida limpia
def shutdown_handler(sig, frame):
    log("🛑 Señal de salida recibida, guardando datos...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(save_user_data())
    log("👋 Datos guardados. Saliendo...")
    os._exit(0)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    backup_task = loop.create_task(backup_loop())
    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(debug=True, port=5000, use_reloader=False)
