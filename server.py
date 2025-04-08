import asyncio
import json
import os
import signal
import ssl
import sys

from main import SystemInfo
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK


def setup_ssl():
    ssl_cert = "./certificates/cert.pem"
    ssl_key = "./certificates/key.pem"
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)
    except FileNotFoundError as e:
        print("\nNo certificate files found - run setup\n")
        sys.exit(1)
    return ssl_context


async def kill_process(ws, id):
    try:
        os.kill(int(id), signal.SIGTERM)
    except Exception as e:
        print(str(e))
        await ws.send(json.dumps({"type": "kill_status", "status": str(e)}))
        return
    await ws.send(json.dumps({"type": "kill_status", "status": f"Process {id}, killed."}))


async def listen(ws):
    async for id in ws:
        await kill_process(ws, id)


async def echo(ws):
    sys = SystemInfo()
    while True:
        sys.update()
        data_to_send = {"type": "data", "memory_info": sys.meminfo, "cores_usage": sys.cores_usage, "load_average": sys.load_avg, "processes": sys.processes, "uptime": sys.uptime}
        try:
            await ws.send(json.dumps(data_to_send))
        except ConnectionClosedOK:
            print("Client disconnected")
            break
        await asyncio.sleep(1)


async def handler(websocket):
    await asyncio.gather(echo(websocket), listen(websocket))


async def main():
    address = "0.0.0.0"
    port = 8765
    ssl_context = setup_ssl()
    async with serve(handler, address, port, ssl=ssl_context) as server:
        print(f"Server running on {address}:{port}")
        await server.serve_forever()


asyncio.run(main())
