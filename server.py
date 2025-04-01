import asyncio
import json
import os
import signal
from main import SystemInfo
from websockets.asyncio.server import serve



async def kill_process(id):
    try:
        os.kill(int(id), signal.SIGTERM)
    except Exception as e:
        print(e)


async def listen(ws):
    async for id in ws:
        await kill_process(id)


async def echo(ws):
    sys = SystemInfo()
    while True:
        sys.update()
        data_to_send = {
            "memory_info":sys.meminfo,
            "cores_usage":sys.cores_usage,
            "load_average":sys.load_avg,
            "processes":sys.processes,
            "uptime":sys.uptime
        }
        await ws.send(json.dumps(data_to_send))
        await asyncio.sleep(1)


async def handler(websocket):
    await asyncio.gather(echo(websocket),listen(websocket))


async def main():
    address = "0.0.0.0"
    port = 8765
    async with serve(handler, address, port) as server:
        print(f"Server running on {address}:{port}")
        await server.serve_forever()


asyncio.run(main())
