const { Client, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const WAWebJS = require('whatsapp-web.js');

const client = new Client();

function log(msg) {
    const timestamp = new Date().toLocaleString('es-AR');
    console.log(`[${timestamp}] ${msg}`);
}

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    log('✅ Cliente de WhatsApp en ejecución!');
});

client.on('message', async msg => {
    const contact = await msg.getContact();
    const messageDate = new Date(msg.timestamp * 1000);
    const hoursDiff = (Date.now() - messageDate.getTime()) / 36e5;

    // Ignoro mensajes:
    if (msg.from.includes('status')) return;
    if (msg.from.includes('@g.us')) return;
    if (contact.isMyContact) {
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
            mensaje: msg.body,
            numero: msg.from
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

/**
 * @param {import('whatsapp-web.js').Message} msg
 */
async function alreadyReplied(msg) {
    const chat = await msg.getChat();
    const lastMessages = await chat.fetchMessages({ limit: 50 });
    return lastMessages.some(m => {
        if (m.fromMe && m.body) {
            log(`⚠ No se respondió a +${m.from} porque ya se le envió un mensaje el ${new Date(m.timestamp * 1000).toLocaleString()}`);
            return true;
        }
        return false;
    });
}

client.initialize();
log("📷 Vincular un dispositivo nuevo con este QR:");
