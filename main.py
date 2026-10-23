import asyncio
from core.actions import ActionsExecutor
from core.engine import MetricsEngine
from api.ws_server import WebsocketServer


async def main():
    metrics_engine = MetricsEngine()
    actions = ActionsExecutor()
    websocket_server = WebsocketServer(metrics_engine, actions = actions)
    asyncio.create_task(metrics_engine.run_loop())
    await websocket_server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Exiting... ")