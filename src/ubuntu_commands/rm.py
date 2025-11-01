import shutil
import typing
from pathlib import Path

from constants import FOR_UNDO_HISTORY, TRASH_PATH
from logger.logger_setup import terminal_logger

correct_flags = {'r'}


def rm(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Удаляет файлы и директории.

    Args:
        arguments: Пути к удаляемым файлам и директориям
        flags: 'r' - рекурсивное удаление директорий

    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if flags is None:
        flags = set()

    if not flags.issubset(correct_flags):
        print(
            'rm: does not support the flags:',
            f' {", ".join(flags.difference(correct_flags))}',
        )
        terminal_logger.error(
            'rm: does not support the flags:',
            f' {", ".join(flags.difference(correct_flags))}',
        )
        return 1

    if not arguments:
        print('rm: missing operand')
        terminal_logger.error('rm: missing operand')
        return 1

    rm_items = []

    recursive = False
    if 'r' in flags:
        recursive = True

    for argument in arguments:
        argument_path = Path(argument)

        if not argument_path.exists():
            print(f"rm: cannot remove '{argument}': No such file or directory")
            terminal_logger.error(
                f"rm: cannot remove '{argument}': No such file or directory"
            )
            continue

        if argument_path.is_dir():
            if not recursive:
                print(f'rm: cannot remove {argument}: Is a directory')
                terminal_logger.error(
                    f'rm: cannot remove {argument}: Is a directory'
                )
                continue

            forbidden_path = argument_path.resolve()
            current_dir = Path('.').resolve()

            if forbidden_path == forbidden_path.root:
                print(
                    f"rm: cannot remove '{argument}':",
                    ' Permission denied - root directory',
                )
                terminal_logger.error(
                    f"rm: attempt to remove root directory '{argument}'"
                )
                continue

            if forbidden_path == current_dir.parent:
                print(
                    f"rm: cannot remove '{argument}':",
                    ' Permission denied - parent directory',
                )
                terminal_logger.error(
                    f"rm: attempt to remove parent directory '{argument}'"
                )
                continue

            answer = (
                input(f"rm: remove directory '{argument}'? [y/n] ")
                .strip()
                .lower()
            )

            if answer not in ('y', 'yes'):
                print(f"rm: skipping directory '{argument}'")
                terminal_logger.info(f"rm: skipping directory '{argument}'")
                continue

            try:
                trash_argument_path = TRASH_PATH / argument_path.name

                if trash_argument_path.exists():
                    if trash_argument_path.is_dir():
                        shutil.rmtree(trash_argument_path)
                    else:
                        trash_argument_path.unlink()

                rm_items.append(str(argument_path))
                shutil.copytree(argument_path, trash_argument_path)
                shutil.rmtree(argument_path)
                terminal_logger.info(f'rm: {argument} - success')

            except Exception as e:
                print(f"rm: cannot remove '{argument}': {e}")
                terminal_logger.error(f"rm: cannot remove '{argument}': {e}")
                continue

        elif argument_path.is_file():
            try:
                rm_items.append(str(argument_path))
                shutil.copy2(argument_path, TRASH_PATH)
                argument_path.unlink()
                terminal_logger.info(f'rm: {argument} - success')

            except Exception as e:
                print(f"rm: cannot remove '{argument}': {e}")
                terminal_logger.error(f"rm: cannot remove '{argument}': {e}")
                continue
        else:
            print(f"rm: cannot remove '{argument}': No such file or directory")
            terminal_logger.error(
                f"rm: cannot remove '{argument}': No such file or directory"
            )
            continue

    if rm_items:
        FOR_UNDO_HISTORY.append(['rm'] + rm_items + [Path('.')])

    return 0
