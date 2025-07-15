import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
version = '1.0.0'

# Definimos el scope para Sheets y Drive
scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Autenticación
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes)
client = gspread.authorize(credentials)
print("Autentificación exitosa")

# Abrimos el Google Sheet por URL
url = "https://docs.google.com/spreadsheets/d/12E24sqkNvhLOa9_-_DPiceVm9wdFni6Ql_SMQwcTgqE/edit?gid=0#gid=0"
spreadsheet = client.open_by_url(url)
print("Google spreadsheet obtenida exitosamente")

# Abrimos la hoja (pestaña) por título
print(f'lista de hojas disponibles: {spreadsheet.worksheets()}')
sheet = spreadsheet.worksheet("Base de datos automática")
print("Hoja de cálculo obtenida exitosamente")

# --- Leer datos ---
data = sheet.get_all_values()
print("Datos de hoja de cálculo obtenidos exitosamente")

print("Datos originales:")
for fila in data:
    print(fila)

# --- Procesar datos ---
header = data[0]
rows = data[1:]

if "Número" in header:
    idx_number = header.index("Número")
else:
    idx_number = None

header.append("Número ARG")

for row in rows:
    if idx_number is not None and row[idx_number].isdigit():
        nueva_edad = "+54" + row[idx_number]
    else:
        nueva_edad = ""
    row.append(nueva_edad)

new_data = [header] + rows

# --- Subir datos nuevos ---
sheet.clear()
sheet.update('A1', new_data)

print("Datos actualizados en la hoja.")
