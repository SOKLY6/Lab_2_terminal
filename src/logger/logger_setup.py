import logging

terminal_logger = logging.getLogger('terminal_logger')
terminal_logger.setLevel(logging.INFO)

terminal_logger_handler = logging.FileHandler('src/logger/shell.log', mode='a')
terminal_logger_formater = logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s'
)

terminal_logger_handler.setFormatter(terminal_logger_formater)

terminal_logger.addHandler(terminal_logger_handler)
