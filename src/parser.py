import shlex

from logger.logger_setup import terminal_logger
from ubuntu_commands import (
    cat,
    cd,
    cp,
    grep,
    helper_functions,
    history,
    ls,
    mv,
    rm,
    tar,
    undo,
    untar,
    unzip,
    zip_,
)

commands = {
    'ls': ls.ls,
    'cd': cd.cd,
    'cat': cat.cat,
    'cp': cp.cp,
    'mv': mv.mv,
    'rm': rm.rm,
    'zip': zip_.zip_,
    'unzip': unzip.unzip,
    'tar': tar.tar,
    'untar': untar.untar,
    'grep': grep.grep,
    'history': history.history,
    'undo': undo.undo,
}


def parser(line: str) -> int:
    list_of_line = shlex.split(line)
    if not list_of_line:
        return 0

    command = list_of_line[0]

    if command in commands:
        arguments = list_of_line[1:]
        flags = set()

        for argument in arguments:
            result_flagging = helper_functions.is_flags(argument)

            if result_flagging == 1:
                print('a non-existent flags')
                terminal_logger.error('a non-existent flags')
                return 1

            if result_flagging == 0:
                break

            arguments = arguments[1:]
            flags.update(result_flagging)

        return commands[command](arguments, flags)

    else:
        print(f'{command}: command not found')
        terminal_logger.error(f'{command}: command not found')
        return 1
