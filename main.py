"""
Author: Marcel Braasch
Email: marcelbraasch@gmail.com

Goethe University Frankfurt
Text Technology Lab
September 2019

Utility to speed up wikipedia scraping.
NOTE: Only tested on MacOS.

Expects two arguments.
1) Number of scripts: "number" indicating with how many terminal
   windows you want to run the script.
   For example: python main.py 10
2) Safe mode: argument you can set if you want to set safe mode.
   Safe mode cancels script in every window and restarts it.
   This assures to restart if wikipedia blocked your calls.
   For example: python main.py 10 -s
"""

import sys
import os
import time
import datetime
from typing import Union
import json


class Main:

    def __init__(self):

        self._config = self._load_config()

        self._get_arg("-h")

        script_arg = self._get_arg("-a")
        self._no_of_scripts = script_arg if script_arg else 1

        lang_arg = self._get_arg("-l")
        self._language = lang_arg if lang_arg else "de"

        safe_arg = self._get_arg("-s")
        self._safe_mode_time = safe_arg

        self._start_command = self._get_command("start")
        self._stop_command = self._get_command("stop")
        self._restart_command = self._get_command("restart")

        self._run()

    @staticmethod
    def _load_config():
        with open("config.json", "r") as file:
            return json.loads(str(file.read()))

    def _print_help(self):
        print("==============================================================================="
              "\nThis programm will scrape and format Wikipedia for you.\n"
              "\n"
              "Go to  ./config.json if you want to specify file paths\n"
              "or if you want to specify a new language you want to scrape\n"
              "in.\n"
              "\n"
              "You can specify the following arguments:\n"
              "-s <integer> (starts safe mode)\n"
              "Specifies how long to wait until you want to restart the script.\n"
              "This makes sure you can restart the scripts in case of server time outs.\n"
              "Default: no safe mode at all.\n"
              "\n"
              "-a <integer> (amount of scripts to run)\n"
              "Specifies how many scripts you want to run at the same time.\n"
              "You can run several scripts at the same time. This will ensure fast scraping.\n"
              "Default: 1.\n"
              "\n"
              "-l <string> (language you want to scrape in)\n"
              "This specifies the language you want to scrape in.\n"
              f"You can choose out of {str(self._config['languages'])[1:-1]}\n"
              "Default: 'de'\n"
              "\n"
              "==============================================================================="
              )
        sys.exit()

    def _get_arg(self, arg_type: str) -> Union[str, int]:
        get_arg = False
        for arg in sys.argv:
            if arg == arg_type:
                get_arg = True

            elif arg == "-h":
                self._print_help()

            elif get_arg:

                if arg_type == "-a":
                    try:
                        return int(arg)
                    except ValueError:
                        raise Exception("-a <argument> needs to be an integer"
                                        "specifying the amount of scripts to run.")
                elif arg_type == "-s":
                    try:
                        return int(arg)
                    except ValueError:
                        raise Exception("-s <argument> nneds to be an integer"
                                        "specifying how long to wait until restart.")

                elif arg_type == "-l":
                    languages = self._config["languages"]
                    if arg in languages:
                        return arg
                    else:
                        raise Exception("-l <argument> must be in one of "
                                        f"{str(languages)[1:-1]}.")

    def _run(self):
        if self._safe_mode_time:
            os.system(self._start_command)
            counter = 1
            while True:
                time.sleep(self._safe_mode_time * 60)  # wait 12 minutes and restart script
                counter += 1
                os.system(self._restart_command)
                print(f"Round {counter}: " + str(datetime.datetime.now()).split(".")[0])
        else:
            os.system(self._start_command)

    def _get_command(self, name: str) -> str:
        path = self._config["commands_path"] + f"{name}_command.txt"
        with open(path, "r+") as file:
            command = file.read()
            command = command.replace("no_of_scripts", str(self._no_of_scripts))
            command = command.replace("language", str(self._language))
            return command


m = Main()
