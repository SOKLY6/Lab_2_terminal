import typing

from constants import HISTORY_PATH
from logger.logger_setup import terminal_logger


def history(argument: list[str], flags: set[typing.Any] | None = None) -> int:
    """Показывает историю команд.

    Args:
        argument: Количество последних команд для показа (опционально)
        flags: Флаги (не поддерживаются)

    Returns:
        int: 0 при успехе, 1 при ошибке
    """
    if not argument:
        history_lines = open(HISTORY_PATH).readlines()

        for history_line in history_lines:
            print(history_line, end='')

        terminal_logger.info('history: success')
        return 0

    elif len(argument) > 1:
        print('-bash: history: too many arguments')
        terminal_logger.error(f'history: too many arguments: {argument}')
        return 1

    else:
        try:
            number = int(argument[0])
        except ValueError:
            print(f'-bash: history: {argument[0]}: numeric argument required')
            terminal_logger.error(
                f'history: {argument[0]}: numeric argument required'
            )
            return 1

        if number < 0:
            print(f'-bash: history: {number}: invalid option')
            terminal_logger.error(f'history: {number}: invalid option')
            return 1

        elif number == 0:
            terminal_logger.info(f'history: {argument[0]} - success')
            return 0

        else:
            history_lines = open(HISTORY_PATH).readlines()
            last_line_number, *_ = history_lines[-1].split()
            last_number = int(last_line_number[:-1])

            if last_number < number:
                number = last_number

            for history_line in history_lines[last_number - number :]:
                if number:
                    print(history_line, end='')
                    number -= 1
                else:
                    terminal_logger.info(f'history: {argument[0]} - success')
                    return 0
            terminal_logger.info(f'history: {argument[0]} - success')
            return 0
