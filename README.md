# 🤖 Autoresponder de Calares

**Sistema gratuito y modular de autorespuesta para WhatsApp**, ideal para automatizar el primer contacto con potenciales clientes.

---

## 📋 Requisitos

### 🖥️ Hardware
- RAM mínima recomendada: **1 GB**
- Espacio libre en disco: **100 MB**
- Conexión a Internet: **estable y continua**

### 💻 Software necesario

- [Git](https://git-scm.com/downloads/)
    - Verificar instalación:
      ```bash
      git --version
      ```
- [Python 3.8+](https://www.python.org/downloads/)
    - Verificar instalación:
      ```bash
      python --version
      ```
- [Node.js 16+](https://nodejs.org/es/)
    - Verificar instalación:
      ```bash
      node --version
      ```

---

## ⚙️ Instalación

1. **Abrí una consola de comandos** (Command Prompt o Terminal).
2. **Cloná el repositorio** en tu directorio de trabajo:
   ```bash
   cd "Calares/Gestion del cliente"
   git clone https://github.com/l-hopita1/autoresponder.git
   cd autoresponder/
   ```
3. **Instalá los paquetes de Python**:
   ```bash
   python -m pip install -r python_backend/requirements.txt
   ```
4. **Instalá las dependencias de Node.js**:
   ```bash
   cd nodejs
   npm install
   ```

---

## 🚀 Ejecución del programa

1. **Abrí una consola nueva**, navegá al proyecto y ejecutá el bot de WhatsApp:
   ```bash
   cd "Calares/Gestion del cliente/autoresponder"
   node nodejs/bot.js
   ```
   > Escaneá el código QR desde el celular para vincular tu cuenta de WhatsApp.

2. **En otra consola**, ejecutá el servidor backend de Python:
   ```bash
   cd "Calares/Gestion del cliente/autoresponder"
   python python_backend/app.py
   ```

---

## 🧾 Historial de Cambios

Consultá el archivo [CHANGELOG](CHANGELOG) para ver el historial completo de versiones.

---

## 🔮 Próximas versiones

### ✅ 1.1.0
- Estadísticas sincronizadas con Google Sheets:
  - Número de celular
  - Cantidad de interacciones
  - Último estado del menú
  - Última fecha de interacción

### ⏳ 1.2.0
- Seguimiento automático por inactividad con reintentos configurables.

### ✉️ 1.3.0
- Seguimiento personalizado en base al último mensaje enviado.

### 📊 2.0.0
- Métricas avanzadas por cliente:
  - Cantidad de consultas
  - Monto estimado de compra
  - Nivel de interés calculado

### 📈 3.0.0
- Seguimiento de etapas de venta por cliente e instalación.
- Gestión avanzada de oportunidades comerciales.

---

## 🙌 Agradecimientos

- [whatsapp-web.js](https://wwebjs.dev/): Librería base para el control de WhatsApp Web vía código.