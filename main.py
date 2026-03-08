import asyncio
import sys

from creart import add_creator

loop = asyncio.new_event_loop()

from src.logger import LoggerCreator
add_creator(LoggerCreator)
from src.config import ConfigCreator
add_creator(ConfigCreator)
from src.api import APICreator
add_creator(APICreator)
from src.grpc.manager import WMCreator
add_creator(WMCreator)
from src.measurer import MeasurerCreator
add_creator(MeasurerCreator)

from src.cmd import InteractiveShell

if __name__ == '__main__':
    cmd = InteractiveShell(loop)
    if len(sys.argv) > 1:
        try:
            loop.run_until_complete(cmd.run_cli(sys.argv[1:]))
        except KeyboardInterrupt:
            loop.stop()
    else:
        try:
            loop.run_until_complete(cmd.start())
        except KeyboardInterrupt:
            loop.stop()
