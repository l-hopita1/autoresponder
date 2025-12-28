# Import Modules:
import psutil, time, os
# Import Class:
from worker_class import workerClass
from chatbot import chatBotWorker
from crm import crmWorker
from logging import Logger

class performanceWorker(workerClass):
    _version_filename = "VERSION.txt"
    
    def __init__(self, logger: Logger):
        self._git_version_str = "Versión desconocida"
        self._initialization_time = self.current_time_str()
        super().__init__(logger)

    
    def init(self, config:dict, chatbot_worker: chatBotWorker, crm_worker: crmWorker):
        self._config = config
        self._crm_worker = crm_worker
        self._chatbot_worker = chatbot_worker

        # Cargar versión del programa desde VERSION.txt
        version_file = os.path.join(os.path.dirname(__file__), self._version_filename)
        if os.path.exists(version_file):
            with open(version_file, "r", encoding="utf-8") as f:
                self._git_version_str = f.read().strip()
        
        self.logger.info(f'{self.__class__.__name__} | init | ✅ Inicializado correctamente.')
        
    def build_status(self, data:dict)-> dict:
        contact_name = data.get('contact_name','').strip()
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
- Versión: {self._git_version_str}
- Fecha de inicio: {self._initialization_time}
- Última respuesta automática: {self._chatbot_worker.last_answer}
- Contador de clientes: {self._chatbot_worker.user_counter}
- Tiempo de esta respuesta: {(time.time()-msg_timestamp):.1f} segundos

📊 *Especificaciones del Backend*
- Uso de RAM (backend): {mem_mb:.1f} MB de {total_mem_mb:.0f} MB
- Uso de CPU (backend): {cpu_percent:.1f} %

💻 *Especificaciones del Sistema*
- Uso de RAM: {sys_mem_percent:.1f} %
- Uso de CPU: {sys_cpu_percent:.1f} %
"""
        return {'respuesta': answer}