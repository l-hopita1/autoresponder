import os, yaml, json, asyncio, signal, time, psutil
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
CHAT_BOT_LEVEL = 'CHAT_BOT_LEVEL'
USER_DATA_FILE_NAME = 'users_data.json'
user_data_path = os.path.join(os.path.dirname(__file__), USER_DATA_FILE_NAME)
users_data = {}
backup_task = None
save_lock = asyncio.Lock()

last_answer = None

def current_time_str():
    return f"[{datetime.now():%d/%m/%Y %H:%M:%S}]"

initalization_time = current_time_str() # Primer tiempo en que está ejecutandose la función.

def log(msg):
    print(f"[{current_time_str()}] | {msg}")
    
# Cargar menú
with open(os.path.join(os.path.dirname(__file__), 'menu.yaml'), encoding='utf-8') as f:
    MENU = yaml.safe_load(f)

# Cargar usuarios
if os.path.exists(user_data_path):
    try:
        with open(user_data_path, 'r', encoding='utf-8') as f:
            users_data = dict(json.load(f))
        log(f"app.py | ✅ {len(users_data)} usuarios cargados correctamente.")
    except Exception as e:
        log(f"❌ Error al cargar datos-> {e.__class__.__name__}: {e}")

# Guardar usuarios
async def save_user_data():
    async with save_lock:
        try:
            if users_data:
                with open(user_data_path, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                log(f"save_user_data | ✅ Datos guardados correctamente: {users_data.items()}")
        except Exception as e:
            log(f"save_user_data | ❌ Error al guardar datos: {e}")

# Backup loop asincrónico
async def backup_loop():
    while True:
        await asyncio.sleep(300)
        await save_user_data()

# Estado de programa:
@app.route('/status', methods=['POST'])
def status():
    global last_answer
    data = request.get_json(force=True)
    contact_name = data.get('contact_name').strip()
    msg_timestamp = data.get('msg_timestamp')

    # Datos de proceso y sistema
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.5)

    sys_mem = psutil.virtual_memory()
    sys_mem_total = sys_mem.total / (1024 * 1024)
    sys_mem_available = sys_mem.available / (1024 * 1024)
    sys_cpu_percent = psutil.cpu_percent(interval=0.5)

    answer = f"""*{contact_name}*: Todo bien ✅
- El backend se está ejecutando desde: {initalization_time}
- Última respuesta automática: {last_answer}
- Contador de clientes: {len(users_data)}
- Tiempo de respuesta: {time.time()-msg_timestamp} segundos

📊 *Estado del Backend*
- Uso de RAM (backend): {mem_mb:.2f} MB
- Uso de CPU (backend): {cpu_percent:.1f} %

💻 *Estado del Sistema*
- RAM total: {sys_mem_total:.2f} MB
- RAM libre: {sys_mem_available:.2f} MB
- Uso total de CPU: {sys_cpu_percent:.1f} %
"""
    return jsonify({'respuesta': answer})

# Ruta principal
@app.route('/responder', methods=['POST'])
def responder():
    global last_answer
    # Datos de entrada:
    data = request.get_json(force=True)
    message = data.get('message', '').strip()
    number = data.get('number', '').strip()
    messageHistory = data.get('messageHistory')

    # Validación de entrada:
    if messageHistory:
        menu_messages = {nodo['message'] for nodo in MENU.values()}
        for m in messageHistory:
            if m.get("fromMe") and m.get("body"):
                contenido = m["body"].strip()
                contenido_normalizado = normalize(contenido)
                menu_normalizados = [normalize(msg) for msg in menu_messages]
                if contenido_normalizado not in menu_normalizados:
                    log(f"responder | 🤖 Chat intervenido por humano, no se responderá a {number}. Último mensaje de humano: {contenido}")
                    return jsonify({'respuesta': ''})
    if not number:
        log("responder | ❌ Número no proporcionado")
        return jsonify({'error': 'Número no proporcionado'}), 400

    log(f"responder | 📨 {number}: {message}")
    
    answer = ''    
    if not users_data.get(number): # Si no hay datos del usuario, responder con la raiz.
        users_data[number] = {CHAT_BOT_LEVEL: 'root'}
        answer = MENU['root']['message']
        last_answer = current_time_str()
        
    # Obtención de datos del usuario:
    user_data = users_data.get(number)
    current_level = user_data.get(CHAT_BOT_LEVEL, 'root')
    current_node = MENU.get(current_level, {})
    options = current_node.get('options', {})

    # Respuesta automática:
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
        else:
            log(f"responder | ⚠️ Menú sin 'back': {current_level}")
        last_answer = current_time_str()
    else:
        log(f"responder | ⚠️ Ignorando mensaje de {number}, el mensaje no es una opción del menú")

    return jsonify({'respuesta': answer})

# Manejo de salida limpia
def shutdown_handler(sig, frame):
    log("shutdown_handler | 🛑 Señal de salida recibida, guardando datos...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(save_user_data())
    log("shutdown_handler | 👋 Datos guardados. Saliendo...")
    os._exit(0)

def normalize(text):
    return ' '.join(text.strip().lower().split())

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    backup_task = loop.create_task(backup_loop())
    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(debug=True, port=5000, use_reloader=False)