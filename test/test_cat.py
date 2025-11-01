import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import cat


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов cat"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file1:
        temp_file1.write("file1 content line 1\nfile1 content line 2")
        temp_path1 = temp_file1.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file2:
        temp_file2.write("file2 content")
        temp_path2 = temp_file2.name
    
    yield temp_path1, temp_path2
    
    Path(temp_path1).unlink()
    Path(temp_path2).unlink()


def test_cat_single_file(mock_temp_files, capsys):
    """cat с одним файлом показывает его содержимое"""
    temp_path1, _ = mock_temp_files
    
    result = cat.cat([temp_path1], None)
    
    captured = capsys.readouterr()
    expected_output = "file1 content line 1\nfile1 content line 2"
    
    assert result == 0
    assert captured.out.strip() == expected_output


def test_cat_multiple_files(mock_temp_files, capsys):
    """cat с несколькими файлами показывает их содержимое"""
    temp_path1, temp_path2 = mock_temp_files
    
    result = cat.cat([temp_path1, temp_path2], None)
    
    captured = capsys.readouterr()
    expected_output = "file1 content line 1\nfile1 content line 2\nfile2 content"
    
    assert result == 0
    assert captured.out.strip() == expected_output


def test_cat_nonexistent_file(capsys):
    """cat с несуществующим файлом показывает ошибку"""
    result = cat.cat(['/nonexistent/file.txt'], None)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "cat: /nonexistent/file.txt: No such file or directory" in captured.out


def test_cat_directory(capsys):
    """cat с директорией показывает ошибку"""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = cat.cat([temp_dir], None)
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert f"cat: {temp_dir}: Is a directory" in captured.out


def test_cat_mixed_files_and_dirs(mock_temp_files, capsys):
    """cat с mix файлов и директорий обрабатывает все"""
    temp_path1, temp_path2 = mock_temp_files
    
    with tempfile.TemporaryDirectory() as temp_dir:
        result = cat.cat([temp_path1, temp_dir, temp_path2, '/nonexistent.txt'], None)
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "file1 content line 1" in captured.out
        assert "file2 content" in captured.out
        assert f"cat: {temp_dir}: Is a directory" in captured.out
        assert "cat: /nonexistent.txt: No such file or directory" in captured.out


def test_cat_with_flags(capsys):
    """cat с флагами показывает ошибку о неподдерживаемых флагах"""
    result = cat.cat(['file.txt'], {'n', 'E'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "cat: does not support the flags:" in captured.out
    assert "n" in captured.out
    assert "E" in captured.out


def test_cat_empty_file(capsys):
    """cat с пустым файлом показывает пустой вывод"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
        temp_path = temp_file.name
    
    try:
        result = cat.cat([temp_path], None)
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert captured.out == "\n"
        
    finally:
        Path(temp_path).unlink()


def test_cat_special_characters(capsys):
    """cat с файлом содержащим специальные символы"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
        temp_file.write("line with\ttab\nline with\nnewline")
        temp_path = temp_file.name
    
    try:
        result = cat.cat([temp_path], None)
        
        captured = capsys.readouterr()
        expected_output = "line with\ttab\nline with\nnewline"
        
        assert result == 0
        assert captured.out.strip() == expected_output
        
    finally:
        Path(temp_path).unlink()


def test_cat_no_arguments(capsys):
    """cat без аргументов не показывает ничего"""
    result = cat.cat([], None)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == ""