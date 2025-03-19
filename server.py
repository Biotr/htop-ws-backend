import asyncio
import json
import os
import signal

from websockets.asyncio.server import serve

from main import get_all_data


async def kill_process(id):
    try:
        os.kill(int(id), signal.SIGTERM)
    except Exception as e:
        print(e)


async def listen(ws):
    async for id in ws:
        await kill_process(id)


async def echo(ws):
    while True:
        await ws.send(json.dumps(get_all_data()))
        await asyncio.sleep(1)


async def handler(websocket):
    async with asyncio.TaskGroup() as tg:
        tg.create_task(listen(websocket))
        tg.create_task(echo(websocket))


async def main():
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


asyncio.run(main())
