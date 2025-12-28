# Import modules:
import gspread
# Import Class
from pathlib import Path
from logging import Logger
from datetime import datetime
from worker_class import workerClass
from oauth2client.service_account import ServiceAccountCredentials

BASE_DIR = Path(__file__).resolve().parent



class crmWorker(workerClass):
    _scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

    def __init__(self, logger: Logger):
        super().__init__(logger)
        self._client                = None
        self._credentials_filename  = None

    def init(self, config: dict):
        # Guardo la configuración
        self._config = config

        # Autenticación
        credentials_path = config.get("credentials_path")
        if not credentials_path:
            raise ValueError("crmWorker | init | credentials_path no definido en config")
        credentials_path = Path(credentials_path)
        if not credentials_path.is_absolute():
            credentials_path = BASE_DIR / credentials_path
        self._credentials_filename = credentials_path
        if not self._credentials_filename.exists():
            raise FileNotFoundError(
                f"Archivo de credenciales no encontrado: {self._credentials_filename}"
            )
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            str(self._credentials_filename),
            self._scopes
            )
        self._client = gspread.authorize(credentials)
        self.logger.debug(f'{self.__class__.__name__} | init | Credenciales de Google verificadas')
        self.logger.info(f'{self.__class__.__name__} | init | ✅ Inicializado correctamente.')

    def handle_crm(self, payload: dict):
        # Check inputs:
        chats = payload.get("chats", [])
        if not chats:
            self.logger.warning(f'{self.__class__.__name__} | handle_crm | No se recibieron chats')
            return

        # Get configuration:
        keywords = self._config.get("keywords", [])
        dry_run = self._config.get("dry_run", False)
        spreadsheet_url = self._config.get("spreadsheet_url")
        worksheet_name = self._config.get("worksheet_name", "crm")

        rows = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 
        for chat in chats:
            if not self._filter_chat(chat):
                continue

            stats = self._analyze_chat(chat, keywords)

            row = [
                stats["chat_id"],
                stats["name"],
                stats["my_messages"],
                stats["client_messages"],
                stats["last_my_message"],
                stats["last_client_message"],
            ]

            # keywords (míos / cliente)
            for k in keywords:
                row.append(stats["my_keywords"][k])
                row.append(stats["client_keywords"][k])

            row.append(now_str)
            rows.append(row)

        if not rows:
            self.logger.warning(f'{self.__class__.__name__} | handle_crm | No hay filas para escribir')
            return

        # Header dinámico
        header = [
            "chat_id",
            "name",
            "my_messages",
            "client_messages",
            "last_my_message",
            "last_client_message",
        ]

        for k in keywords:
            header.append(f"kw_{k}_my")
            header.append(f"kw_{k}_client")

        header.append("last_crm_update")

        data = [header] + rows

        if dry_run:
            self.logger.info(f'{self.__class__.__name__} | handle_crm | DRY RUN | {len(rows)} filas procesadas')
            return

        self._set_worksheet_data(
            spreadsheet_url,
            worksheet_name,
            data
        )

        self.logger.info(f'{self.__class__.__name__} | handle_crm | CRM actualizado correctamente ({len(rows)} chats)')

    # Private fuctions:

    def _get_worksheet_data(self, url: str, worksheet_name: str)->list[list]:
        # Abrimos el Google Sheet por URL        
        spreadsheet = self._client.open_by_url(url)

        # Abrimos la hoja (pestaña) por título
        sheet = self._get_worksheet_from_spreadsheet(worksheet_name,spreadsheet)
        self.logger.debug(f'{self.__class__.__name__} | _get_worksheet_data | Hoja de cálculo "{worksheet_name}" obtenida exitosamente')

        # Devolvemos los datos
        return sheet.get_all_values()
    

    def _set_worksheet_data(self, url: str, worksheet_name: str, data: list[list]):
        # Abrimos el Google Sheet por URL        
        spreadsheet = self._client.open_by_url(url)

        # Abrimos la hoja (pestaña) por título
        sheet = self._get_worksheet_from_spreadsheet(worksheet_name,spreadsheet)
        
        # Reescribo los datos:
        sheet.clear()
        sheet.update('A1', data)
    
    def _get_worksheet_from_spreadsheet(self, worksheet_name: str,spreadsheet:str):
        titles = [ws.title for ws in spreadsheet.worksheets()]
        if worksheet_name not in titles:
            raise ValueError(
                f'Hoja "{worksheet_name}" no encontrada. Disponibles: {titles}'
            )
        return spreadsheet.worksheet(worksheet_name)
    
    def _filter_chat(self, chat):
        if not self._config.get("include_groups", False) and chat["isGroup"]:
            return False
        if not self._config.get("include_readonly", False) and chat["isReadOnly"]:
            return False
        return True

    def _analyze_chat(self, chat, keywords):
        """
        """
        # Defino las estadísticas a utilizar:
        stats = {
            "chat_id": chat["chatId"],
            "name": chat["name"],
            "my_messages": 0, # Contador de mensajes míos.
            "client_messages": 0, # Contador de mensajes del cliente.
            "last_my_message": None, # Tiempo de mi último mensaje.
            "last_client_message": None, # Tiempo del último mensaje del cliente.
            "my_keywords": {k: 0 for k in keywords}, # Contadores de palabras clave míos.
            "client_keywords": {k: 0 for k in keywords}, # Contadores de palabras clave del cliente.
        }

        # Actualizo los tiempos y los contadores.
        for m in chat["messages"]:
            text = (m["body"] or "").lower()
            ts = m["timestamp"]

            if m["fromMe"]:
                stats["my_messages"] += 1
                stats["last_my_message"] = max(stats["last_my_message"] or 0, ts)
                for k in keywords:
                    stats["my_keywords"][k] += text.count(k)
            else:
                stats["client_messages"] += 1
                stats["last_client_message"] = max(stats["last_client_message"] or 0, ts)
                for k in keywords:
                    stats["client_keywords"][k] += text.count(k)

        return stats