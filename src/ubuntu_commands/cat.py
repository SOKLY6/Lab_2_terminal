import typing
from pathlib import Path

from logger.logger_setup import terminal_logger


def cat(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    if not flags:
        for argument in arguments:
            argument_path = Path(argument)

            if not argument_path.exists():
                print(f'cat: {argument}: No such file or directory')
                terminal_logger.error(
                    f'cat: {argument}: No such file or directory'
                )
                continue

            if argument_path.is_dir():
                print(f'cat: {argument}: Is a directory')
                terminal_logger.error(f'cat: {argument}: Is a directory')
                continue

            if argument_path.is_file():
                text = argument_path.read_text(encoding='utf-8')
                print(text)

        terminal_logger.info(f'cat: {arguments} - success')
        return 0

    print(f'cat: does not support the flags: {", ".join(flags)}')
    terminal_logger.error(
        f'cat: does not support the flags: {", ".join(flags)}'
    )
    return 1
