import sys
import json
import os

class Close:

    def __init__(self):

        self._config = self._load_config()
        self.no_of_scripts = int(sys.argv[1])
        self.command = self.get_command()
        self.run_command()

    @staticmethod
    def _load_config():
        with open("config.json", "r") as file:
            return json.loads(str(file.read()))

    def run_command(self):
        os.system(self.command)

    def get_command(self):
        path = self._config["commands_path"] + "stop_command.txt"
        with open(path, "r+") as file:
            command = file.read().replace("no_of_scripts", str(self.no_of_scripts))
        return command
        
c = Close()