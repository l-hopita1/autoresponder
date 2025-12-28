# Import modules:
import os, yaml, json, asyncio, time
# Import class:
from logging import Logger
from worker_class import workerClass



class chatBotWorker(workerClass):
    _chat_bot_level = "CHAT_BOT_LEVEL"

    @property
    def last_answer(self)->float:
        return self._last_answer
    
    @property
    def user_counter(self)->int:
        return len(self._users_data)
    
    def __init__(self, logger: Logger):
        self._menu = {}
        self._last_answer = None
        self._user_data_path = None
        self._users_data = {}
        self._save_lock = asyncio.Lock()
        super().__init__(logger)

    def init(self, config: dict):
        self._config = config

        # Cargar menú
        with open(os.path.join(os.path.dirname(__file__), 'menu.yaml'), encoding='utf-8') as f:
            self._menu = yaml.safe_load(f)
        if not self._menu or "root" not in self._menu:
            raise RuntimeError("menu.yaml inválido o sin nodo root")

        # Cargar usuarios
        self._user_data_path = os.path.join(os.path.dirname(__file__), self._config.get('user_data_filename'))
        if os.path.exists(self._user_data_path):
            try:
                with open(self._user_data_path, 'r', encoding='utf-8') as f:
                    self._users_data = dict(json.load(f))
                self.logger.debug(f'{self.__class__.__name__} | init | ✅ {len(self._users_data)} usuarios cargados correctamente.')
            except Exception as e:
                self.logger.error(f'{self.__class__.__name__} | init | ❌ Error al cargar datos-> {e.__class__.__name__}: {e}')

        self.logger.info(f'{self.__class__.__name__} | init | ✅ Inicializado correctamente.')

    async def run(self):
        try:
            while True:
                self.logger.info(f'{self.__class__.__name__} | run | Ejecutando...')
                await self.save_user_data()
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            self.logger.info(f'{self.__class__.__name__} | run | Cancelado')

    async def save_user_data(self):
        async with self._save_lock:
            try:
                if self._users_data:
                    with open(self._user_data_path, 'w', encoding='utf-8') as f:
                        json.dump(self._users_data, f, ensure_ascii=False, indent=2)
                    self.logger.info(f'{self.__class__.__name__} | save_user_data | ✅ {len(self._users_data)} usuarios guardados correctamente')
            except Exception as e:
                self.logger.error(f'{self.__class__.__name__} | save_user_data | ❌ Error al guardar datos: {e}')

    def handle_message(self, data:dict):
        message = data.get('message', '').strip()
        number = data.get('number', '').strip()
        messageHistory = data.get('messageHistory')

        if messageHistory:
            menu_messages = {nodo['message'] for nodo in self._menu.values()}
            for m in messageHistory:
                if m.get("fromMe") and m.get("body"):
                    contenido = m["body"].strip()
                    contenido_normalizado = self.normalize(contenido)
                    menu_normalizados = [self.normalize(msg) for msg in menu_messages]
                    if contenido_normalizado not in menu_normalizados:
                        self.logger.info(f'{self.__class__.__name__} | handle_message | 🤖 Chat intervenido por humano, no se responderá a {number}. Último mensaje de humano: {contenido}')
                        return {'respuesta': ''}
        if not number:
            self.logger.error(f'{self.__class__.__name__} | handle_message | ❌ Número no proporcionado')
            return {'error': 'Número no proporcionado'}, 400

        self.logger.debug(f'{self.__class__.__name__} | responder | 📨 {number}: {message}')
        
        answer = ''    
        if not self._users_data.get(number):
            self._users_data[number] = {self._chat_bot_level: 'root'}
            answer = self._menu['root']['message']
            self._last_answer = time.monotonic()
            
        current_level = self._users_data[number].get(self._chat_bot_level, 'root')    
        current_node = self._menu.get(current_level, {})
        options = current_node.get('options', {})

        if message in options:
            next_level = options[message]
            if next_level in self._menu:
                self._users_data[number][self._chat_bot_level] = next_level
                answer = self._menu[next_level]['message']
                self._last_answer = time.monotonic()
        elif message == '0':
            self._users_data[number][self._chat_bot_level] = 'root'
            answer = self._menu['root']['message']
            self._last_answer = time.monotonic()
        elif message == '9':
            back_level = current_node.get('back')
            if back_level and back_level in self._menu:
                self._users_data[number][self._chat_bot_level] = back_level
                answer = self._menu[back_level]['message']
            self._last_answer = time.monotonic()
        else:
            self.logger.warning(f'{self.__class__.__name__} | responder | ⚠️ Ignorando mensaje de {number}, el mensaje no es una opción del menú')

        return {'respuesta': answer}