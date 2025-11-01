import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import rm


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов rm"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file1:
        temp_file1.write("file1 content")
        temp_path1 = temp_file1.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file2:
        temp_file2.write("file2 content")
        temp_path2 = temp_file2.name
    
    yield temp_path1, temp_path2
    
    if Path(temp_path1).exists():
        Path(temp_path1).unlink()
    if Path(temp_path2).exists():
        Path(temp_path2).unlink()


@pytest.fixture
def mock_temp_directory():
    """Создает временную директорию для тестов rm"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_trash_path():
    """Создает временную корзину для тестов rm"""
    with tempfile.TemporaryDirectory() as trash_dir:
        with patch('src.ubuntu_commands.rm.TRASH_PATH', Path(trash_dir)):
            yield trash_dir


def test_rm_empty_arguments(capsys):
    """rm без аргументов показывает ошибку"""
    result = rm.rm([], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "rm: missing operand\n"


def test_rm_nonexistent_file(capsys):
    """rm с несуществующим файлом показывает ошибку"""
    result = rm.rm(['/nonexistent/file.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "rm: cannot remove '/nonexistent/file.txt': No such file or directory" in captured.out


def test_rm_successful_file(mock_temp_files, mock_trash_path, capsys):
    """rm успешно удаляет файл"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history:
        result = rm.rm([temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        trash_files = list(Path(mock_trash_path).iterdir())
        assert len(trash_files) == 1
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_directory_without_r_flag(mock_temp_directory, capsys):
    """rm с директорией без флага -r показывает ошибку"""
    result = rm.rm([mock_temp_directory], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert f"rm: cannot remove {mock_temp_directory}: Is a directory" in captured.out


def test_rm_directory_with_r_flag(mock_temp_directory, mock_trash_path, capsys):
    """rm успешно удаляет директорию с флагом -r"""
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history, \
         patch('builtins.input', return_value='y'):
        result = rm.rm([mock_temp_directory], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(mock_temp_directory).exists()
        trash_items = list(Path(mock_trash_path).iterdir())
        assert len(trash_items) == 1
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_directory_with_r_flag_declined(mock_temp_directory, mock_trash_path, capsys):
    """rm пропускает директорию при отказе пользователя"""
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history, \
         patch('builtins.input', return_value='n'):
        result = rm.rm([mock_temp_directory], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert Path(mock_temp_directory).exists()
        trash_items = list(Path(mock_trash_path).iterdir())
        assert len(trash_items) == 0
        assert "rm: skipping directory" in captured.out
        assert len(mock_history) == 0 


def test_rm_multiple_files(mock_temp_files, mock_trash_path, capsys):
    """rm успешно удаляет несколько файлов"""
    temp_path1, temp_path2 = mock_temp_files
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history:
        result = rm.rm([temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        assert not Path(temp_path2).exists()
        trash_files = list(Path(mock_trash_path).iterdir())
        assert len(trash_files) == 2
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_mixed_files_and_dirs(mock_temp_files, mock_temp_directory, mock_trash_path, capsys):
    """rm обрабатывает mix файлов и директорий"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history, \
         patch('builtins.input', return_value='y'):
        result = rm.rm([temp_path1, mock_temp_directory], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        assert not Path(mock_temp_directory).exists()
        trash_items = list(Path(mock_trash_path).iterdir())
        assert len(trash_items) == 2
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_file_remove_error(mock_temp_files, capsys):
    """rm показывает ошибку при сбое удаления файла"""
    temp_path1, _ = mock_temp_files
    
    with patch('shutil.copy2', side_effect=Exception("Permission denied")):
        result = rm.rm([temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "rm: cannot remove" in captured.out
        assert "Permission denied" in captured.out


def test_rm_directory_remove_error(mock_temp_directory, capsys):
    """rm показывает ошибку при сбое удаления директории"""
    with patch('builtins.input', return_value='y'), \
         patch('shutil.copytree', side_effect=Exception("Permission denied")):
        result = rm.rm([mock_temp_directory], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "rm: cannot remove" in captured.out
        assert "Permission denied" in captured.out


def test_rm_with_incorrect_flags(capsys):
    """rm с неправильными флагами показывает ошибку"""
    result = rm.rm(['file.txt'], {'x', 'y'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "rm: does not support the flags:" in captured.out
    assert "x" in captured.out
    assert "y" in captured.out


def test_rm_none_flags_initialization(mock_temp_files, mock_trash_path, capsys):
    """rm корректно обрабатывает flags=None"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history:
        result = rm.rm([temp_path1], None)
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_multiple_items_with_errors(mock_temp_files, mock_trash_path, capsys):
    """rm продолжает работу при ошибках с несколькими элементами"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history:
        result = rm.rm([temp_path1, '/nonexistent.txt'], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        assert "rm: cannot remove '/nonexistent.txt': No such file or directory" in captured.out
        trash_files = list(Path(mock_trash_path).iterdir())
        assert len(trash_files) == 1
        assert len(mock_history) == 1


def test_rm_directory_with_contents(mock_temp_directory, mock_trash_path, capsys):
    """rm удаляет директорию с содержимым"""
    temp_path = Path(mock_temp_directory)
    inner_file = temp_path / "inner_file.txt"
    inner_file.write_text("inner content")
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history, \
         patch('builtins.input', return_value='y'):
        result = rm.rm([mock_temp_directory], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(mock_temp_directory).exists()
        trash_items = list(Path(mock_trash_path).iterdir())
        assert len(trash_items) == 1
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_trash_conflict_resolution(mock_temp_directory, mock_trash_path, capsys):
    """rm разрешает конфликты имен в корзине"""
    temp_path = Path(mock_temp_directory)
    
    conflict_path = Path(mock_trash_path) / temp_path.name
    conflict_path.mkdir()
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history, \
         patch('builtins.input', return_value='y'):
        result = rm.rm([mock_temp_directory], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(mock_temp_directory).exists()
        trash_items = list(Path(mock_trash_path).iterdir())
        assert len(trash_items) == 1
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_nonexistent_item_type(mock_temp_files, capsys):
    """rm показывает ошибку для элемента, который не файл и не директория"""
    temp_path1, _ = mock_temp_files
    
    with patch('pathlib.Path.is_file', return_value=False), \
         patch('pathlib.Path.is_dir', return_value=False):
        result = rm.rm([temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "rm: cannot remove" in captured.out
        assert "No such file or directory" in captured.out


def test_rm_empty_directory(mock_temp_directory, mock_trash_path, capsys):
    """rm удаляет пустую директорию с флагом -r"""
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history, \
         patch('builtins.input', return_value='y'):
        result = rm.rm([mock_temp_directory], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(mock_temp_directory).exists()
        trash_items = list(Path(mock_trash_path).iterdir())
        assert len(trash_items) == 1
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_single_file_in_directory(mock_temp_directory, mock_trash_path, capsys):
    """rm удаляет одиночный файл в директории"""
    temp_path = Path(mock_temp_directory)
    test_file = temp_path / "test_file.txt"
    test_file.write_text("test content")
    
    with patch('src.ubuntu_commands.rm.FOR_UNDO_HISTORY', []) as mock_history:
        result = rm.rm([str(test_file)], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not test_file.exists()
        trash_files = list(Path(mock_trash_path).iterdir())
        assert len(trash_files) == 1
        assert captured.out == ""
        assert len(mock_history) == 1


def test_rm_forbidden_paths_root(mock_trash_path, capsys):
    """rm запрещает удаление корневой директории"""
    with patch('pathlib.Path.resolve', return_value=Path('/')), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.is_dir', return_value=True), \
         patch('builtins.input', return_value='y'):
        result = rm.rm(['/'], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert any(msg in captured.out for msg in [
            "Permission denied - root directory",
            "Permission denied - parent directory"
        ])


if __name__ == '__main__':
    pytest.main()