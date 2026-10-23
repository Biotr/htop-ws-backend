import asyncio
import sys
import json
import ssl

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK


class WebsocketServer:
    def __init__(
        self,
        engine,
        host="0.0.0.0",
        port=8765,
        certfile="./certificates/cert.pem",
        keyfile="./certificates/key.pem",
        *,
        actions,
    ):

        self.engine = engine
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.actions = actions
        self.clients = set()

    def _setup_ssl(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        except FileNotFoundError as e:
            print("\n Certificate not files found - run setup.sh\n")
            sys.exit(1)
        return ssl_context

    async def _listen_client(self, client):
        while True:
            message = await client.recv()
            status = self.actions.execute_from_json(message)
            print(f"Execution status: {status}")
            await client.send(json.dumps(status))

    async def broadcast(self, interval=1):
        while True:
            await asyncio.sleep(interval)

            if not self.clients or not self.engine.data:
                continue

            try:
                for client in self.clients:
                    await client.send(json.dumps(self.engine.data))
            except Exception as e:
                print(f"Client disconnected {client}, reason: {e}")
                self.clients.remove(client)

    async def _connection_handler(self, client):
        self.clients.add(client)
        print(f"Connection opened with client {client}")

        try:
            await self._listen_client(client)
        except ConnectionClosedOK:
            print(f"Connection closed succesfully with client {client}")
        except Exception as e:
            print(f"Unhandled exception: {e}")
        finally:
            self.clients.remove(client)

    async def start(self):
        ssl_context = self._setup_ssl()
        await serve(self._connection_handler, self.host, self.port, ssl=ssl_context)
        await self.broadcast()
