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

    // 🚀 Iniciar loop diario de status
    startDailyStatusLoop();
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

// --- 🔄 Loop diario de status ---
function startDailyStatusLoop() {
    const ONE_DAY_MS = 24 * 60 * 60 * 1000;
    const TWO_HOUR_MS = 2 * 60 * 60 * 1000;

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

    async function sendCRM() {
        try {
            const chats = await client.getChats();
            const crmChats = [];

            for (const chat of chats) {

                // Evitar estados, grupos y chats de whatsapp.
                if (chat.id._serialized.includes('status') || chat.isReadOnly || chat.isGroup) continue;

                // Obtener TODO el historial posible del chat
                const messages = await chat.fetchMessages({ limit: 5000 }); // máximo permitido por WhatsApp-Web.js

                const formattedMessages = messages.map(m => ({
                    id: m.id._serialized,
                    fromMe: m.fromMe,
                    author: m.author || null,
                    timestamp: m.timestamp,
                    body: m.body || "",
                    type: m.type
                }));

                crmChats.push({
                    chatId: chat.id._serialized,
                    name: chat.name || chat.formattedTitle || "Sin nombre",
                    isGroup: chat.isGroup,
                    messages: formattedMessages
                });
            }
            // Enviar TODO al CRM
            const response = await axios.post("http://localhost:5000/crm", {
                chats: crmChats
            });

            if (response.data.success) {
                console.log(`📊 CRM actualizado con ${crmChats.length} chats (historial completo enviado).`);
            } else {
                console.log("⚠️ CRM respondió sin éxito.");
            }

        } catch (err) {
            console.log(`❌ Error al enviar CRM: ${err.message}`);
        }
    }


    // Primera ejecución inmediata al arrancar
    sendDailyStatus();
    sendCRM();

    // Ejecución periódica
    setInterval(sendDailyStatus, ONE_DAY_MS);
    setInterval(sendCRM, TWO_HOUR_MS);
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
