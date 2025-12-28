const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

console.log('==============================');
console.log('🧪 TEST_NODE — whatsapp-web.js');
console.log('==============================');

process.on('unhandledRejection', err => {
    console.error('❌ UNHANDLED REJECTION:', err);
});

process.on('uncaughtException', err => {
    console.error('❌ UNCAUGHT EXCEPTION:', err);
});

const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "test-node"
    }),
    webVersionCache: {
        type: 'none'
    },
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    }
});

client.on('qr', qr => {
    console.log('📷 EVENT_QR');
    qrcode.generate(qr, { small: true });
});

client.on('authenticated', () => {
    console.log('🔐 EVENT_AUTHENTICATED');
});

client.on('auth_failure', msg => {
    console.error('❌ EVENT_AUTH_FAILURE:', msg);
});

client.on('loading_screen', (percent, message) => {
    console.log(`⏳ LOADING ${percent}% — ${message}`);
});

client.on('ready', async () => {
    console.log('✅ EVENT_READY');
    console.log('EVENT_READY'); // ← NO BORRAR (lo usa test_node.py)

    const info = client.info;
    console.log('📱 WhatsApp info:', {
        wid: info.wid?._serialized,
        platform: info.platform,
        pushname: info.pushname
    });

    // Mantener vivo 10s y salir limpio
    setTimeout(async () => {
        console.log('🧹 Cerrando cliente...');
        await client.destroy();
        console.log('👋 FIN TEST_NODE');
        process.exit(0);
    }, 10000);
});

client.on('disconnected', reason => {
    console.error('🔌 EVENT_DISCONNECTED:', reason);
});

console.log('🚀 Inicializando cliente...');
client.initialize();
