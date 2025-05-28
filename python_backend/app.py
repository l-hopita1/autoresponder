# Importar módulos
import json, os

from flask import Flask, request, jsonify
# Importar clases
from datetime import datetime

app = Flask(__name__)

# Cargar el menú desde el archivo JSON
with open(os.path.join(os.path.dirname(__file__), 'menu.json'), encoding='utf-8') as f:
    MENU = json.load(f)

# Estados por usuario
user_states = {}

def log(msg):
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print(f"[{timestamp}] {msg}")

@app.route('/responder', methods=['POST'])
def responder():
    try:
        data = request.get_json(force=True)
        mensaje = data.get('mensaje', '').strip()
        numero = data.get('numero', '').strip()
    except Exception as e:
        log(f"❌ Error al parsear JSON: {e}")
        return jsonify({'error': 'Solicitud malformada'}), 400

    log(f"📨 Mensaje de {numero}: {mensaje}")
    state = user_states.get(numero, {'level': 'root'})
    current_level = state['level']

    # Si el usuario envía "0", volver al menú principal
    if mensaje == '0':
        user_states[numero] = {'level': 'root'}
        return jsonify({'respuesta': MENU['root']['message']})

    # Si el usuario envía "9", ir al menú anterior si está definido
    if mensaje == '9':
        previous_level = MENU.get(current_level, {}).get('back')
        if previous_level:
            user_states[numero] = {'level': previous_level}
            return jsonify({'respuesta': MENU[previous_level]['message']})

    # Si el mensaje no es un número válido, ignorar (no responder nada)
    options = MENU.get(current_level, {}).get('options', {})
    if mensaje in options:
        next_level = options[mensaje]
        user_states[numero] = {'level': next_level}
        return jsonify({'respuesta': MENU[next_level]['message']})

    # No responder si no es una opción válida
    log(f"⚠️ Mensaje ignorado de {numero}: {mensaje}")
    return jsonify({'respuesta': ''})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
