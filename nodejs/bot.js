const fs = require('fs');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({
    authStrategy: new LocalAuth()
});

function log(msg) {
    const timestamp = new Date().toLocaleString('es-AR', {
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    console.log(`[${timestamp}] ${msg}`);
}

log('🚀 Iniciando bot de WhatsApp...');

// Cargar lista de desarrolladores desde secrets.json
let DEVELOPERS = [];
try {
    const devData = JSON.parse(fs.readFileSync('./secrets.json', 'utf8'));
    DEVELOPERS = devData.developers || [];
    log('✅ Lista de desarrolladores actualizada.');
} catch (err) {
    log(`❌ No se pudo cargar developers.json: ${err.message}`);
}

client.on('qr', qr => {
    log("📷 Vincular un dispositivo nuevo con este QR:");
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    log('✅ Cliente de WhatsApp en ejecución!');
});

client.on('message', async msg => {
    try {
        // Filtros tempranos
        if (
            msg.from.includes('status') ||
            msg.from.includes('@g.us') ||
            msg.from === msg.body ||
            !msg.timestamp || msg.timestamp < 1600000000
        ) return;

        const messageDate = new Date(msg.timestamp * 1000);
        const hoursDiff = (Date.now() - messageDate.getTime()) / 36e5;
        if (hoursDiff > 24) return;

        // Obtener contacto:
        const contact = await msg.getContact();
        if (contact.isMyContact) {
            // Si es un desarrollador y quiere consultar el estado
            if (DEVELOPERS.includes(msg.from) && msg.body.includes('Status')) {
                const response = await axios.post('http://localhost:5000/status', {
                    contact_name: contact.name || 'Usuario',
                    msg_timestamp: msg.timestamp
                });
                const respuesta = response.data.respuesta;
                if (respuesta) {
                    await client.sendMessage(msg.from, respuesta);
                    log(`🤖 ${contact.name || msg.from} preguntó por el estado del programa.`);
                }
                return;
            }
            // Es un contacto guardado, no responder.
            else { 
                log(`🛡️ Filtrado: ${contact.name || msg.from} es un contacto guardado`);
                return;
            }    
        }
        log(`📩 Mensaje de +${msg.from}`)
        // Obtener historial reciente del chat
        const chat = await msg.getChat();
        let lastMessages = await chat.fetchMessages({ limit: 20 }); // Limitar para ahorrar RAM
        const messageHistory = lastMessages.map(m => ({
            fromMe: m.fromMe,
            timestamp: m.timestamp,
            body: m.body
        }));
        lastMessages = null; // liberar explícitamente

        // Llamar al backend Flask
        const response = await axios.post('http://localhost:5000/responder', {
            message: msg.body,
            number: msg.from,
            messageHistory
        });

        const respuesta = response.data.respuesta;
        if (respuesta) {
            await client.sendMessage(msg.from, respuesta);
            log(`📨 Respondido a +${msg.from}`);
        }

    } catch (error) {
        log(`❌ Error al procesar mensaje: ${error.message}`);
    }
});

client.initialize();
