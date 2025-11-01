import pytest
import tempfile
import os
from unittest.mock import patch
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.ubuntu_commands import history


@pytest.fixture
def mock_history_file():
    """Создает временный файл истории для тестов"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.history') as f:
        f.write("1. ls\n")
        f.write("2. cd /home\n")
        f.write("3. pwd\n")
        f.write("4. cat file.txt\n")
        f.write("5. mkdir test\n")
        temp_path = f.name
    
    with patch('src.ubuntu_commands.history.HISTORY_PATH', temp_path):
        yield temp_path
    
    os.unlink(temp_path)


def test_history_no_args_shows_all_commands(mock_history_file, capsys):
    """history без аргументов показывает всю историю"""
    result = history.history([], None)
    
    captured = capsys.readouterr()
    expected_output = "1. ls\n2. cd /home\n3. pwd\n4. cat file.txt\n5. mkdir test\n"
    
    assert result == 0
    assert captured.out == expected_output


def test_history_too_many_args_shows_error(mock_history_file, capsys):
    """history с более чем одним аргументом показывает ошибку"""
    result = history.history(["5", "10"], None)
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "-bash: history: too many arguments\n"


def test_history_invalid_numeric_arg_shows_error(mock_history_file, capsys):
    """history с нечисловым аргументом показывает ошибку"""
    result = history.history(["abc"], None)
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "-bash: history: abc: numeric argument required\n"


def test_history_negative_number_shows_error(mock_history_file, capsys):
    """history с отрицательным числом показывает ошибку"""
    result = history.history(["-5"], None)
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "-bash: history: -5: invalid option\n"


def test_history_zero_returns_success(mock_history_file):
    """history с аргументом 0 возвращает успех"""
    result = history.history(["0"], None)
    
    assert result == 0


def test_history_small_number_shows_last_n_commands(mock_history_file, capsys):
    """history с малым числом показывает последние N команд"""
    result = history.history(["3"], None)
    
    captured = capsys.readouterr()
    expected_output = "3. pwd\n4. cat file.txt\n5. mkdir test\n"
    
    assert result == 0
    assert captured.out == expected_output


def test_history_large_number_shows_all_commands(mock_history_file, capsys):
    """history с большим числом показывает все команды"""
    result = history.history(["10"], None)
    
    captured = capsys.readouterr()
    expected_output = "1. ls\n2. cd /home\n3. pwd\n4. cat file.txt\n5. mkdir test\n"
    
    assert result == 0
    assert captured.out == expected_output


def test_history_exact_number_shows_all_commands(mock_history_file, capsys):
    """history с числом равным количеству команд показывает все команды"""
    result = history.history(["5"], None)
    
    captured = capsys.readouterr()
    expected_output = "1. ls\n2. cd /home\n3. pwd\n4. cat file.txt\n5. mkdir test\n"
    
    assert result == 0
    assert captured.out == expected_output


def test_history_one_shows_last_command(mock_history_file, capsys):
    """history с аргументом 1 показывает последнюю команду"""
    result = history.history(["1"], None)
    
    captured = capsys.readouterr()
    expected_output = "5. mkdir test\n"
    
    assert result == 0
    assert captured.out == expected_output


def test_history_empty_file_returns_empty_output(mock_history_file, capsys):
    """history с пустым файлом истории возвращает пустой вывод"""
    with open(mock_history_file, 'w') as f:
        f.write("")
    
    result = history.history([], None)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == ""


def test_history_with_flags_parameter(mock_history_file, capsys):
    """history работает с параметром flags (игнорирует его)"""
    result = history.history([], flags={'some_flag'})
    
    captured = capsys.readouterr()
    expected_output = "1. ls\n2. cd /home\n3. pwd\n4. cat file.txt\n5. mkdir test\n"
    
    assert result == 0
    assert captured.out == expected_output


def test_history_file_with_gaps_in_numbers(mock_history_file, capsys):
    """history работает с файлом где есть пропуски в номерах"""
    with open(mock_history_file, 'w') as f:
        f.write("1. first\n")
        f.write("3. third\n")
        f.write("5. fifth\n")
        f.write("7. seventh\n")
    
    result = history.history(["2"], None)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "error" not in captured.out.lower()


def test_history_single_line_file(mock_history_file, capsys):
    """history работает с файлом содержащим одну команду"""
    with open(mock_history_file, 'w') as f:
        f.write("1. single command\n")
    
    result = history.history([], None)
    
    captured = capsys.readouterr()
    expected_output = "1. single command\n"
    
    assert result == 0
    assert captured.out == expected_output


def test_history_number_greater_than_available_commands(mock_history_file, capsys):
    """history с числом большим чем доступно команд показывает все команды"""
    result = history.history(["100"], None)
    
    captured = capsys.readouterr()
    expected_output = "1. ls\n2. cd /home\n3. pwd\n4. cat file.txt\n5. mkdir test\n"
    
    assert result == 0
    assert captured.out == expected_output