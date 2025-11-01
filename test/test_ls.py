import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import ls


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов ls"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file1:
        temp_file1.write("file1 content")
        temp_path1 = temp_file1.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file2:
        temp_file2.write("file2 content")
        temp_path2 = temp_file2.name
    
    yield temp_path1, temp_path2
    
    Path(temp_path1).unlink()
    Path(temp_path2).unlink()


@pytest.fixture
def mock_temp_directory():
    """Создает временную директорию для тестов ls"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_ls_without_arguments(capsys):
    """ls без аргументов выводит содержимое текущей директории"""
    test_flags = set()
    test_arguments = []
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert len(captured.out) > 0


def test_ls_nonexistent_file(capsys):
    """ls с несуществующим файлом показывает ошибку"""
    test_flags = set()
    test_arguments = ['/nonexistent/goose/file/path']
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == "ls: cannot access '/nonexistent/goose/file/path': No such file or directory\n"


def test_ls_l_flag(mock_temp_files, capsys):
    """ls с флагом -l показывает длинный формат"""
    temp_path1, _ = mock_temp_files
    
    test_flags = {'l'}
    test_arguments = [temp_path1]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert Path(temp_path1).name in captured.out
    assert "rw" in captured.out


def test_ls_a_flag(mock_temp_directory, capsys):
    """ls с флагом -a показывает скрытые файлы"""
    temp_path = Path(mock_temp_directory)
    hidden_file = temp_path / ".hidden_goose_file"
    hidden_file.write_text("hidden content")
    
    normal_file = temp_path / "visible_goose_file"
    normal_file.write_text("visible content")
    
    test_flags = {'a'}
    test_arguments = [mock_temp_directory]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert ".hidden_goose_file" in captured.out
    assert "visible_goose_file" in captured.out


def test_ls_with_incorrect_flags(capsys):
    """ls с неправильными флагами возвращает ошибку"""
    test_flags = {'x', 'y', 'z'}
    test_arguments = ['.']
    
    with patch('src.ubuntu_commands.ls.terminal_logger'):
        result = ls.ls(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "ls: does not support the flags:" in captured.out
        assert "x" in captured.out
        assert "y" in captured.out
        assert "z" in captured.out


def test_ls_multiple_dirs(mock_temp_directory, capsys):
    """ls с несколькими директориями показывает содержимое"""
    with tempfile.TemporaryDirectory() as temp_dir2:
        test_flags = set()
        test_arguments = [mock_temp_directory, temp_dir2]
        
        result = ls.ls(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert mock_temp_directory in captured.out or temp_dir2 in captured.out


def test_ls_empty_dir(mock_temp_directory, capsys):
    """ls с пустой директорией возвращает пустой вывод"""
    test_flags = set()
    test_arguments = [mock_temp_directory]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == "\n"


def test_ls_single_file_argument(mock_temp_files, capsys):
    """ls с одним файлом в аргументах"""
    temp_path1, _ = mock_temp_files
    
    test_flags = set()
    test_arguments = [temp_path1]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert Path(temp_path1).name in captured.out


def test_ls_multiple_files(mock_temp_files, capsys):
    """ls с несколькими файлами в аргументах"""
    temp_path1, temp_path2 = mock_temp_files
    
    test_flags = set()
    test_arguments = [temp_path1, temp_path2]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert Path(temp_path1).name in captured.out
    assert Path(temp_path2).name in captured.out


def test_ls_mixed_files_and_dirs(mock_temp_files, mock_temp_directory, capsys):
    """ls с mix файлов и директорий"""
    temp_path1, _ = mock_temp_files
    
    test_flags = set()
    test_arguments = [temp_path1, mock_temp_directory]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert Path(temp_path1).name in captured.out


def test_ls_la_flags_combined(mock_temp_directory, capsys):
    """ls с комбинацией флагов -l -a"""
    temp_path = Path(mock_temp_directory)
    hidden_file = temp_path / ".hidden_goose"
    hidden_file.write_text("hidden")
    
    normal_file = temp_path / "visible_goose"
    normal_file.write_text("visible")
    
    test_flags = {'l', 'a'}
    test_arguments = [mock_temp_directory]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert ".hidden_goose" in captured.out
    assert "visible_goose" in captured.out


def test_ls_nonexistent_file_continues_with_others(mock_temp_files, capsys):
    """ls продолжает работу после несуществующего файла"""
    temp_path1, _ = mock_temp_files
    
    test_flags = set()
    test_arguments = ['/nonexistent/goose', temp_path1]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "ls: cannot access '/nonexistent/goose': No such file or directory" in captured.out
    assert Path(temp_path1).name in captured.out


def test_ls_with_none_flags(mock_temp_files, capsys):
    """ls с flags=None работает корректно"""
    temp_path1, _ = mock_temp_files
    
    test_flags = None
    test_arguments = [temp_path1]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert Path(temp_path1).name in captured.out


def test_ls_directory_with_hidden_files(mock_temp_directory, capsys):
    """ls директории со скрытыми файлами без флага -a"""
    temp_path = Path(mock_temp_directory)
    hidden_file = temp_path / ".hidden_file"
    hidden_file.write_text("hidden")
    
    normal_file = temp_path / "normal_file"
    normal_file.write_text("normal")
    
    test_flags = set()
    test_arguments = [mock_temp_directory]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "normal_file" in captured.out
    assert ".hidden_file" not in captured.out


def test_ls_directory_sorting(mock_temp_directory, capsys):
    """ls сортирует файлы по имени"""
    temp_path = Path(mock_temp_directory)
    file_c = temp_path / "c_file.txt"
    file_a = temp_path / "a_file.txt"
    file_b = temp_path / "b_file.txt"
    
    file_c.write_text("content")
    file_a.write_text("content")
    file_b.write_text("content")
    
    test_flags = set()
    test_arguments = [mock_temp_directory]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    output = captured.out

    a_pos = output.find("a_file.txt")
    b_pos = output.find("b_file.txt")
    c_pos = output.find("c_file.txt")
    
    assert a_pos < b_pos < c_pos


def test_ls_multiple_arguments_with_separators(mock_temp_directory, capsys):
    """ls с несколькими аргументами показывает разделители"""
    with tempfile.TemporaryDirectory() as temp_dir2:
        test_flags = set()
        test_arguments = [mock_temp_directory, temp_dir2]
        
        result = ls.ls(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        # Должны быть названия директорий в выводе
        assert mock_temp_directory in captured.out or f"{mock_temp_directory}/:" in captured.out


def test_ls_long_format_details(mock_temp_files, capsys):
    """ls -l показывает детальную информацию"""
    temp_path1, _ = mock_temp_files
    
    test_flags = {'l'}
    test_arguments = [temp_path1]
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    output = captured.out
    assert "rw" in output
    assert Path(temp_path1).name in output


def test_ls_current_directory(capsys):
    """ls текущей директории"""
    test_flags = set()
    test_arguments = ['.']
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert len(captured.out) > 0


def test_ls_parent_directory(capsys):
    """ls родительской директории"""
    test_flags = set()
    test_arguments = ['..']
    
    result = ls.ls(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert len(captured.out) > 0


if __name__ == '__main__':
    pytest.main()