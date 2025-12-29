from aiohttp import web
import asyncio
from ws import ws_handler, CLIENTS
import hardware

print("Serveur Python démarre")

async def redirect_root(request):
    raise web.HTTPFound('/index.html')

async def start_tasks(app):
    app["sensor"] = asyncio.create_task(
        hardware.sensor_loop(CLIENTS)
    )
    app["joystick"] = asyncio.create_task(
        hardware.joystick_loop(CLIENTS)
    )

async def stop_tasks(app):
    for task in app.values():
        task.cancel()

app = web.Application()
app.router.add_get("/", redirect_root)
app.router.add_get("/ws", ws_handler)
app.router.add_static("/", path="html", show_index=True)

app.on_startup.append(start_tasks)
app.on_cleanup.append(stop_tasks)

web.run_app(app, host="0.0.0.0", port=8000)
