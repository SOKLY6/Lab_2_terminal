import shutil
import typing
from pathlib import Path

from ubuntu_commands import helper_functions


def zip_(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Создает zip-архив из файлов и директорий.

    Args:
        arguments: Имя архива и пути к архивируемым файлам
        flags: Флаги (не поддерживаются)

    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if not flags:
        if len(arguments) == 0:
            print('zip: missing arguments')
            return 1

        if len(arguments) == 1:
            archive_name = arguments[0]
            argument_path = Path(archive_name)

            if not argument_path.exists():
                print(
                    f"zip: cannot stat '{archive_name}':",
                    ' No such file or directory',
                )
                return 1

            archive_name = argument_path.stem

        else:
            archive_name = arguments[0]
            arguments = arguments[1:]
            archive_name = Path(archive_name).stem

        if not helper_functions.is_valid_filename(archive_name):
            print(f"zip: invalid archive name '{archive_name}'")
            return 1

        missing_arguments = []
        for argument in arguments:
            if not Path(argument).exists():
                missing_arguments.append(argument)

        if missing_arguments:
            for missing in missing_arguments:
                print(
                    f"zip: cannot stat '{missing}': No such file or directory"
                )
            return 1

        temp_dir = Path(f'temp_zip_{archive_name}')
        try:
            temp_dir.mkdir(exist_ok=True)

            for argument in arguments:
                argument_path = Path(argument)
                final_path = temp_dir / argument_path.name

                if argument_path.is_file():
                    shutil.copy2(argument_path, final_path)

                elif argument_path.is_dir():
                    shutil.copytree(argument_path, final_path)

            shutil.make_archive(archive_name, 'zip', temp_dir)
            return 0

        except Exception as e:
            print(f'zip: error creating archive: {e}')
            return 1

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    print(f'zip: does not support the flags: {", ".join(flags)}')
    return 1
