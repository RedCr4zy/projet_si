# -*- coding: utf-8 -*-

import asyncio
import json
from aiohttp import web

try:
    from grove.adc import ADC
    GROVE_AVAILABLE = True
except ImportError:
    print("Module Grove non trouvé. Le capteur sera désactivé.")
    GROVE_AVAILABLE = False

print("Serveur Python demarre")

CLIENTS = set()

# ---------- WebSocket ----------
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    CLIENTS.add(ws)
    print("Client WebSocket connecté")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data.get("type") == "button":
                print("Bouton cliqué depuis la page web")

    CLIENTS.discard(ws)
    print("Client WebSocket déconnecté")
    return ws

# ---------- Boucle capteur ----------
async def sensor_loop(app):
    if not GROVE_AVAILABLE:
        print("Grove non disponible : lecture capteur désactivée")
        return

    try:
        adc = ADC()  # Initialisation du capteur dans la tâche async
        print("Capteur ADC initialisé")
    except Exception as e:
        print("Impossible d'initialiser ADC :", e)
        return

    while True:
        try:
            value = adc.read(0)  # A0
            message = json.dumps({"type": "sensor", "value": value})

            for ws in list(CLIENTS):
                if not ws.closed:
                    await ws.send_str(message)
        except Exception as e:
            print("Erreur lecture capteur :", e)

        await asyncio.sleep(0.1)  # 10 Hz

# ---------- Démarrage et arrêt des tâches ----------
async def start_background_tasks(app):
    app["sensor_task"] = asyncio.create_task(sensor_loop(app))

async def cleanup_background_tasks(app):
    task = app.get("sensor_task")
    if task:
        task.cancel()
        await task

# ---------- Application ----------
app = web.Application()
app.router.add_get("/ws", ws_handler)
app.router.add_static("/", path="html", show_index=True)

app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

web.run_app(app, host="0.0.0.0", port=8000)
