import os
import typing
from pathlib import Path

from logger.logger_setup import terminal_logger


def cd(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Меняет текущую рабочую директорию.
    
    Args:
        arguments: Путь к директории (максимум 1 аргумент)
        flags: Флаги (не поддерживаются)
    
    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if not flags:
        if len(arguments) > 1:
            print('-bash: cd: too many arguments')
            terminal_logger.error(f'cd: too many arguments: {arguments}')
            return 0

        if not arguments or arguments[0] == '~':
            argument_path = Path.home()
            os.chdir(str(argument_path))
            terminal_logger.info(f'cd: {arguments} - success')
            return 0

        else:
            argument_path = Path(arguments[0])

            if argument_path.is_dir():
                argument_path = Path(arguments[0]).expanduser().resolve()
                os.chdir(str(argument_path))
                terminal_logger.info(f'cd: {arguments} - success')
                return 0

            elif argument_path.is_file():
                print(f'-bash: cd: {argument_path.name}: Not a directory')
                terminal_logger.error(
                    f'cd: {argument_path.name}: Not a directory'
                )
                return 1

            else:
                print(
                    f'-bash: cd: {argument_path.name}:',
                    ' No such file or directory',
                )
                terminal_logger.error(
                    f'cd: {argument_path.name}: No such file or directory'
                )
                return 1

    print(f'-bash: cd: does not support the flags: {", ".join(flags)}')
    terminal_logger.error(
        f'cd: does not support the flags: {", ".join(flags)}'
    )
    return 1
