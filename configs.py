import os


class WebSocketConfig:
    host = os.getenv("WEBSOCKET_HOST")
    port = os.getenv("WEBSOCKET_PORT")
    cert_path = os.getenv("WEBSOCKET_CERT_PATH")
    key_path = os.getenv("WEBSOCKET_KEY_PATH")


class EngineConfig:
    interval = float(os.getenv("ENGINE_INTERVAL"))


class AppConfig:
    websocket = WebSocketConfig()
    engine = EngineConfig()


config = AppConfig()
