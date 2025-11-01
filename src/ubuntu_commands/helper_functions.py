import shutil
from pathlib import Path

from constants import (
    HISTORY_PATH,
    POSSIBLE_LONS_FLAGS,
    POSSIBLE_SHORT_FLAGS,
    TRANSFORMATION_FLAGS,
)


def is_flags(flags: str) -> int | set:
    """Проверяет и преобразует флаги командной строки.

    Args:
        flags: Строка с флагами (--long или -short)

    Returns:
        set: Множество флагов при успехе
        int: 1 при ошибке, 0 если не флаги
    """
    if flags.startswith('-') and not flags.startswith('--'):
        set_of_flags = set(flags[1:])

        if set_of_flags.issubset(POSSIBLE_SHORT_FLAGS):
            return set_of_flags
        else:
            return 1

    elif flags.startswith('--'):
        flags = flags[2:]

        if flags in POSSIBLE_LONS_FLAGS:
            return set(TRANSFORMATION_FLAGS[flags])
        else:
            return 1

    else:
        return 0


def is_valid_filename(filename: str) -> bool:
    """Проверяет валидность имени файла.

    Args:
        filename: Имя файла для проверки

    Returns:
        bool: True если имя валидно
    """
    if len(filename) > 255:
        return False

    if not filename or filename == '.':
        return False

    invalid_chars = set('&`?*.\\/|')

    for char in filename:
        if char in invalid_chars:
            return False

    return True


def is_valid_dirname(dirname: str) -> bool:
    """Проверяет валидность имени директории.

    Args:
        dirname: Имя директории для проверки

    Returns:
        bool: True если имя валидно
    """
    if len(dirname) > 255:
        return False

    if not dirname or dirname == '.' or dirname == '..':
        return False

    invalid_chars = set('&`?*.\\/|')

    for char in dirname:
        if char in invalid_chars:
            return False

    return True


def extracting_files(
    temp_dir_path: Path, extract_folder_path: Path, archive_name: str
) -> int:
    """Извлекает файлы из временной директории с обработкой конфликтов.

    Args:
        temp_dir_path: Путь к временной директории
        extract_folder_path: Путь для извлечения
        archive_name: Имя архива

    Returns:
        int: 0 при успехе
    """
    print(f'Archive:  {archive_name}')

    all_files = list(temp_dir_path.rglob('*'))

    conflict_files = []
    no_conflict_files = []

    for file_path in all_files:
        if file_path.is_file():
            relative_path = file_path.relative_to(temp_dir_path)
            final_file_path = extract_folder_path / relative_path

            if final_file_path.exists():
                conflict_files.append(
                    (file_path, relative_path, final_file_path)
                )
            else:
                no_conflict_files.append(
                    (file_path, relative_path, final_file_path)
                )

    for file_path, relative_path, final_file_path in no_conflict_files:
        final_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, final_file_path)
        print(f'  inflating: {relative_path}')

    replace_all = False
    skip_all = False

    for file_path, relative_path, final_file_path in conflict_files:
        if skip_all:
            print(f'  skipping: {relative_path}')
            continue

        if replace_all:
            shutil.copy2(file_path, final_file_path)
            print(f'  inflating: {relative_path}')
            continue

        print(
            f'replace {relative_path}? [y]es, [n]o, [A]ll, [s]kip all: ',
            end='',
        )
        answer = input().strip().lower()

        if answer in ('y', 'yes'):
            shutil.copy2(file_path, final_file_path)
            print(f'  inflating: {relative_path}')
        elif answer in ('a', 'all'):
            replace_all = True
            shutil.copy2(file_path, final_file_path)
            print(f'  inflating: {relative_path}')
        elif answer in ('s', 'skip'):
            skip_all = True
            print(f'  skipping: {relative_path}')
        elif answer in ('n', 'no'):
            print(f'  skipping: {relative_path}')
        else:
            print(f'  skipping: {relative_path}')

    return 0


def write_history(line: str) -> int:
    """Записывает команду в файл истории.

    Args:
        line: Команда для записи

    Returns:
        int: 0 при успехе
    """
    if HISTORY_PATH.stat().st_size == 0:
        with open(HISTORY_PATH, 'w') as f:
            f.write(f'1. {line}\n')
        return 0

    history_lines = open(HISTORY_PATH).readlines()
    last_line_number, *_ = history_lines[-1].split()
    last_number = int(last_line_number[:-1])

    with open(HISTORY_PATH, 'a') as f:
        f.write(f'{last_number + 1}. {line}\n')
    return 0
