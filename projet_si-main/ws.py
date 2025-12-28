from aiohttp import web
import json
import asyncio
import music

CLIENTS = set()

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    CLIENTS.add(ws)
    print("🔌 WebSocket connecté")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)

            if data.get("type") == "play":
                print("🎵 Play melody demandé")
                asyncio.create_task(asyncio.to_thread(music.piano, 261.63, 1))
                print("Mélodie jouée")

    CLIENTS.discard(ws)
    print("❌ WebSocket déconnecté")
    return ws
