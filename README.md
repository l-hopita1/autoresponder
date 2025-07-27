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
    - Para verificar instalación ejecutar:
      ```bash
      git --version
      ```
- [Python 3.8+](https://www.python.org/downloads/)
    - Para verificar instalación ejecutar:
      ```bash
      python --version
      ```
- [Node.js 16+](https://nodejs.org/es/)
    - Para verificar instalación ejecutar:
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
   npm audit fix --force
   ```

---

## 🚀 Ejecución del programa

- **Hacer doble click en el archivo RUN.bat**, verifica que se abran las siguientes tres ventanas de terminales de Windows PowerShell:
  1. La primer ventana ejecuta el backend y el bot de whatsapp.
  2. La segunda ventana que crea las respuestas de whatsapp.
  3. La tercer y última ventana que recive y envía mensajes de whatsapp al backend.
## 🔒 Cerrar el programa

1. **Abrir la primer consola (whatsapp web js)**, apretar la siguiente combinación de teclas **CTRL**+ **C**.
2. **Abrir la segunda consola (código backend)**, apretar la siguiente combinación de teclas **CTRL**+ **C**.
> Revisar en la terminal un mensaje afirmando que se guardaron los datos de los contactos.

---

## 🧾 Historial de Cambios

Consultá el archivo [CHANGELOG](CHANGELOG) para ver el historial completo de versiones.

---

## 🔮 Próximas versiones
### 1.3.X
- Almacenamiento en *Google Sheet* del estado del cliente:
  - Número de celular
  - Cantidad de interacciones
  - Último estado del menú
  - Última fecha de interacción
### 1.4.X
- Seguimiento automático por inactividad con reintentos configurables.
### 1.5.X
- Seguimiento personalizado en base al último mensaje enviado.
### 1.6.X
- Métricas avanzadas por cliente:
  - Cantidad de consultas
  - Monto estimado de compra
  - Nivel de interés calculado
### 1.7.X
- Seguimiento de etapas de venta por cliente e instalación.
### 1.8.X
- Gestión avanzada de oportunidades comerciales.

---

## 🙌 Agradecimientos

- [whatsapp-web.js](https://wwebjs.dev/): Librería base para el control de WhatsApp Web vía código.