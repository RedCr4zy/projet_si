import asyncio
import json
from aiohttp import web
from grove.adc import ADC

print("Serveur Python démarré")

adc = ADC()
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

            if data["type"] == "button":
                print("👉 Bouton cliqué depuis la page web")

    CLIENTS.remove(ws)
    print("Client WebSocket déconnecté")
    return ws


# ---------- Lecture capteur ----------
async def sensor_loop(app):
    while True:
        value = adc.read(0)  # A0
        message = json.dumps({
            "type": "sensor",
            "value": value
        })

        for ws in CLIENTS:
            await ws.send_str(message)

        await asyncio.sleep(0.1)  # 10 Hz


# ---------- Serveur HTTP ----------
app = web.Application()
app.router.add_get("/ws", ws_handler)
app.router.add_static("/", path="html", show_index=True)

app.on_startup.append(lambda app: asyncio.create_task(sensor_loop(app)))

web.run_app(app, host="0.0.0.0", port=8000)
