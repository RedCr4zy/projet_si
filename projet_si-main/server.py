# -*- coding: utf-8 -*-

import asyncio
import json
from aiohttp import web

# ---------- Modules matériels ----------
try:
    from grove.adc import ADC
    GROVE_AVAILABLE = True
except ImportError:
    print("Module Grove non trouvé. Capteur désactivé.")
    GROVE_AVAILABLE = False

try:
    from inputs import get_gamepad
    JOYSTICK_AVAILABLE = True
except ImportError:
    print("Module inputs non trouvé. Joystick désactivé.")
    JOYSTICK_AVAILABLE = False

print("Serveur Python démarre")

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
                print("Bouton cliqué depuis le web")

    CLIENTS.discard(ws)
    print("Client WebSocket déconnecté")
    return ws

# ---------- Boucle potentiomètre ----------
async def sensor_loop(app):
    if not GROVE_AVAILABLE:
        print("Grove non disponible : lecture capteur désactivée")
        return

    try:
        adc = ADC()  # Initialisation dans la tâche async
        print("Capteur ADC initialisé")
    except Exception as e:
        print("Impossible d'initialiser ADC :", e)
        return

    while True:
        try:
            value = adc.read(0)
            msg = json.dumps({"type": "sensor", "value": value})
            for ws in list(CLIENTS):
                if not ws.closed:
                    await ws.send_str(msg)
        except Exception as e:
            print("Erreur lecture capteur :", e)
        await asyncio.sleep(0.1)  # 10 Hz

# ---------- Boucle joystick ----------
async def joystick_loop(app):
    if not JOYSTICK_AVAILABLE:
        print("Joystick non disponible")
        return

    print("Joystick actif")
    while True:
        try:
            events = get_gamepad()
            for e in events:
                msg = json.dumps({
                    "type": "joystick",
                    "ev_type": e.ev_type,
                    "code": e.code,
                    "state": e.state
                })
                for ws in list(CLIENTS):
                    if not ws.closed:
                        await ws.send_str(msg)
        except Exception as e:
            print("Erreur joystick :", e)
        await asyncio.sleep(0.01)  # 100 Hz

# ---------- Redirection racine ----------
async def redirect_root(request):
    raise web.HTTPFound('/index.html')

# ---------- Démarrage / arrêt tâches ----------
async def start_background_tasks(app):
    app["sensor_task"] = asyncio.create_task(sensor_loop(app))
    app["joystick_task"] = asyncio.create_task(joystick_loop(app))

async def cleanup_background_tasks(app):
    for task_name in ["sensor_task", "joystick_task"]:
        task = app.get(task_name)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

# ---------- Application ----------
app = web.Application()
app.router.add_get("/", redirect_root)
app.router.add_get("/ws", ws_handler)
app.router.add_static("/", path="html", show_index=True)
print("Test")

app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

web.run_app(app, host="0.0.0.0", port=8000)
