"""
import asyncio
from aiohttp import web
import json
import random

CLIENTS = set()
print('Script launched')

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
app.router.add_static('/', path='html', show_index=True)

app.on_startup.append(lambda app: asyncio.create_task(send_sensor_values(app)))

web.run_app(app, host='0.0.0.0', port=8000)
"""

from aiohttp import web
import asyncio

print(">>> server.py démarre")

async def hello(request):
    print("Nouvelle connection")
    return web.Response(text="Serveur OK")

app = web.Application()
app.router.add_get('/', hello)

print(">>> Lancement du serveur sur le port 8000")
web.run_app(app, host='0.0.0.0', port=8000)
