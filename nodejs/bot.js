const fs = require('fs');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({
    authStrategy: new LocalAuth()
});

console.log('🚀 Iniciando bot de WhatsApp...');

// Cargar lista de desarrolladores desde secrets.json
let DEVELOPERS = [];
try {
    const devData = JSON.parse(fs.readFileSync('./secrets.json', 'utf8'));
    DEVELOPERS = devData.developers || [];
    console.log('✅ Lista de desarrolladores actualizada.');
} catch (err) {
    console.log(`❌ No se pudo cargar secrets.json: ${err.message}`);
}

client.on('qr', qr => {
    console.log("📷 Vincular un dispositivo nuevo con este QR:");
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ Cliente de WhatsApp en ejecución!');
});

client.on('message', async msg => {
    try {
        if (
            msg.from.includes('status') ||
            msg.from.includes('@g.us') ||
            msg.from === msg.body ||
            !msg.timestamp || msg.timestamp < 1600000000
        ) return;

        const messageDate = new Date(msg.timestamp * 1000);
        const hoursDiff = (Date.now() - messageDate.getTime()) / 36e5;
        if (hoursDiff > 24) return;

        const contact = await msg.getContact();
        if (contact.isMyContact) {
            if (DEVELOPERS.includes(msg.from) && msg.body.includes('Status')) {
                console.log(`🤖 ${contact.name || msg.from} preguntó por el estado del programa.`);
                const response = await axios.post('http://localhost:5000/status', {
                    contact_name: contact.name || 'Usuario',
                    msg_timestamp: msg.timestamp
                });
                const respuesta = response.data.respuesta;
                if (respuesta) {
                    await client.sendMessage(msg.from, respuesta);
                    console.log(`🤖 Se le respondió a ${contact.name || msg.from}.`);
                }
                return;
            } else { 
                console.log(`🛡️ Filtrado: ${contact.name || msg.from} es un contacto guardado`);
                return;
            }    
        }

        const chat = await msg.getChat();
        let lastMessages = await chat.fetchMessages({ limit: 20 });
        const messageHistory = lastMessages.map(m => ({
            fromMe: m.fromMe,
            timestamp: m.timestamp,
            body: m.body
        }));
        lastMessages = null;

        const response = await axios.post('http://localhost:5000/responder', {
            message: msg.body,
            number: msg.from,
            messageHistory
        });

        const respuesta = response.data.respuesta;
        if (respuesta) {
            await client.sendMessage(msg.from, respuesta);
            console.log(`📨 Respondido a +${msg.from}`);
        }

    } catch (error) {
        console.log(`❌ Error al procesar mensaje: ${error.message}`);
    }
});

// Manejo de cierre
function shutdown() {
    console.log('🛑 Señal de salida recibida, cerrando cliente de WhatsApp...');
    client.destroy();
    console.log('✅ Cliente de WhatsApp cerrado. Saliendo...');
    process.exit(0);
}

// Capturar Ctrl+C
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

client.initialize();
