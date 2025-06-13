
const fs = require('fs');
const { Client, MessageMedia, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const WAWebJS = require('whatsapp-web.js');
const TESTING = false;
const version = '1.1.4';
const client = new Client({
    authStrategy: new LocalAuth()
});

function log(msg) {
    const timestamp = new Date().toLocaleString('es-AR');
    console.log(`[${timestamp}] ${msg}`);
}

log(`bot.js | 👨🏼‍💻 version: ${version}`);

client.on('qr', qr => {
    log("📷 Vincular un dispositivo nuevo con este QR:");
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    log('✅ Cliente de WhatsApp en ejecución!');
});

client.on('message', async msg => {
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

    if (msg.from.includes('status')) return;
    if (msg.from.includes('@g.us')) return;
    if (contact.isMyContact && !TESTING) {
        log(`✔️ Filtrado: Contacto guardado en +${msg.from}`);
        return;
    }
    if (!msg.timestamp || msg.timestamp < 1600000000) {
        log(`⌛ Filtrado: Mensaje viejo de +${msg.from}`);
        return;
    }
    if (hoursDiff > 24) {
        log(`⌛ Filtrado: Mensaje con más de 24 hs de +${msg.from}`);
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
