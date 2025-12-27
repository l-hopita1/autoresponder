# Import class:
from datetime import datetime
from logging import Logger



class workerClass():
    def __init__(self, logger: Logger):
        self.logger = logger
        self._config = {}
    
    def init(self, config: dict):
        self._config = config

    async def run(self):
        raise NotImplementedError("run() debe implementarse en el worker hijo")
    
    def current_time_str(self):
        return f"[{datetime.now():%d/%m/%Y %H:%M:%S}]"
    
    def normalize(self, text:str)->str:
        return ' '.join(text.strip().lower().split())