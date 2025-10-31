import os
import sys
from pathlib import Path

import parser
from logger.logger_setup import terminal_logger
from ubuntu_commands import helper_functions


def run() -> None:
    os.chdir(str(Path.home()))
    print(Path.cwd(), end=' ', flush=True)
    for line in sys.stdin:
        line = line.strip()

        terminal_logger.info(line)

        helper_functions.write_history(line)

        if not line:
            print(Path.cwd(), end=' ', flush=True)
            continue
        try:
            parser.parser(line)

        except Exception as e:
            print(f'Error: {e}')
            terminal_logger.error(f'{e}')

        print(Path.cwd(), end=' ', flush=True)


if __name__ == '__main__':
    run()
