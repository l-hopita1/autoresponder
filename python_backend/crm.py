# Import modules:
import gspread
# Import Class
from logging import Logger
from .worker_class import workerClass
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

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
        self._spreadsheet_url       = None
        self._worksheet_name        = None
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

    def handle_crm(self):
        self._spreadsheet_url = self._config.get('spreadsheet_url')
        self._worksheet_name = self._config.get('worksheet_name','crm')

        # Obtengo los datos de la hoja de cálculo
        data = self._get_worksheet_data(self._spreadsheet_url, self._worksheet_name)
        if not data:
            self.logger.warning("La hoja está vacía")
            return
        else:
            self.logger.debug(f'{self.__class__.__name__} | handle_crm | Datos de hoja de cálculo obtenidos exitosamente')

        print("Datos originales:")
        for fila in data:
            print(fila)

        # --- Procesar datos ---
        header = data[0]
        rows = data[1:]

        idx_number = header.index("Número") if "Número" in header else None
        header.append("Número ARG")

        for row in rows:
            if idx_number is not None and row[idx_number].isdigit():
                row.append("+54" + row[idx_number])
            else:
                row.append("")

        self._set_worksheet_data(
            self._spreadsheet_url,
            self._worksheet_name,
            [header] + rows
        )

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