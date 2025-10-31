import shutil
import typing
from pathlib import Path

from logger.logger_setup import terminal_logger
from ubuntu_commands import helper_functions


def is_zip_archive(file_path: Path) -> bool:
    path = Path(file_path)
    return path.exists() and path.is_file() and path.suffix.lower() == '.zip'


def unzip(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    if not flags:
        if not arguments:
            print('unzip: missing archive operand')
            terminal_logger.error('unzip: missing archive operand')
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
                print(f"unzip:  cannot find or open '{archive}'")
                terminal_logger.error(
                    f"unzip:  cannot find or open '{archive}'"
                )
                archives.remove(archive)
                continue

            if not is_zip_archive(archive_path):
                print(f"unzip: '{archive}' is not zipfile")
                terminal_logger.error(f"unzip: '{archive}' is not zipfile")
                archives.remove(archive)
                continue

        for archive in archives:
            archive_path = Path(archive)

            try:
                temp_dir = Path('temp_unzip')
                temp_dir.mkdir(exist_ok=True)

                shutil.unpack_archive(archive, temp_dir)

                helper_functions.extracting_files(
                    temp_dir, extract_folder, archive
                )

                shutil.rmtree(temp_dir)

                terminal_logger.info(f'unzip: {archive} - success')

            except Exception as e:
                print(f"unzip: error extracting '{archive}': {e}")
                terminal_logger.error(
                    f"unzip: error extracting '{archive}': {e}"
                )
                continue

        return 0

    print(f'unzip: does not support the flags: {", ".join(flags)}')
    terminal_logger.error(
        f'unzip: does not support the flags: {", ".join(flags)}'
    )
    return 1
