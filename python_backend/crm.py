# Import modules:
import gspread
# Import Class
from logging import Logger
from .worker_class import workerClass
from oauth2client.service_account import ServiceAccountCredentials



class crmWorker(workerClass):
    _credentials_filename = "credentials.json"
    _scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

    def __init__(self, logger: Logger):
        super().__init__(logger)
        self._client = None
        self._spreadsheet_url = None
        self._worksheet_name = None

    def init(self, config: dict):
        # Guardo la configuración
        self._config = config
        
        # Autenticación
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self._credentials_filename,
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
        self.logger.debug(f'{self.__class__.__name__} | init | Google spreadsheet obtenida exitosamente')

        # Abrimos la hoja (pestaña) por título
        self.logger.debug(f'{self.__class__.__name__} | init | lista de hojas disponibles: {spreadsheet.worksheets()}')
        sheet = spreadsheet.worksheet(worksheet_name)
        self.logger.debug(f'{self.__class__.__name__} | init | Hoja de cálculo "{worksheet_name}"obtenida exitosamente')

        # Devolvemos los datos
        return sheet.get_all_values()
    

    def _set_worksheet_data(self, url: str, worksheet_name: str, data: list[list]):
        # Abrimos el Google Sheet por URL        
        spreadsheet = self._client.open_by_url(url)
        self.logger.debug(f'{self.__class__.__name__} | init | Google spreadsheet obtenida exitosamente')

        # Abrimos la hoja (pestaña) por título
        self.logger.debug(f'{self.__class__.__name__} | init | lista de hojas disponibles: {spreadsheet.worksheets()}')
        sheet = spreadsheet.worksheet(worksheet_name)
        self.logger.debug(f'{self.__class__.__name__} | init | Hoja de cálculo "{worksheet_name}"obtenida exitosamente')
        
        # Reescribo los datos:
        sheet.clear()
        sheet.update('A1', data)