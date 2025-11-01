import re
import typing
from pathlib import Path

from logger.logger_setup import terminal_logger

correct_flags = {'r', 'i'}


def grep(arguments: list[str], flags: set[typing.Any] | None = None) -> int:
    """Ищет текст в файлах по регулярному выражению.

    Args:
        arguments: Паттерн для поиска и пути к файлам
        flags: 'r' - рекурсивный поиск, 'i' - игнорировать регистр

    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if flags is None:
        flags = set()

    if not flags.issubset(correct_flags):
        print(
            'grep: does not support the flags:',
            f' {", ".join(flags.difference(correct_flags))}',
        )
        terminal_logger.error(
            'grep: does not support the flags:',
            f' {", ".join(flags.difference(correct_flags))}',
        )
        return 1

    recursive = False
    ignore_case = False

    if 'r' in flags:
        recursive = True
    if 'i' in flags:
        ignore_case = True

    if len(arguments) < 2:
        print('Usage: grep [OPTION]... PATTERNS [FILE]...')
        terminal_logger.error('grep: insufficient arguments')
        return 1

    else:
        pattern = arguments[0]

        if ignore_case:
            pattern = arguments[0].lower()

        for argument in arguments[1:]:
            argument_path = Path(argument)

            if not argument_path.exists():
                print(f'grep: {argument}: No such file or directory')
                terminal_logger.error(
                    f'grep: {argument}: No such file or directory'
                )
                continue

            if argument_path.is_file():
                line_number = 1

                try:
                    with open(argument_path) as file:
                        for line in file:
                            if ignore_case:
                                if re.search(pattern, line.lower()):
                                    print(
                                        f'{argument}:',
                                        f' {line_number}. {line}',
                                        end='',
                                    )
                                    terminal_logger.info(
                                        f'grep: {argument}:',
                                        f'{line_number} - found',
                                    )

                            else:
                                if re.search(pattern, line):
                                    print(
                                        f'{argument}:',
                                        f' {line_number}. {line}',
                                        end='',
                                    )
                                    terminal_logger.info(
                                        f'grep: {argument}:',
                                        f'{line_number} - found',
                                    )

                            line_number += 1
                        print()
                    continue
                except UnicodeDecodeError:
                    print(f'grep: {argument}: Binary file matches')
                    terminal_logger.error(
                        f'grep: {argument}: Binary file matches'
                    )
                except Exception as e:
                    print(f'grep: {argument}: {e}')
                    terminal_logger.error(f'grep: {argument}: {e}')

            if argument_path.is_dir():
                if not recursive:
                    print(f'grep: {argument}: Is a directory')
                    terminal_logger.error(f'grep: {argument}: Is a directory')
                    continue

                for file_path in argument_path.rglob('*'):
                    if file_path.is_dir():
                        continue

                    line_number = 1

                    try:
                        with open(file_path) as file:
                            for line in file:
                                if ignore_case:
                                    if bool(re.match(pattern, line.lower())):
                                        print(
                                            f'{file_path.name}:',
                                            f' {line_number}. {line}',
                                            end='',
                                        )
                                        terminal_logger.info(
                                            f'grep: {file_path.name}:',
                                            f'{line_number} - found',
                                        )

                                else:
                                    if bool(re.match(pattern, line)):
                                        print(
                                            f'{file_path.name}:',
                                            f' {line_number}. {line}',
                                            end='',
                                        )
                                        terminal_logger.info(
                                            f'grep: {file_path.name}:',
                                            f'{line_number} - found',
                                        )

                                line_number += 1
                        continue
                    except UnicodeDecodeError:
                        print(f'grep: {file_path}: Binary file matches')
                        terminal_logger.error(
                            f'grep: {file_path}: Binary file matches'
                        )
                    except Exception as e:
                        print(f'grep: {file_path}: {e}')
                        terminal_logger.error(f'grep: {file_path}: {e}')

        return 0
