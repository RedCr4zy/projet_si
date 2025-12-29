import json
import asyncio
from aiohttp import web
import music

CLIENTS = set()

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    CLIENTS.add(ws)
    print("WebSocket connecté")

    await ws.send_json({"type": "connection", "msg": "Ping"})

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            print("WS reçu :", data)

            if data["type"] == "play":
                print("Lecture de l'instrument :", data["instrument"])
                music.play_beep(freq=440)

            if data["type"] == "connection":
                print("Client connecté avec ping pong")

    CLIENTS.discard(ws)
    print("WebSocket déconnecté")
    return ws
