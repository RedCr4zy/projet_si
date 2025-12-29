import asyncio
import json

try:
    from grove.adc import ADC
    GROVE_AVAILABLE = True
except ImportError:
    GROVE_AVAILABLE = False

try:
    from inputs import get_gamepad
    JOYSTICK_AVAILABLE = True
except ImportError:
    JOYSTICK_AVAILABLE = False


async def sensor_loop(clients):
    if not GROVE_AVAILABLE:
        return

    adc = ADC()
    while True:
        value = adc.read(0)
        msg = json.dumps({"type": "sensor", "value": value})
        for ws in list(clients):
            if not ws.closed:
                await ws.send_str(msg)
        await asyncio.sleep(0.1)


async def joystick_loop(clients):
    if not JOYSTICK_AVAILABLE:
        return

    while True:
        for e in get_gamepad():
            msg = json.dumps({
                "type": "joystick",
                "code": e.code,
                "state": e.state
            })
            for ws in list(clients):
                if not ws.closed:
                    await ws.send_str(msg)
        await asyncio.sleep(0.01)
