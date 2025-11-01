import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import os
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import cp


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов cp"""
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
    """Создает временную директорию для тестов cp"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_cp_empty_arguments(capsys):
    """cp без аргументов показывает ошибку"""
    result = cp.cp([], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "cp: missing file operand\n"


def test_cp_single_argument(capsys):
    """cp с одним аргументом показывает ошибку"""
    result = cp.cp(['source.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "cp: missing destination file operand after 'source.txt'\n"


def test_cp_incorrect_flags(capsys):
    """cp с неправильными флагами показывает ошибку"""
    result = cp.cp(['src', 'dest'], {'x', 'y'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "cp: does not support the flags:" in captured.out
    assert "x" in captured.out
    assert "y" in captured.out


def test_cp_nonexistent_source(capsys):
    """cp с несуществующим исходным файлом показывает ошибку"""
    result = cp.cp(['/nonexistent.txt', 'dest.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "cp: cannot stat '/nonexistent.txt': No such file or directory\n"


def test_cp_directory_without_r_flag(mock_temp_directory, capsys):
    """cp с директорией без флага -r показывает ошибку"""
    result = cp.cp([mock_temp_directory, 'dest'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == f"cp: -r not specified; omitting directory '{mock_temp_directory}'\n"


def test_cp_successful_file_to_file(mock_temp_files, capsys):
    """cp успешно копирует файл в файл"""
    temp_path1, _ = mock_temp_files
    dest_path = temp_path1 + '_copy'
    
    try:
        with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
            result = cp.cp([temp_path1, dest_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path(dest_path).exists()
            with open(dest_path, 'r', encoding='utf-8') as f:
                assert f.read() == "file1 content"
            assert captured.out == ""
            assert len(mock_history) == 1
            
    finally:
        if Path(dest_path).exists():
            Path(dest_path).unlink()


def test_cp_successful_file_to_directory(mock_temp_files, mock_temp_directory, capsys):
    """cp успешно копирует файл в директорию"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
        result = cp.cp([temp_path1, mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        dest_file = Path(mock_temp_directory) / Path(temp_path1).name
        assert dest_file.exists()
        with open(dest_file, 'r', encoding='utf-8') as f:
            assert f.read() == "file1 content"
        assert captured.out == ""
        assert len(mock_history) == 1


def test_cp_file_copy_error(mock_temp_files, capsys):
    """cp показывает ошибку при сбое копирования файла"""
    temp_path1, _ = mock_temp_files
    
    with patch('shutil.copy2', side_effect=Exception("Disk full")), \
         patch('src.ubuntu_commands.cp.helper_functions.is_valid_filename', return_value=True):
        result = cp.cp([temp_path1, 'valid_name.txt'], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "cp: cannot copy" in captured.out
        assert "Disk full" in captured.out


def test_cp_successful_directory_copy(mock_temp_directory, capsys):
    """cp успешно копирует директорию с флагом -r"""
    dest_dir = mock_temp_directory + '_copy'
    
    try:
        with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
            result = cp.cp([mock_temp_directory, dest_dir], {'r'})
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path(dest_dir).exists()
            assert Path(dest_dir).is_dir()
            assert captured.out == ""
            assert len(mock_history) == 1
            
    finally:
        if Path(dest_dir).exists():
            shutil.rmtree(dest_dir)


def test_cp_directory_copy_error(mock_temp_directory, capsys):
    """cp показывает ошибку при сбое копирования директории"""
    with patch('shutil.copytree', side_effect=Exception("Permission denied")), \
         patch('src.ubuntu_commands.cp.helper_functions.is_valid_dirname', return_value=True):
        result = cp.cp([mock_temp_directory, 'new_dir'], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "cp: cannot create directory" in captured.out
        assert "Permission denied" in captured.out


def test_cp_directory_to_existing_dir_success(mock_temp_directory, capsys):
    """cp успешно копирует директорию в существующую директорию"""
    with tempfile.TemporaryDirectory() as dest_dir:
        with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
            result = cp.cp([mock_temp_directory, dest_dir], {'r'})
            
            captured = capsys.readouterr()
            
            assert result == 0
            final_dest = Path(dest_dir) / Path(mock_temp_directory).name
            assert final_dest.exists()
            assert final_dest.is_dir()
            assert captured.out == ""
            assert len(mock_history) == 1


def test_cp_multiple_files_success(mock_temp_files, mock_temp_directory, capsys):
    """cp успешно копирует несколько файлов в директорию"""
    temp_path1, temp_path2 = mock_temp_files
    
    with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
        result = cp.cp([temp_path1, temp_path2, mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        dest_file1 = Path(mock_temp_directory) / Path(temp_path1).name
        dest_file2 = Path(mock_temp_directory) / Path(temp_path2).name
        assert dest_file1.exists()
        assert dest_file2.exists()
        assert captured.out == ""
        assert len(mock_history) == 1


def test_cp_multiple_files_with_errors(mock_temp_files, mock_temp_directory, capsys):
    """cp продолжает работу при ошибках с несколькими файлами"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
        result = cp.cp([temp_path1, '/nonexistent.txt', mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        dest_file1 = Path(mock_temp_directory) / Path(temp_path1).name
        assert dest_file1.exists()
        assert "cp: cannot stat '/nonexistent.txt': No such file or directory" in captured.out
        assert len(mock_history) == 1


def test_cp_multiple_directories_success(mock_temp_directory, capsys):
    """cp успешно копирует несколько директорий"""
    with tempfile.TemporaryDirectory() as dir1, \
         tempfile.TemporaryDirectory() as dir2, \
         tempfile.TemporaryDirectory() as dest_dir:
        
        with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
            result = cp.cp([dir1, dir2, dest_dir], {'r'})
            
            captured = capsys.readouterr()
            
            assert result == 0
            final_dest1 = Path(dest_dir) / Path(dir1).name
            final_dest2 = Path(dest_dir) / Path(dir2).name
            assert final_dest1.exists()
            assert final_dest2.exists()
            assert captured.out == ""
            assert len(mock_history) == 1


def test_cp_none_flags_initialization(capsys):
    """cp корректно обрабатывает flags=None"""
    with patch('pathlib.Path.exists', return_value=False):
        result = cp.cp(['src', 'dest'], None)
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "cp: cannot stat 'src': No such file or directory" in captured.out


def test_cp_nonexistent_item_type(mock_temp_files, capsys):
    """cp показывает ошибку для элемента, который не файл и не директория"""
    temp_path1, _ = mock_temp_files
    
    with patch('pathlib.Path.is_file', return_value=False), \
         patch('pathlib.Path.is_dir', return_value=False):
        result = cp.cp([temp_path1, 'dest.txt'], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert captured.out == f"cp: cannot copy '{temp_path1}': No such file or directory\n"


def test_cp_directory_to_file_overwrite_error(mock_temp_directory, capsys):
    """cp показывает ошибку при попытке перезаписать файл директорией"""
    with tempfile.NamedTemporaryFile(delete=False) as dest_file:
        dest_path = dest_file.name
        
        try:
            result = cp.cp([mock_temp_directory, dest_path], {'r'})
            
            captured = capsys.readouterr()
            
            assert result == 1
            assert "cp: cannot overwrite non-directory" in captured.out
            
        finally:
            Path(dest_path).unlink()


def test_cp_file_creation_with_parent_dirs(mock_temp_files, capsys):
    """cp создает родительские директории при копировании файла"""
    temp_path1, _ = mock_temp_files
    dest_path = '/tmp/nested/dirs/dest.txt'
    
    try:
        with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history, \
             patch('src.ubuntu_commands.cp.helper_functions.is_valid_filename', return_value=True):
            
            result = cp.cp([temp_path1, dest_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path(dest_path).exists()
            with open(dest_path, 'r', encoding='utf-8') as f:
                assert f.read() == "file1 content"
            assert captured.out == ""
            assert len(mock_history) == 1
            
    finally:
        if Path(dest_path).exists():
            Path(dest_path).unlink()
            
        if Path('/tmp/nested/dirs').exists():
            Path('/tmp/nested/dirs').rmdir()
        if Path('/tmp/nested').exists():
            Path('/tmp/nested').rmdir()


def test_cp_multiple_directories_partial_success(mock_temp_directory, capsys):
    """cp частично успешен при копировании нескольких директорий"""
    with tempfile.TemporaryDirectory() as dest_dir:
        with patch('src.ubuntu_commands.cp.FOR_UNDO_HISTORY', []) as mock_history:
            result = cp.cp([mock_temp_directory, '/nonexistent_dir', dest_dir], {'r'})
            
            captured = capsys.readouterr()
            
            assert result == 0
            final_dest = Path(dest_dir) / Path(mock_temp_directory).name
            assert final_dest.exists()
            assert "cp: cannot stat '/nonexistent_dir': No such file or directory" in captured.out
            assert len(mock_history) == 1


def test_cp_invalid_filename(mock_temp_files, capsys):
    """cp показывает ошибку при невалидном имени файла"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.cp.helper_functions.is_valid_filename', return_value=False):
        result = cp.cp([temp_path1, 'invalid*name.txt'], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "cp: invalid filename 'invalid*name.txt'" in captured.out


def test_cp_invalid_dirname(mock_temp_directory, capsys):
    """cp показывает ошибку при невалидном имени директории"""
    with patch('src.ubuntu_commands.cp.helper_functions.is_valid_dirname', return_value=False):
        result = cp.cp([mock_temp_directory, 'invalid*dir'], {'r'})
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "cp: invalid directory name 'invalid*dir'" in captured.out


if __name__ == '__main__':
    pytest.main()