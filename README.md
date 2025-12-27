# 🤖 Autoresponder de Calares

**Sistema gratuito, modular y extensible de autorespuesta para WhatsApp**, pensado para automatizar el primer contacto con potenciales clientes y centralizar la gestión inicial de consultas.

Este proyecto combina:
- **Node.js** para la comunicación con WhatsApp Web
- **Python** como backend lógico y de gestión de estados
- Un diseño modular orientado a crecer hacia un CRM liviano

---

## ✨ Características principales

- 📲 Respuestas automáticas por WhatsApp
- 🧠 Lógica de menús configurable
- 🗂️ Gestión de estados por contacto
- 🔌 Arquitectura modular (Node + Python)
- 🆓 100% gratuito y auto-hosteado
- 🧩 Preparado para integración con Google Sheets y CRM

---

## 📋 Requisitos

### 🖥️ Hardware
- **RAM mínima:** 1 GB  
- **Espacio en disco:** 100 MB  
- **Conectividad:** Internet estable y continua

### 💻 Software necesario

- **Git**
  ```bash
  git --version
  ```

- **Python 3.8 o superior**
  ```bash
  python --version
  ```

- **Node.js 16 o superior**
  ```bash
  node --version
  ```

---

## ⚙️ Instalación

1. Abrí una consola de comandos.
2. Cloná el repositorio:
   ```bash
   git clone https://github.com/l-hopita1/autoresponder.git
   cd autoresponder
   ```
3. Instalá las dependencias de Python:
   ```bash
   python -m pip install -r python_backend/requirements.txt
   ```
4. Instalá las dependencias de Node.js:
   ```bash
   cd nodejs
   npm install
   npm audit fix --force
   ```

---

## 🚀 Ejecución del programa (Windows)

Ejecutar `RUN.bat`.  
Se abrirán tres consolas:
1. Backend y bot de WhatsApp
2. Generador de respuestas
3. Comunicación WhatsApp ↔ Backend

Escaneá el QR en la primera ejecución.

---

## 🔒 Cierre seguro del programa

Cerrar las consolas con:
```
CTRL + C
```

Verificar que los datos se guarden correctamente.

---

## 🧾 Historial de cambios

Ver [`CHANGELOG`](CHANGELOG.md).

---

## 🔮 Roadmap

### 🚧 2.1.X
- Integración con Google Sheets
  - Número de celular
  - Cantidad de interacciones
  - Estado del menú
  - Última fecha de contacto
### 🚧 2.2.X
- Seguimiento automático por inactividad
- Reintentos configurables
### 🚧 2.3.X
- Seguimiento personalizado según último mensaje
### 🚧 2.4.X
- Métricas avanzadas por cliente:
- Cantidad de consultas
- Monto estimado de compra
- Nivel de interés calculado
### 🚧 2.5.X
- Pipeline de ventas por cliente
### 🚧 2.6.X
- Gestión avanzada de oportunidades comerciales

---

## 🙌 Agradecimientos
- [whatsapp-web.js](https://wwebjs.dev/)