import shutil
import typing
from pathlib import Path

from constants import FOR_UNDO_HISTORY, TRASH_PATH
from logger.logger_setup import terminal_logger


def undo(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Отменяет последнюю команду (cp, mv, rm).
    
    Args:
        arguments: Не используются
        flags: Флаги (не поддерживаются)
    
    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if not FOR_UNDO_HISTORY:
        print('undo: no commands to undo')
        terminal_logger.error('undo: no commands to undo')
        return 1

    last_line = FOR_UNDO_HISTORY.pop()
    command = last_line[0]
    arguments = last_line[1:-1]

    try:
        if command == 'cp':
            if len(arguments) > 1:
                final_path = Path(arguments[-1])

                if final_path.is_dir():
                    for argument in arguments[:-1]:
                        argument_path = Path(argument)
                        cp_item = final_path / argument_path.name
                        if cp_item.exists():
                            if cp_item.is_file():
                                cp_item.unlink()
                            elif cp_item.is_dir():
                                shutil.rmtree(cp_item)
                else:
                    if final_path.exists():
                        final_path.unlink()

        elif command == 'mv':
            if len(arguments) > 1:
                final_path = Path(arguments[-1])

                if final_path.is_dir():
                    for argument in arguments[:-1]:
                        argument_path = Path(argument)
                        mv_item = final_path / argument_path.name
                        if mv_item.exists():
                            shutil.move(str(mv_item), str(argument_path))
                else:
                    if final_path.exists():
                        argument_path = Path(arguments[0])
                        shutil.move(str(final_path), str(argument_path))

        elif command == 'rm':
            for argument in arguments:
                argument_path = Path(argument)
                trash_item_path = TRASH_PATH / argument_path.name

                if trash_item_path.exists():
                    if trash_item_path.is_dir():
                        shutil.copytree(trash_item_path, argument_path)
                    else:
                        shutil.copy2(trash_item_path, argument_path)

        else:
            print(f"undo: unknown command '{command}'")
            terminal_logger.error(f"undo: unknown command '{command}'")
            FOR_UNDO_HISTORY.append(last_line)
            return 1

        terminal_logger.info(f'undo: {command} - success')
        return 0

    except Exception as e:
        print(f'undo: error during undo operation: {e}')
        terminal_logger.error(f'undo: error during undo operation: {e}')
        FOR_UNDO_HISTORY.append(last_line)
        return 1
