
const fs = require('fs');
const { Client, MessageMedia, LocalAuth, Buttons, List } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const WAWebJS = require('whatsapp-web.js');
const TESTING = true;
const version = '1.1.6';


const client = new Client({
    authStrategy: new LocalAuth()
});

function log(msg) {
    const timestamp = new Date().toLocaleString('es-AR', {
        hour12: false,  // 👈 Esto desactiva AM/PM
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    console.log(`[${timestamp}] ${msg}`);
}

client.on('qr', qr => {
    log("📷 Vincular un dispositivo nuevo con este QR:");
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    log('✅ Cliente de WhatsApp en ejecución!');
});

client.on('message', async msg => {
    
    // Datos del mensaje enviado:
    const contact = await msg.getContact();
    const chat = await msg.getChat();
    const messageDate = new Date(msg.timestamp * 1000);
    const hoursDiff = (Date.now() - messageDate.getTime()) / 36e5;
    const lastMessages = await chat.fetchMessages({ limit: 50 });
    const messageHistory = lastMessages.map(m => ({
        fromMe: m.fromMe,
        timestamp: m.timestamp,
        body: m.body
    }));
    
    // Filtro mensajes no deseados:
    if (msg.from.includes('status')) return;
    if (msg.from.includes('@g.us')) return;
    if (contact.isMyContact && !TESTING) {
        contact.name
        log(`🛡️ Filtrado: ${contact.name} es un contacto guardado`);
        return;
    }
    if (!msg.timestamp || msg.timestamp < 1600000000) {
        log(`🛡️ Filtrado: Mensaje viejo de +${msg.from}`);
        return;
    }
    if (hoursDiff > 24) {
        log(`🛡️ Filtrado: Mensaje con más de 24 hs de +${msg.from}`);
        return;
    }
    if (msg.from == msg.body) {
        log(`🛡️ Filtrado: Notificación de cifrado con +${msg.from}`);
        return;
    }

    log(`📩 Mensaje de +${msg.from}: ${msg.body}`);
    try {
        const response = await axios.post('http://localhost:5000/responder', {
            message: msg.body,
            number: msg.from,
            messageHistory: messageHistory
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const respuesta = response.data.respuesta;
        if (respuesta) {
            client.sendMessage(msg.from, respuesta);
            log(`📨 Respondido a +${msg.from}`);
        }
    } catch (error) {
        log(`❌ Error al consultar el backend: ${error.message}`);
    }
});


client.initialize();
