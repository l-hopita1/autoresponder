MENU = {
    'root': {
        'message': """🌍💚 ¡Hola! ¡Muchas gracias por contactarnos! Puedo ayudarte en forma automática o podés solicitar la atención de nuestros asesores.

Ingresá el número y hablemos:
1. 💡 Paneles fotovoltaicos para electricidad y baterías
2. 🏊‍♂ Climatización de pileta
3. 🚿 Termotanques solares
4. ❄ Bomba de calor (aerotermia) para climatización del hogar
5. 🛠 Mantenimiento y reparaciones en general, herrería, electricidad, pintura, sanitarios
6. 👤 Chatear con un asesor. Atención a empresas
""",
        'options': {
            '1': 'menu_1',
            '2': 'menu_2',
            '3': 'menu_3',
            '4': 'menu_4',
            '5': 'menu_5',
            '6': 'menu_6'
        }
    },
    "menu_1": {
        "message": """Seleccione el número de la opción deseada 
✅ Si querés un presupuesto instantáneo de paneles de electricidad y/o baterías, completá este formulario: 
https://calaresenergiasrenovables.com/cotizate.php

Sino, adelantamos por favor lo siguiente:
1. Mi objetivo es ahorrar en la factura
2. Mi objetivo es tener backup eléctrico ante corte y baja tensión (como un generador)
3. Quiero ahorrar y además tener Backup ante corte y baja tension
4. Estoy en una zona sin servicio eléctrico
0. Menú Principal""",
        "options": {
            "1": "menu_1_1",
            "2": "menu_1_2",
            "3": "menu_1_3",
            "4": "menu_1_4",
            "0": "root"
        },
        "back": "root"
    },
    "menu_1_1":{
        "message":"""Seleccione el número de la opción deseada 
Un asesor se contactará contigo. mientras, adelantamos por favor si tu instalación es  trifásica o monofásico. 
¿Estás en etapa de construcción o ya está construido?
¿Qué tipo de techo es?
¿En qué localidad?
9. Menú Anterior
0. Menú Principal""",
        "options":{
            "9": "menu_1",
            "0": "root"
        }
    },
    'menu_2': {
        'message': """Seleccione el número de la opción deseada 
Vas a poder disfrutar a una temperatura ideal, extendiendo la temporada de forma ecológica y económica.
⌨ Por favor escribí el número ( 1 / 2 / 0) de la opción que elijas:
1. ❓ Ver respuestas a preguntas frecuentes
2. 📝 Solicitar un presupuesto.
0. Menú Principal""",
        "options": {
            "1": "menu_2_1",
            "2": "menu_2_2",
            "0": "root"
        },
    },
    "menu_2_1":{
        "message":"""Seleccione el número de la opción deseada 
❓ Para ver un listado de las principales preguntas y respuestas, entrá en www.calaresenergiasrenovables.com/dudas/#piscinas
📧 Si aún necesitás nuestro asesoramiento, escribinos tu consulta por aquí o a info@calaresenergiasrenovables.com 
⌨ Por favor escribí el número de la opción que elijas ( 9 / 0 )
9. Menú Anterior
0. Menú Principal""",
        "options": {
            "9": "menu_2",
            "0": "root"
        }
    },
    'menu_3': {
        'message': "🚿 Termotanques solares: eficiencia energética para agua caliente sanitaria. Enviá 0 para volver.",
        'options': {}
    },
    'menu_4': {
        'message': "❄ Bomba de calor: climatización eficiente con energía renovable. Enviá 0 para volver.",
        'options': {}
    },
    'menu_5': {
        'message': "🛠 Mantenimiento y reparaciones: ofrecemos herrería, pintura, electricidad, sanitarios, etc. Enviá 0 para volver.",
        'options': {}
    },
    'menu_6': {
        'message': "👤 Un asesor se contactará con vos a la brevedad. Enviá 0 para volver.",
        'options': {}
    }
}
