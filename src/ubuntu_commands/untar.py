import shutil
import typing
from pathlib import Path

from logger.logger_setup import terminal_logger
from ubuntu_commands import helper_functions


def is_tar_gz_archive(file_path: Path) -> bool:
    """Проверяет, является ли файл tar.gz архивом.

    Args:
        file_path: Путь к файлу для проверки

    Returns:
        bool: True если файл является tar.gz архивом
    """
    path = Path(file_path)
    suffixes = path.suffixes
    return (
        path.exists()
        and path.is_file()
        and len(suffixes) >= 2
        and suffixes[-2].lower() == '.tar'
        and suffixes[-1].lower() == '.gz'
    )


def untar(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Распаковывает tar-архивы.

    Args:
        arguments: Пути к архивам и директория для распаковки (опционально)
        flags: Флаги (не поддерживаются)

    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if not flags:
        if not arguments:
            print('untar: missing archive operand')
            terminal_logger.error('untar: missing archive operand')
            return 1

        if len(arguments) == 1:
            extract_folder = Path('.')
            archives = arguments
        else:
            first_argument = Path(arguments[0])
            if first_argument.is_dir():
                extract_folder = first_argument
                archives = arguments[1:]
            else:
                extract_folder = Path('.')
                archives = arguments

        for archive in archives:
            archive_path = Path(archive)

            if not archive_path.exists():
                print(f"untar:  cannot find or open '{archive}'")
                terminal_logger.error(
                    f"untar:  cannot find or open '{archive}'"
                )
                archives.remove(archive)
                continue

            if not is_tar_gz_archive(archive_path):
                print(f"untar: '{archive}' is not tarfile")
                terminal_logger.error(f"untar: '{archive}' is not tarfile")
                archives.remove(archive)
                continue

        for archive in archives:
            archive_path = Path(archive)

            try:
                temp_dir = Path('temp_untar')
                temp_dir.mkdir(exist_ok=True)

                shutil.unpack_archive(archive, temp_dir)

                helper_functions.extracting_files(
                    temp_dir, extract_folder, archive
                )

                shutil.rmtree(temp_dir)

                terminal_logger.info(f'untar: {archive} - success')

            except Exception as e:
                print(f"untar: error extracting '{archive}': {e}")
                terminal_logger.error(
                    f"untar: error extracting '{archive}': {e}"
                )
                continue

        return 0

    print(f'untar: does not support the flags: {", ".join(flags)}')
    terminal_logger.error(
        f'untar: does not support the flags: {", ".join(flags)}'
    )
    return 1
