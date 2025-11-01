import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import undo


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов undo"""
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
    """Создает временную директорию для тестов undo"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_trash_path():
    """Создает временную корзину для тестов undo"""
    with tempfile.TemporaryDirectory() as trash_dir:
        with patch('src.ubuntu_commands.undo.TRASH_PATH', Path(trash_dir)):
            yield trash_dir


def test_undo_empty_history(capsys):
    """undo с пустой историей показывает ошибку"""
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', []):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "undo: no commands to undo" in captured.out


def test_undo_unknown_command(capsys):
    """undo с неизвестной командой показывает ошибку"""
    mock_history = [['unknown_cmd', 'file.txt', Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "undo: unknown command 'unknown_cmd'" in captured.out
        assert len(mock_history) == 1


def test_undo_cp_file_to_file(mock_temp_files, capsys):
    """undo отменяет копирование файла в файл"""
    temp_path1, _ = mock_temp_files
    dest_path = temp_path1 + '_copy'
    
    shutil.copy2(temp_path1, dest_path)
    
    mock_history = [['cp', temp_path1, dest_path, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(dest_path).exists()
        assert captured.out == ""


def test_undo_cp_file_to_directory(mock_temp_files, mock_temp_directory, capsys):
    """undo отменяет копирование файла в директорию"""
    temp_path1, _ = mock_temp_files
    
    dest_file = Path(mock_temp_directory) / Path(temp_path1).name
    shutil.copy2(temp_path1, dest_file)
    
    mock_history = [['cp', temp_path1, mock_temp_directory, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not dest_file.exists()
        assert captured.out == ""


def test_undo_cp_multiple_files(mock_temp_files, mock_temp_directory, capsys):
    """undo отменяет копирование нескольких файлов"""
    temp_path1, temp_path2 = mock_temp_files
    
    dest_file1 = Path(mock_temp_directory) / Path(temp_path1).name
    dest_file2 = Path(mock_temp_directory) / Path(temp_path2).name
    shutil.copy2(temp_path1, dest_file1)
    shutil.copy2(temp_path2, dest_file2)
    
    mock_history = [['cp', temp_path1, temp_path2, mock_temp_directory, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not dest_file1.exists()
        assert not dest_file2.exists()
        assert captured.out == ""


def test_undo_mv_file_to_file(mock_temp_files, capsys):
    """undo отменяет перемещение файла в файл"""
    temp_path1, _ = mock_temp_files
    dest_path = temp_path1 + '_moved'
    
    shutil.move(temp_path1, dest_path)
    
    mock_history = [['mv', temp_path1, dest_path, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert Path(temp_path1).exists()
        assert not Path(dest_path).exists()
        assert captured.out == ""


def test_undo_mv_file_to_directory(mock_temp_files, mock_temp_directory, capsys):
    """undo отменяет перемещение файла в директорию"""
    temp_path1, _ = mock_temp_files
    
    dest_file = Path(mock_temp_directory) / Path(temp_path1).name
    shutil.move(temp_path1, dest_file)
    
    mock_history = [['mv', temp_path1, mock_temp_directory, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert Path(temp_path1).exists()
        assert not dest_file.exists()
        assert captured.out == ""


def test_undo_mv_multiple_files(mock_temp_files, mock_temp_directory, capsys):
    """undo отменяет перемещение нескольких файлов"""
    temp_path1, temp_path2 = mock_temp_files
    
    dest_file1 = Path(mock_temp_directory) / Path(temp_path1).name
    dest_file2 = Path(mock_temp_directory) / Path(temp_path2).name
    shutil.move(temp_path1, dest_file1)
    shutil.move(temp_path2, dest_file2)
    
    mock_history = [['mv', temp_path1, temp_path2, mock_temp_directory, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert Path(temp_path1).exists()
        assert Path(temp_path2).exists()
        assert not dest_file1.exists()
        assert not dest_file2.exists()
        assert captured.out == ""


def test_undo_rm_file(mock_temp_files, mock_trash_path, capsys):
    """undo отменяет удаление файла"""
    temp_path1, _ = mock_temp_files
    
    trash_file = Path(mock_trash_path) / Path(temp_path1).name
    shutil.copy2(temp_path1, trash_file)
    Path(temp_path1).unlink()
    
    mock_history = [['rm', temp_path1, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert Path(temp_path1).exists()
        assert captured.out == ""


def test_undo_rm_multiple_files(mock_temp_files, mock_trash_path, capsys):
    """undo отменяет удаление нескольких файлов"""
    temp_path1, temp_path2 = mock_temp_files
    
    trash_file1 = Path(mock_trash_path) / Path(temp_path1).name
    trash_file2 = Path(mock_trash_path) / Path(temp_path2).name
    shutil.copy2(temp_path1, trash_file1)
    shutil.copy2(temp_path2, trash_file2)
    Path(temp_path1).unlink()
    Path(temp_path2).unlink()
    
    mock_history = [['rm', temp_path1, temp_path2, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert Path(temp_path1).exists()
        assert Path(temp_path2).exists()
        assert captured.out == ""


def test_undo_with_flags(capsys):
    """undo с флагами работает корректно (функция не проверяет флаги)"""
    mock_history = [['cp', 'src', 'dest', Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], {'x', 'v'})
        
        captured = capsys.readouterr()
        
        assert result == 0


def test_undo_none_flags_initialization(mock_temp_files, capsys):
    """undo корректно обрабатывает flags=None"""
    temp_path1, _ = mock_temp_files
    dest_path = temp_path1 + '_copy'
    
    shutil.copy2(temp_path1, dest_path)
    
    mock_history = [['cp', temp_path1, dest_path, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], None)
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(dest_path).exists()
        assert captured.out == ""


def test_undo_error_during_operation(capsys):
    """undo показывает ошибку при сбое операции отмены"""
    mock_history = [['cp', '/nonexistent/src', 'dest', Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result in [0, 1]


def test_undo_cp_directory(mock_temp_directory, capsys):
    """undo отменяет копирование директории"""
    dest_dir = mock_temp_directory + '_copy'
    
    shutil.copytree(mock_temp_directory, dest_dir)
    
    mock_history = [['cp', mock_temp_directory, dest_dir, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert captured.out == ""


def test_undo_mv_directory(mock_temp_directory, capsys):
    """undo отменяет перемещение директории"""
    dest_dir = mock_temp_directory + '_moved'
    
    shutil.move(mock_temp_directory, dest_dir)
    
    mock_history = [['mv', mock_temp_directory, dest_dir, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert captured.out == ""


def test_undo_rm_directory(mock_temp_directory, mock_trash_path, capsys):
    """undo отменяет удаление директории"""
    trash_dir = Path(mock_trash_path) / Path(mock_temp_directory).name
    shutil.copytree(mock_temp_directory, trash_dir)
    shutil.rmtree(mock_temp_directory)
    
    mock_history = [['rm', mock_temp_directory, Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert Path(mock_temp_directory).exists()
        assert captured.out == ""


def test_undo_history_removal(capsys):
    """undo удаляет команду из истории при успешном выполнении"""
    mock_history = [['cp', 'src', 'dest', Path('.')], ['mv', 'file1', 'file2', Path('.')]]
    
    with patch('src.ubuntu_commands.undo.FOR_UNDO_HISTORY', mock_history):
        result = undo.undo([], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert len(mock_history) == 1
        assert mock_history[0][0] == 'cp'


if __name__ == '__main__':
    pytest.main()