import asyncio
import json
import time
from main import get_all_data
from websockets.asyncio.server import serve
async def echo(websocket):  
    while True:
        await websocket.send(json.dumps(get_all_data()))
        time.sleep(1)

async def main():
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()

asyncio.run(main())