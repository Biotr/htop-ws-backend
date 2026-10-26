import asyncio
from configs import config
from core.actions import ActionsExecutor
from core.engine import MetricsEngine
from api.ws_server import WebsocketServer


async def main():
    metrics_engine = MetricsEngine()
    actions = ActionsExecutor()
    websocket_server = WebsocketServer(
        config.websocket.host,
        config.websocket.port,
        config.websocket.cert_path,
        config.websocket.key_path,
        engine=metrics_engine,
        actions=actions,
    )

    asyncio.create_task(metrics_engine.run_loop(config.engine.interval))
    await websocket_server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Exiting... ")
