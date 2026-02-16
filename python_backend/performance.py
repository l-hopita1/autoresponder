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

        # System Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

        # Network Stats (since boot)
        net_io = psutil.net_io_counters()    
        sent_mb = net_io.bytes_sent / (1024 * 1024)
        recv_mb = net_io.bytes_recv / (1024 * 1024)

        # Disk Usage (C:)
        try:
            disk_usage = psutil.disk_usage('C:\\')
            disk_total_gb = disk_usage.total / (1024**3)
            disk_free_gb = disk_usage.free / (1024**3)
            disk_percent = disk_usage.percent
        except:
             disk_total_gb = 0
             disk_free_gb = 0
             disk_percent = 0

        answer = f"""*Estado del Sistema* 🤖
📅 *Fecha:* {time.strftime('%d/%m/%Y %H:%M:%S')}
⏱ *Uptime Sistema:* {uptime_string}
⏱ *Uptime Bot:* {self._initialization_time}
🔢 *Versión:* {self._git_version_str}

📊 *Estadísticas de Autoresponder*
----------------------------------
💬 *Última respuesta:* {self._chatbot_worker.last_answer}
👥 *Clientes interactuando:* {self._chatbot_worker.user_counter}
⚡ *Tiempo de respuesta:* {(time.time()-msg_timestamp):.2f}s
🧠 *RAM Bot:* {mem_mb:.1f} MB
⚙️ *CPU Bot:* {cpu_percent:.1f}%

💻 *Recursos del Servidor*
----------------------------------
🧠 *RAM Total:* {total_mem_mb:.0f} MB (Uso: {sys_mem_percent:.1f}%)
⚙️ *CPU Total:* {sys_cpu_percent:.1f}%
💾 *Disco (C:):* {disk_free_gb:.1f} GB libres de {disk_total_gb:.1f} GB ({disk_percent}%)
🌐 *Red:* ⬆️ {sent_mb:.0f} MB | ⬇️ {recv_mb:.0f} MB
"""
        return {'respuesta': answer}