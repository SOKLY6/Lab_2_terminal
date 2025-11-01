import datetime
import stat
import typing
from pathlib import Path

from logger.logger_setup import terminal_logger

correct_flags = {'l', 'a'}


def ls_long(item_path: Path) -> str:
    """Форматирует информацию о файле для подробного вывода ls.
    
    Args:
        item_path: Путь к файлу/директории
    
    Returns:
        str: Отформатированная строка с правами, размером, датой и именем
    """
    stat_info = item_path.stat()

    permissions = stat.filemode(stat_info.st_mode)

    size = stat_info.st_size

    date_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime(
        '%b %d %H:%M'
    )

    name = item_path.name

    return f'{permissions} {size:>8} {date_time} {name}'


def ls(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Выводит список файлов и директорий.
    
    Args:
        arguments: Пути для отображения (по умолчанию текущая директория)
        flags: 'l' - подробный формат, 'a' - показывать скрытые файлы
    
    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if flags is None:
        flags = set()

    if not flags.issubset(correct_flags):
        print(
            'ls: does not support the flags:',
            f' {", ".join(flags.difference(correct_flags))}',
        )
        terminal_logger.error(
            'ls: does not support the flags:'
            + f' {", ".join(flags.difference(correct_flags))}',
        )
        return 1

    All = False
    long = False

    if 'l' in flags:
        long = True
    if 'a' in flags:
        All = True

    if not arguments:
        arguments = ['.']

    for argument in arguments:
        argument_path = Path(argument)

        if not argument_path.exists():
            print(f"ls: cannot access '{argument}': No such file or directory")
            terminal_logger.error(
                f"ls: cannot access '{argument}': No such file or directory"
            )
            continue

        if argument_path.is_file():
            if long:
                print(ls_long(argument_path))
            else:
                print(argument)

        elif argument_path.is_dir():
            items = []

            for item in argument_path.iterdir():
                if not All and item.name.startswith('.'):
                    continue
                items.append(item)

            items.sort(key=lambda x: x.name)

            if len(arguments) > 1:
                print(f'{argument}/:')

            if long:
                for item in items:
                    print(ls_long(item))

            else:
                item_names = ' '.join([item.name for item in items])
                print(item_names)

            if len(arguments) > 1 and argument != arguments[-1]:
                print()

    terminal_logger.info(f'ls: {" ".join(arguments)} - success')
    return 0
