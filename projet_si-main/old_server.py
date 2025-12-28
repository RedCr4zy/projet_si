# -*- coding: utf-8 -*-
from aiohttp import web
from ws import ws_handler

print("🚀 Serveur Python démarre")

async def redirect_root(request):
    raise web.HTTPFound('/index.html')

app = web.Application()
app.router.add_get("/", redirect_root)
app.router.add_get("/ws", ws_handler)
app.router.add_static("/", path="html", show_index=True)

web.run_app(app, host="0.0.0.0", port=8000)
