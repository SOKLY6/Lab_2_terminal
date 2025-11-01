import shutil
import typing
from pathlib import Path

from constants import FOR_UNDO_HISTORY
from logger.logger_setup import terminal_logger
from ubuntu_commands import helper_functions


def mv(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Перемещает или переименовывает файлы и директории.
    
    Args:
        arguments: Исходные пути и путь назначения
        flags: Флаги (не поддерживаются)
    
    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if not flags:
        if not arguments:
            print('mv: missing file operand')
            terminal_logger.error('mv: missing file operand')
            return 1

        if len(arguments) == 1:
            print(
                f"mv: missing destination file operand after '{arguments[0]}'"
            )
            terminal_logger.error(
                f"mv: missing destination file operand after '{arguments[0]}'"
            )
            return 1

        mv_items = []

        if len(arguments) == 2:
            first_item = arguments[0]
            second_item = arguments[1]

            if not Path(first_item).exists():
                print(
                    f"mv: cannot stat '{first_item}':",
                    ' No such file or directory',
                )
                terminal_logger.error(
                    f"mv: cannot stat '{first_item}':",
                    ' No such file or directory',
                )
                return 1

            first_path = Path(first_item)
            second_path = Path(second_item)

            if first_path.is_dir():
                if second_path.exists():
                    if second_path.is_dir():
                        final_dest = second_path / first_path.name
                        try:
                            shutil.move(str(first_path), str(final_dest))
                            mv_items.append(str(first_path))
                            mv_items.append(str(final_dest))
                            terminal_logger.info(
                                f'mv: {first_item} -> {final_dest} - success'
                            )

                        except Exception as e:
                            print(
                                f"mv: cannot move '{first_item}'",
                                f" to '{final_dest}': {e}",
                            )
                            terminal_logger.error(
                                f"mv: cannot move '{first_item}'",
                                f" to '{final_dest}': {e}",
                            )
                            return 1
                    else:
                        print(
                            'mv: cannot overwrite non-directory ',
                            f"'{second_item}' with directory '{first_item}'",
                        )
                        terminal_logger.error(
                            'mv: cannot overwrite non-directory ',
                            f"'{second_item}' with directory '{first_item}'",
                        )
                        return 1
                else:
                    if helper_functions.is_valid_dirname(second_path.name):
                        try:
                            second_path.parent.mkdir(
                                parents=True, exist_ok=True
                            )
                            shutil.move(str(first_path), str(second_path))
                            mv_items.append(str(first_path))
                            mv_items.append(str(second_path))
                            terminal_logger.info(
                                f'mv: {first_item} -> {second_item} - success'
                            )

                        except Exception as e:
                            print(
                                f"mv: cannot move '{first_item}'",
                                f" to '{second_item}': {e}",
                            )
                            terminal_logger.error(
                                f"mv: cannot move '{first_item}'",
                                f" to '{second_item}': {e}",
                            )
                            return 1
                    else:
                        print(
                            f"mv: invalid directory name '{second_path.name}'"
                        )
                        terminal_logger.error(
                            f"mv: invalid directory name '{second_path.name}'"
                        )
                        return 1

            elif first_path.is_file():
                if second_path.exists() and second_path.is_dir():
                    try:
                        shutil.move(str(first_path), str(second_path))
                        mv_items.append(str(first_path))
                        mv_items.append(str(second_path))
                        terminal_logger.info(
                            f'mv: {first_item} -> {second_item} - success'
                        )

                    except Exception as e:
                        print(
                            f"mv: cannot move '{first_item}'",
                            f" to '{second_item}': {e}",
                        )
                        terminal_logger.error(
                            f"mv: cannot move '{first_item}'",
                            f" to '{second_item}': {e}",
                        )
                        return 1
                else:
                    try:
                        second_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(first_path), str(second_path))
                        mv_items.append(str(first_path))
                        mv_items.append(str(second_path))
                        terminal_logger.info(
                            f'mv: {first_item}', f' -> {second_item} - success'
                        )

                    except Exception as e:
                        print(
                            f"mv: cannot move '{first_item}'",
                            f" to '{second_item}': {e}",
                        )
                        terminal_logger.error(
                            f"mv: cannot move '{first_item}'",
                            f" to '{second_item}': {e}",
                        )
                        return 1
            else:
                print(
                    f"mv: cannot move '{first_item}':",
                    ' No such file or directory',
                )
                terminal_logger.error(
                    f"mv: cannot move '{first_item}':",
                    ' No such file or directory',
                )
                return 1

        else:
            last_item = arguments[-1]
            last_path = Path(last_item)

            if not last_path.exists():
                print(f"mv: target '{last_item}': No such file or directory")
                terminal_logger.error(
                    f"mv: target '{last_item}': No such file or directory"
                )
                return 1

            if not last_path.is_dir():
                print(f"mv: target '{last_item}' is not a directory")
                terminal_logger.error(
                    f"mv: target '{last_item}' is not a directory"
                )
                return 1

            for item in arguments[:-1]:
                item_path = Path(item)
                if not item_path.exists():
                    print(
                        f"mv: cannot stat '{item}': No such file or directory"
                    )
                    terminal_logger.error(
                        f"mv: cannot stat '{item}': No such file or directory"
                    )
                    continue

                try:
                    final_path = last_path / item_path.name
                    shutil.move(str(item_path), str(final_path))
                    mv_items.append(str(item_path))
                    terminal_logger.info(
                        f'mv: {item} -> {final_path} - success'
                    )
                except Exception as e:
                    print(f"mv: cannot move '{item}' to '{final_path}': {e}")
                    terminal_logger.error(
                        f"mv: cannot move '{item}' to '{final_path}': {e}"
                    )
                    continue

            if mv_items:
                mv_items.append(str(final_path))

        if mv_items:
            FOR_UNDO_HISTORY.append(['mv'] + mv_items + [Path('.')])
        return 0

    print(f'mv: does not support the flags: {", ".join(flags)}')
    terminal_logger.error(
        f'mv: does not support the flags: {", ".join(flags)}'
    )
    return 1
