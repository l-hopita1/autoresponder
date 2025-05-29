import os
import yaml
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Cargar el menú una sola vez al iniciar la app
with open(os.path.join(os.path.dirname(__file__), 'menu.yaml'), encoding='utf-8') as f:
    MENU = yaml.safe_load(f)

# Estados por usuario (en memoria, considerar almacenamiento persistente si es necesario)
user_states = {}

def log(msg: str) -> None:
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print(f"[{timestamp}] {msg}")

@app.route('/responder', methods=['POST'])
def responder():
    data = request.get_json(force=True)
    mensaje = data.get('mensaje', '').strip()
    numero = data.get('numero', '').strip()

    if not numero:
        log("❌ Número no proporcionado")
        return jsonify({'error': 'Número no proporcionado'}), 400

    log(f"📨 Mensaje de {numero}: {mensaje}")

    # Estado actual del usuario, por defecto 'root'
    current_level = user_states.get(numero, 'root')
    current_node = MENU.get(current_level, {})
    options = current_node.get('options', {})

    # Ir al menú principal con "0"
    if mensaje == '0':
        user_states[numero] = 'root'
        return jsonify({'respuesta': MENU['root']['message']})

    # Ir atrás con "9" si hay una referencia válida en 'back'
    if mensaje == '9':
        back_level = current_node.get('back')
        if back_level and back_level in MENU:
            user_states[numero] = back_level
            return jsonify({'respuesta': MENU[back_level]['message']})
        else:
            log(f"⚠️ Menú sin 'back': {current_level}")
            return jsonify({'respuesta': ''})  # o podés responder un mensaje de error

    # Si es una opción válida, ir al siguiente nivel
    if mensaje in options:
        next_level = options[mensaje]
        if next_level in MENU:
            user_states[numero] = next_level
            return jsonify({'respuesta': MENU[next_level]['message']})

    # Si no es válido, no responder
    log(f"⚠️ Opción inválida de {numero} en nivel {current_level}: {mensaje}")
    return jsonify({'respuesta': ''})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
