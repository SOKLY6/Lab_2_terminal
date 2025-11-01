import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import tar


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов tar"""
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
    """Создает временную директорию для тестов tar"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_tar_empty_arguments(capsys):
    """tar без аргументов вызывает IndexError"""
    with pytest.raises(IndexError):
        tar.tar([], set())


def test_tar_single_argument_existing_file(mock_temp_files, capsys):
    """tar с одним существующим файлом создает архив"""
    temp_path1, _ = mock_temp_files
    
    try:
        result = tar.tar([temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = Path(temp_path1).stem + '.tar.gz'
        assert Path(archive_name).exists()
        assert captured.out == ""
        
    finally:
        archive_name = Path(temp_path1).stem + '.tar.gz'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_tar_single_argument_nonexistent_file(capsys):
    """tar с одним несуществующим файлом показывает ошибку"""
    result = tar.tar(['/nonexistent.tar.gz'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "tar: cannot stat '/nonexistent.tar.gz':" in captured.out
    assert "No such file or directory" in captured.out


def test_tar_two_arguments_shows_error(capsys):
    """tar с двумя аргументами показывает ошибку"""
    result = tar.tar(['archive', 'file.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "tar: missing arguments" in captured.out


def test_tar_three_arguments_with_existing_files(mock_temp_files, capsys):
    """tar с тремя аргументами и существующими файлами создает архив"""
    temp_path1, temp_path2 = mock_temp_files
    archive_name = 'test_archive'
    
    try:
        result = tar.tar([archive_name, temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        expected_name = archive_name + '.tar.gz'
        assert Path(expected_name).exists()
        assert captured.out == ""
        
    finally:
        expected_name = archive_name + '.tar.gz'
        if Path(expected_name).exists():
            Path(expected_name).unlink()


def test_tar_three_arguments_with_nonexistent_files(capsys):
    """tar с тремя аргументами и несуществующими файлами показывает ошибки"""
    archive_name = 'test_archive'
    
    result = tar.tar([archive_name, '/nonexistent1.txt', '/nonexistent2.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "tar: cannot stat '/nonexistent1.txt': No such file or directory" in captured.out
    assert "tar: cannot stat '/nonexistent2.txt': No such file or directory" in captured.out


def test_tar_three_arguments_partial_nonexistent(mock_temp_files, capsys):
    """tar с тремя аргументами и частично несуществующими файлами показывает ошибки"""
    temp_path1, _ = mock_temp_files
    archive_name = 'test_archive'
    
    result = tar.tar([archive_name, temp_path1, '/nonexistent.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "tar: cannot stat '/nonexistent.txt': No such file or directory" in captured.out


def test_tar_successful_directory(mock_temp_directory, capsys):
    """tar успешно создает архив из директории с одним аргументом"""
    try:
        result = tar.tar([mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = Path(mock_temp_directory).name + '.tar.gz'
        assert Path(archive_name).exists()
        assert captured.out == ""
        
    finally:
        archive_name = Path(mock_temp_directory).name + '.tar.gz'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_tar_with_flags(capsys):
    """tar с флагами показывает ошибку"""
    result = tar.tar(['file.txt'], {'x', 'v'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "tar: does not support the flags:" in captured.out
    assert "x" in captured.out
    assert "v" in captured.out


def test_tar_none_flags_initialization(mock_temp_files, capsys):
    """tar корректно обрабатывает flags=None"""
    temp_path1, _ = mock_temp_files
    
    try:
        result = tar.tar([temp_path1], None)
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = Path(temp_path1).stem + '.tar.gz'
        assert Path(archive_name).exists()
        assert captured.out == ""
        
    finally:
        archive_name = Path(temp_path1).stem + '.tar.gz'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_tar_invalid_archive_name(mock_temp_files, capsys):
    """tar показывает ошибку при невалидном имени архива"""
    temp_path1, temp_path2 = mock_temp_files
    
    with patch('src.ubuntu_commands.tar.helper_functions.is_valid_filename', return_value=False):

        result = tar.tar(['invalid*name', temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "tar: invalid archive name 'invalid*name'" in captured.out


def test_tar_archive_creation_error(mock_temp_files, capsys):
    """tar показывает ошибку при сбое создания архива"""
    temp_path1, temp_path2 = mock_temp_files
    
    with patch('shutil.make_archive', side_effect=Exception("Disk full")):
        result = tar.tar(['archive', temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "tar: error creating archive: Disk full" in captured.out


def test_tar_temp_dir_cleanup(mock_temp_files, capsys):
    """tar корректно очищает временную директорию"""
    temp_path1, temp_path2 = mock_temp_files
    
    try:
        result = tar.tar(['test_archive', temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = 'test_archive.tar.gz'
        assert Path(archive_name).exists()
        temp_dir = Path('temp_tar_test_archive')
        assert not temp_dir.exists()
        assert captured.out == ""
        
    finally:
        archive_name = 'test_archive.tar.gz'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_tar_file_copy_error(mock_temp_files, capsys):
    """tar показывает ошибку при сбое копирования файла"""
    temp_path1, temp_path2 = mock_temp_files
    
    with patch('shutil.copy2', side_effect=Exception("Permission denied")):
        result = tar.tar(['archive', temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "tar: error creating archive: Permission denied" in captured.out


def test_tar_directory_copy_error(mock_temp_directory, capsys):
    """tar показывает ошибку при сбое копирования директории"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
        temp_path = temp_file.name
        temp_file.write("dummy content")
    
    try:
        with patch('shutil.copytree', side_effect=Exception("Permission denied")):
            result = tar.tar(['archive', mock_temp_directory, temp_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 1
            assert "tar: error creating archive: Permission denied" in captured.out
            
    finally:
        if Path(temp_path).exists():
            Path(temp_path).unlink()


def test_tar_mixed_files_and_dirs(mock_temp_files, mock_temp_directory, capsys):
    """tar успешно создает архив из mix файлов и директорий"""
    temp_path1, _ = mock_temp_files
    archive_name = 'mixed_archive'
    
    try:
        result = tar.tar([archive_name, temp_path1, mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        expected_name = archive_name + '.tar.gz'
        assert Path(expected_name).exists()
        assert captured.out == ""
        
    finally:
        expected_name = archive_name + '.tar.gz'
        if Path(expected_name).exists():
            Path(expected_name).unlink()


if __name__ == '__main__':
    pytest.main()