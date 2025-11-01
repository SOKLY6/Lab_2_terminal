import shutil
import typing
from pathlib import Path

from constants import FOR_UNDO_HISTORY
from logger.logger_setup import terminal_logger
from ubuntu_commands import helper_functions

correct_flags = {'r'}


def cp(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Копирует файлы и директории.
    
    Args:
        arguments: Пути копируемых файлов и директорий
        flags: Поддерживается только флаг 'r' для рекурсивного копирования
    
    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if flags is None:
        flags = set()

    if not flags.issubset(correct_flags):
        print(
            'cp: does not support the flags:',
            f' {", ".join(flags.difference(correct_flags))}',
        )
        terminal_logger.error(
            'cp: does not support the flags:',
            f' {", ".join(flags.difference(correct_flags))}',
        )
        return 1

    if not arguments:
        print('cp: missing file operand')
        terminal_logger.error('cp: missing file operand')
        return 1

    if len(arguments) == 1:
        print(f"cp: missing destination file operand after '{arguments[0]}'")
        terminal_logger.error(
            f"cp: missing destination file operand after '{arguments[0]}'"
        )
        return 1

    cp_items = []

    recursive = False
    if 'r' in flags:
        recursive = True

    if len(arguments) == 2:
        first_item = arguments[0]
        second_item = arguments[1]

        if not Path(first_item).exists():
            print(f"cp: cannot stat '{first_item}': No such file or directory")
            terminal_logger.error(
                f"cp: cannot stat '{first_item}': No such file or directory"
            )
            return 1

        first_path = Path(first_item)
        second_path = Path(second_item)

        if first_path.is_dir():
            if not recursive:
                print(
                    f"cp: -r not specified; omitting directory '{first_item}'"
                )
                terminal_logger.error(
                    f"cp: -r not specified; omitting directory '{first_item}'"
                )
                return 1

            if second_path.exists():
                if second_path.is_dir():
                    final_dest = second_path / first_path.name
                    try:
                        shutil.copytree(first_item, final_dest)
                        cp_items.append(str(first_path))
                        cp_items.append(str(final_dest))
                        terminal_logger.info(
                            f'cp: {first_item} -> {final_dest} - success'
                        )

                    except Exception as e:
                        print(
                            f"cp: cannot copy '{first_item}'",
                            f" to '{final_dest}': {e}",
                        )
                        terminal_logger.error(
                            f"cp: cannot copy '{first_item}'",
                            f" to '{final_dest}': {e}",
                        )
                        return 1
                else:
                    print(
                        'cp: cannot overwrite non-directory',
                        " '{second_item}' with directory '{first_item}'",
                    )
                    terminal_logger.error(
                        'cp: cannot overwrite non-directory',
                        " '{second_item}' with directory '{first_item}'",
                    )
                    return 1
            else:
                if helper_functions.is_valid_dirname(second_path.name):
                    try:
                        shutil.copytree(first_path, second_path)
                        cp_items.append(str(first_path))
                        cp_items.append(str(second_path))
                        terminal_logger.info(
                            f'cp: {first_item} -> {second_item} - success'
                        )

                    except Exception as e:
                        print(
                            f"cp: cannot create directory '{second_item}': {e}"
                        )
                        terminal_logger.error(
                            f"cp: cannot create directory '{second_item}': {e}"
                        )
                        return 1
                else:
                    print(f"cp: invalid directory name '{second_path.name}'")
                    terminal_logger.error(
                        f"cp: invalid directory name '{second_path.name}'"
                    )
                    return 1

        elif first_path.is_file():
            if second_path.exists() and second_path.is_dir():
                try:
                    shutil.copy2(first_path, second_path)
                    cp_items.append(str(first_path))
                    cp_items.append(str(second_path))
                    terminal_logger.info(
                        f'cp: {first_item} -> {second_item} - success'
                    )

                except Exception as e:
                    print(
                        f"cp: cannot copy '{first_item}'",
                        f" to '{second_path}': {e}",
                    )
                    terminal_logger.error(
                        f"cp: cannot copy '{first_item}'",
                        f" to '{second_path}': {e}",
                    )
                    return 1
            else:
                if helper_functions.is_valid_filename(second_path.name):
                    try:
                        second_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(first_path, second_path)
                        cp_items.append(str(first_path))
                        cp_items.append(str(second_path))
                        terminal_logger.info(
                            f'cp: {first_item} -> {second_item} - success'
                        )

                    except Exception as e:
                        print(
                            f"cp: cannot copy '{first_item}'",
                            f" to '{second_item}': {e}",
                        )
                        terminal_logger.error(
                            f"cp: cannot copy '{first_item}'",
                            f" to '{second_item}': {e}",
                        )
                        return 1
                else:
                    print(f"cp: invalid filename '{second_path.name}'")
                    terminal_logger.error(
                        f"cp: invalid filename '{second_path.name}'"
                    )
                    return 1
        else:
            print(f"cp: cannot copy '{first_item}': No such file or directory")
            terminal_logger.error(
                f"cp: cannot copy '{first_item}': No such file or directory"
            )
            return 1

    else:
        last_item = arguments[-1]
        last_path = Path(last_item)

        if not last_path.exists():
            print(f"cp: target '{last_item}': No such file or directory")
            terminal_logger.error(
                f"cp: target '{last_item}': No such file or directory"
            )
            return 1

        if not last_path.is_dir():
            print(f"cp: target '{last_item}' is not a directory")
            terminal_logger.error(
                f"cp: target '{last_item}' is not a directory"
            )
            return 1

        for item in arguments[:-1]:
            item_path = Path(item)
            if not item_path.exists():
                print(f"cp: cannot stat '{item}': No such file or directory")
                terminal_logger.error(
                    f"cp: cannot stat '{item}': No such file or directory"
                )
                continue

            if item_path.is_file():
                try:
                    shutil.copy2(item_path, last_path)
                    cp_items.append(str(item_path))
                    terminal_logger.info(
                        f'cp: {item} -> {last_item} - success'
                    )
                except Exception as e:
                    print(f"cp: cannot copy '{item}' to '{last_item}': {e}")
                    terminal_logger.error(
                        f"cp: cannot copy '{item}' to '{last_item}': {e}"
                    )
                    continue

            elif item_path.is_dir():
                if not recursive:
                    print(f"cp: -r not specified; omitting directory '{item}'")
                    terminal_logger.error(
                        f"cp: -r not specified; omitting directory '{item}'"
                    )
                    continue

                try:
                    final_path = last_path / item_path.name
                    shutil.copytree(item_path, final_path)
                    cp_items.append(str(item_path))
                    terminal_logger.info(
                        f'cp: {item} -> {final_path} - success'
                    )
                except Exception as e:
                    print(f"cp: cannot copy '{item}' to '{final_path}': {e}")
                    terminal_logger.error(
                        f"cp: cannot copy '{item}' to '{final_path}': {e}"
                    )
                    continue

        if cp_items:
            cp_items.append(str(last_path))

    if cp_items:
        FOR_UNDO_HISTORY.append(['cp'] + cp_items + [Path('.')])
    return 0
