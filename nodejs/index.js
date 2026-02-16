const fs = require('fs');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({
    authStrategy: new LocalAuth(),
    webVersionCache: {
        type: 'none'
    }
});

console.log('🚀 Iniciando bot de WhatsApp...');

// Cargar developers
// Ejemplo de secrets.json:
// {
//     "developers": [
//         "X@c.us",
//         "Y@c.us"
//     ]
// }
let DEVELOPERS = [];
try {
    const data = JSON.parse(fs.readFileSync('./secrets.json', 'utf8'));
    DEVELOPERS = data.developers || [];
    console.log('✅ Lista de desarrolladores actualizada.');
} catch (err) {
    console.log(`❌ No se pudo cargar secrets.json: ${err.message}`);
    DEVELOPERS = [
        "X@c.us",
    ]
}

client.on('qr', qr => {
    console.log("📷 Vincular un dispositivo nuevo con este QR:");
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ WhatsApp conectado');
    // 🚀 Iniciar loop diario de servicios
    startDailyLoops();
});

// Mensajes entrantes:
client.on('message', async msg => {
    try {
        // Filtros de mensajes
        if (
            msg.from.includes('status') ||
            msg.from.includes('@g.us') ||
            !msg.body || msg.from === msg.body || // Mensajes de estados de chat
            !msg.timestamp || msg.timestamp < 1600000000 // Mensajes viejos
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
        const history = lastMessages.map(m => ({
            fromMe: m.fromMe,
            timestamp: m.timestamp,
            body: m.body
        }));
        lastMessages = null;

        const response = await axios.post('http://localhost:5000/responder', {
            message: msg.body,
            number: msg.from,
            messageHistory: history
        });

        if (response.data?.respuesta) {
            await client.sendMessage(msg.from, response.data.respuesta);
            console.log(`📨 Respondido a +${msg.from}`);
        }

    } catch (err) {
        console.log('❌ Error mensaje:', err.message);
    }
});

// 🔄 Loops
function startDailyLoops() {
    const TWO_HOURS = 2 * 60 * 60 * 1000;
    sendCRM();
    setInterval(sendCRM, TWO_HOURS);

    const ONE_DAY_MS = 24 * 60 * 60 * 1000;
    sendDailyStatus();
    setInterval(sendDailyStatus, ONE_DAY_MS);
}

// 📊 DailyStatus — Envía datos instantaneos del programa.
async function sendDailyStatus() {
    for (const dev of DEVELOPERS) {
        try {
            const response = await axios.post('http://localhost:5000/status', {
                contact_name: 'Reporte automático',
                msg_timestamp: Date.now() / 1000
            });
            const respuesta = response.data.respuesta;
            if (respuesta) {
                await client.sendMessage(dev, respuesta);
                console.log(`📊 Status diario enviado a ${dev}`);
            }
        } catch (err) {
            console.log(`❌ Error al enviar status a ${dev}: ${err.message}`);
        }
    }
}

// 📊 CRM — ENVÍA TODO EL HISTORIAL
async function sendCRM() {
    try {
        const chats = await client.getChats();
        const crmChats = [];

        for (const chat of chats) {
            try {
                const messages = await chat.fetchMessages({ limit: 500 });
                crmChats.push({
                    chatId: chat.id._serialized,
                    name: chat.name || null,
                    isGroup: chat.isGroup,
                    isReadOnly: chat.isReadOnly,
                    messages: messages.map(m => ({
                        fromMe: m.fromMe,
                        timestamp: m.timestamp,
                        body: m.body || ""
                    }))
                });
            } catch (error) {
                console.log(`❌ Error al procesar chat ${chat.name || 'Sin nombre'} (${chat.id._serialized}): ${error.message} | Archivado: ${chat.isReadOnly}`);
            }
            // Delay to prevent detached frame / overload
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        await axios.post('http://localhost:5000/crm', { chats: crmChats });
        console.log(`📊 CRM actualizado (${crmChats.length} chats)`);

    } catch (err) {
        console.log('❌ Error Global CRM:', err.message);
    }
}

// Manejo de cierre
function shutdown() {
    console.log('🛑 Señal de salida recibida, cerrando cliente de WhatsApp...');
    client.destroy();
    console.log('✅ Cliente de WhatsApp cerrado. Saliendo...');
    process.exit(0);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

client.initialize();
