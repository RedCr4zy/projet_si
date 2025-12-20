import asyncio
from aiohttp import web
import json
import random

CLIENTS = set()
print('Script lancé')

# ---------- WEBSOCKET ----------
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    CLIENTS.add(ws)
    print("Client WebSocket connecté")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            print("Reçu du navigateur :", data)

    CLIENTS.remove(ws)
    print("Client WebSocket déconnecté")
    return ws

async def send_sensor_values(app):
    while True:
        value = random.randint(0, 1023)  # capteur simulé
        message = json.dumps({
            "type": "sensor",
            "value": value
        })

        for ws in CLIENTS:
            await ws.send_str(message)

        await asyncio.sleep(0.2)

# ---------- HTTP ----------
app = web.Application()
app.router.add_get('/ws', ws_handler)
# Sert tout le contenu du dossier html, index.html par défaut
app.router.add_static('/', path='html', show_index=True)

# Lance la boucle pour envoyer les valeurs du capteur
app.on_startup.append(lambda app: asyncio.create_task(send_sensor_values(app)))

# Démarrage du serveur
web.run_app(app, host='0.0.0.0', port=8080)
