import os
import json
import signal
from json.decoder import JSONDecodeError
from abc import ABC, abstractmethod

class ActionCommand(ABC):
    @abstractmethod
    def execute(self, payload):
        pass

class KillProcessCommand(ActionCommand):
    def execute(self, payload):
        try:
            pid = payload.get("pid")
            print(f"Performed kill, pid: {pid} signal.SIGTERM")
            os.kill(int(pid), signal.SIGTERM)
            return {"type": "kill_status", "status": "OK", "reason": ""}
        except Exception as e:
            return {"type": "kill_status", "status": "NOK", "reason": f"{e}"}


class ActionsExecutor:

    _COMMAND = {
        "kill_process": KillProcessCommand
    }

    @classmethod
    def execute_from_json(cls, json_action):
        try:
            action = json.loads(json_action)
            command_class = cls._COMMAND.get(action["type"])
            command = command_class()
            status = command.execute(action)
        except JSONDecodeError:
            return {"type": "execute", "status": "NOK", "reason": "Invalid JSON format"}
        except KeyError, TypeError:
            return {"type": "execute", "status": "NOK", "reason": "Invalid keys"}
        return status
