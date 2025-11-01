import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import grep


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов grep"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file1:
        temp_file1.write("hello world\ntest pattern\nanother line\n")
        temp_path1 = temp_file1.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file2:
        temp_file2.write("HELLO world\nTEST pattern\nanother line\n")
        temp_path2 = temp_file2.name
    
    yield temp_path1, temp_path2
    
    Path(temp_path1).unlink()
    Path(temp_path2).unlink()


@pytest.fixture
def mock_temp_directory():
    """Создает временную директорию для тестов grep"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_grep_empty_arguments(capsys):
    """grep без аргументов показывает ошибку"""
    result = grep.grep([], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "Usage: grep [OPTION]... PATTERNS [FILE]...\n"


def test_grep_single_argument(capsys):
    """grep с одним аргументом показывает ошибку"""
    result = grep.grep(['pattern'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "Usage: grep [OPTION]... PATTERNS [FILE]...\n"


def test_grep_incorrect_flags(capsys):
    """grep с неправильными флагами показывает ошибку"""
    result = grep.grep(['pattern', 'file.txt'], {'x', 'y'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "grep: does not support the flags:" in captured.out
    assert "x" in captured.out
    assert "y" in captured.out


def test_grep_nonexistent_file(capsys):
    """grep с несуществующим файлом показывает ошибку"""
    result = grep.grep(['pattern', '/nonexistent.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == "grep: /nonexistent.txt: No such file or directory\n"


def test_grep_directory_without_r_flag(mock_temp_directory, capsys):
    """grep с директорией без флага -r показывает ошибку"""
    result = grep.grep(['pattern', mock_temp_directory], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == f"grep: {mock_temp_directory}: Is a directory\n"


def test_grep_successful_file_search(mock_temp_files, capsys):
    """grep успешно находит паттерн в файле"""
    temp_path1, _ = mock_temp_files
    
    result = grep.grep(['pattern', temp_path1], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "test pattern" in captured.out
    assert "2." in captured.out


def test_grep_successful_case_insensitive(mock_temp_files, capsys):
    """grep успешно находит паттерн с игнорированием регистра"""
    _, temp_path2 = mock_temp_files
    
    result = grep.grep(['test', temp_path2], {'i'})
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "TEST pattern" in captured.out


def test_grep_no_matches(mock_temp_files, capsys):
    """grep не находит совпадений и не показывает ошибку"""
    temp_path1, _ = mock_temp_files
    
    result = grep.grep(['nonexistentpattern', temp_path1], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "nonexistentpattern" not in captured.out


def test_grep_binary_file_error(capsys):
    """grep показывает ошибку для бинарного файла"""
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as test_file:
        test_file.write(b'\xff\xfe\x00\x01')
        test_path = test_file.name
    
    try:
        result = grep.grep(['pattern', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "Binary file matches" in captured.out
        
    finally:
        Path(test_path).unlink()


def test_grep_recursive_search(mock_temp_directory, capsys):
    """grep успешно ищет рекурсивно в директории"""
    test_file_path = Path(mock_temp_directory) / "test.txt"
    with open(test_file_path, 'w') as f:
        f.write("hello world\ntest pattern\n")
    
    result = grep.grep(['test', mock_temp_directory], {'r'})
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "test pattern" in captured.out


def test_grep_multiple_files(mock_temp_files, capsys):
    """grep успешно ищет в нескольких файлах"""
    temp_path1, temp_path2 = mock_temp_files
    
    result = grep.grep(['pattern', temp_path1, temp_path2], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "test pattern" in captured.out
    assert "TEST pattern" in captured.out


def test_grep_file_read_error(mock_temp_files, capsys):
    """grep показывает ошибку при проблемах с чтением файла"""
    temp_path1, _ = mock_temp_files
    
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        result = grep.grep(['pattern', temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "Permission denied" in captured.out


def test_grep_regex_pattern(capsys):
    """grep успешно работает с regex паттернами"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_file.write("test123\nabc456\nhello world\n")
        test_path = test_file.name
    
    try:
        result = grep.grep([r'test\d+', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "test123" in captured.out
        
    finally:
        Path(test_path).unlink()


def test_grep_none_flags_initialization(capsys):
    """grep корректно обрабатывает flags=None"""
    result = grep.grep(['pattern', 'file.txt'], None)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "grep: file.txt: No such file or directory" in captured.out


def test_grep_complex_pattern(capsys):
    """grep успешно работает со сложными паттернами"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_file.write("email@example.com\nnot an email\nanother@test.com\n")
        test_path = test_file.name
    
    try:
        result = grep.grep(['@', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "@" in captured.out
        
    finally:
        Path(test_path).unlink()


def test_grep_empty_file(capsys):
    """grep корректно обрабатывает пустой файл"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_path = test_file.name
    
    try:
        result = grep.grep(['pattern', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        
    finally:
        Path(test_path).unlink()


def test_grep_special_characters(capsys):
    """grep успешно ищет специальные символы"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_file.write("line with $pecial char@cters\nnormal line\n")
        test_path = test_file.name
    
    try:
        result = grep.grep([r'\$', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "$pecial" in captured.out
        
    finally:
        Path(test_path).unlink()


def test_grep_multiple_patterns_in_file(capsys):
    """grep находит несколько совпадений в файле"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_file.write("pattern here\nanother pattern\nno match\npattern again\n")
        test_path = test_file.name
    
    try:
        result = grep.grep(['pattern', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert captured.out.count("pattern") >= 3
        
    finally:
        Path(test_path).unlink()


def test_grep_recursive_with_subdirectories(mock_temp_directory, capsys):
    """grep рекурсивно ищет в поддиректориях"""
    subdir = Path(mock_temp_directory) / "subdir"
    subdir.mkdir()
    test_file_path = subdir / "test.txt"
    with open(test_file_path, 'w') as f:
        f.write("hidden pattern\n")
    
    result = grep.grep(['hidden', mock_temp_directory], {'r'})
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "hidden pattern" in captured.out


def test_grep_line_number_display(capsys):
    """grep отображает номера строк"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_file.write("first line\nsecond line\npattern here\nfourth line\n")
        test_path = test_file.name
    
    try:
        result = grep.grep(['pattern', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "3." in captured.out
        
    finally:
        Path(test_path).unlink()


def test_grep_exact_match(capsys):
    """grep находит точные совпадения"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_file.write("exact match\nnot exact\nEXACT MATCH\n")
        test_path = test_file.name
    
    try:
        result = grep.grep(['exact match', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "exact match" in captured.out
        assert "EXACT MATCH" not in captured.out
        
    finally:
        Path(test_path).unlink()


def test_grep_with_newlines(capsys):
    """grep корректно обрабатывает разные типы переносов строк"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as test_file:
        test_file.write("line1\nline2\r\nline3\npattern found\nline5\n")
        test_path = test_file.name
    
    try:
        result = grep.grep(['pattern', test_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "pattern found" in captured.out
        
    finally:
        Path(test_path).unlink()


def test_grep_multiple_files_with_errors(mock_temp_files, capsys):
    """grep продолжает работу при ошибках в нескольких файлах"""
    temp_path1, _ = mock_temp_files
    
    result = grep.grep(['pattern', temp_path1, '/nonexistent.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "test pattern" in captured.out
    assert "No such file or directory" in captured.out


def test_grep_case_sensitive_by_default(mock_temp_files, capsys):
    """grep по умолчанию чувствителен к регистру"""
    _, temp_path2 = mock_temp_files
    
    result = grep.grep(['test', temp_path2], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "TEST pattern" not in captured.out


if __name__ == '__main__':
    pytest.main()