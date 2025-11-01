import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import zip_


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов zip"""
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
    """Создает временную директорию для тестов zip"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_zip_empty_arguments(capsys):
    """zip без аргументов показывает ошибку"""
    result = zip_.zip_([], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "zip: missing arguments\n"


def test_zip_single_argument_existing_file(mock_temp_files, capsys):
    """zip с одним существующим файлом создает архив"""
    temp_path1, _ = mock_temp_files
    
    try:
        result = zip_.zip_([temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = Path(temp_path1).stem + '.zip'
        assert Path(archive_name).exists()
        assert captured.out == ""
        
    finally:
        archive_name = Path(temp_path1).stem + '.zip'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_zip_single_argument_nonexistent_file(capsys):
    """zip с одним несуществующим файлом показывает ошибку"""
    result = zip_.zip_(['/nonexistent.zip'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "zip: cannot stat '/nonexistent.zip':" in captured.out
    assert "No such file or directory" in captured.out


def test_zip_two_arguments_with_existing_files(mock_temp_files, capsys):
    """zip с двумя аргументами и существующими файлами создает архив"""
    temp_path1, temp_path2 = mock_temp_files
    archive_name = 'test_archive'
    
    try:
        result = zip_.zip_([archive_name, temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        expected_name = archive_name + '.zip'
        assert Path(expected_name).exists()
        assert captured.out == ""
        
    finally:
        expected_name = archive_name + '.zip'
        if Path(expected_name).exists():
            Path(expected_name).unlink()


def test_zip_two_arguments_with_nonexistent_files(capsys):
    """zip с двумя аргументами и несуществующими файлами показывает ошибки"""
    archive_name = 'test_archive'
    
    result = zip_.zip_([archive_name, '/nonexistent.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "zip: cannot stat '/nonexistent.txt': No such file or directory" in captured.out


def test_zip_three_arguments_with_existing_files(mock_temp_files, capsys):
    """zip с тремя аргументами и существующими файлами создает архив"""
    temp_path1, temp_path2 = mock_temp_files
    archive_name = 'test_archive'
    
    try:
        result = zip_.zip_([archive_name, temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        expected_name = archive_name + '.zip'
        assert Path(expected_name).exists()
        assert captured.out == ""
        
    finally:
        expected_name = archive_name + '.zip'
        if Path(expected_name).exists():
            Path(expected_name).unlink()


def test_zip_three_arguments_with_nonexistent_files(capsys):
    """zip с тремя аргументами и несуществующими файлами показывает ошибки"""
    archive_name = 'test_archive'
    
    result = zip_.zip_([archive_name, '/nonexistent1.txt', '/nonexistent2.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "zip: cannot stat '/nonexistent1.txt': No such file or directory" in captured.out
    assert "zip: cannot stat '/nonexistent2.txt': No such file or directory" in captured.out


def test_zip_three_arguments_partial_nonexistent(mock_temp_files, capsys):
    """zip с тремя аргументами и частично несуществующими файлами показывает ошибки"""
    temp_path1, _ = mock_temp_files
    archive_name = 'test_archive'
    
    result = zip_.zip_([archive_name, temp_path1, '/nonexistent.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "zip: cannot stat '/nonexistent.txt': No such file or directory" in captured.out


def test_zip_successful_directory(mock_temp_directory, capsys):
    """zip успешно создает архив из директории с одним аргументом"""
    try:
        result = zip_.zip_([mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = Path(mock_temp_directory).name + '.zip'
        assert Path(archive_name).exists()
        assert captured.out == ""
        
    finally:
        archive_name = Path(mock_temp_directory).name + '.zip'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_zip_with_flags(capsys):
    """zip с флагами показывает ошибку"""
    result = zip_.zip_(['file.txt'], {'x', 'v'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "zip: does not support the flags:" in captured.out
    assert "x" in captured.out
    assert "v" in captured.out


def test_zip_none_flags_initialization(mock_temp_files, capsys):
    """zip корректно обрабатывает flags=None"""
    temp_path1, _ = mock_temp_files
    
    try:
        result = zip_.zip_([temp_path1], None)
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = Path(temp_path1).stem + '.zip'
        assert Path(archive_name).exists()
        assert captured.out == ""
        
    finally:
        archive_name = Path(temp_path1).stem + '.zip'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_zip_invalid_archive_name(mock_temp_files, capsys):
    """zip показывает ошибку при невалидном имени архива"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.zip_.helper_functions.is_valid_filename', return_value=False):
        result = zip_.zip_(['invalid*name', temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "zip: invalid archive name 'invalid*name'" in captured.out


def test_zip_archive_creation_error(mock_temp_files, capsys):
    """zip показывает ошибку при сбое создания архива"""
    temp_path1, _ = mock_temp_files
    
    with patch('shutil.make_archive', side_effect=Exception("Disk full")):
        result = zip_.zip_(['archive', temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "zip: error creating archive: Disk full" in captured.out


def test_zip_temp_dir_cleanup(mock_temp_files, capsys):
    """zip корректно очищает временную директорию"""
    temp_path1, temp_path2 = mock_temp_files
    
    try:
        result = zip_.zip_(['test_archive', temp_path1, temp_path2], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        archive_name = 'test_archive.zip'
        assert Path(archive_name).exists()
        temp_dir = Path('temp_zip_test_archive')
        assert not temp_dir.exists()
        assert captured.out == ""
        
    finally:
        archive_name = 'test_archive.zip'
        if Path(archive_name).exists():
            Path(archive_name).unlink()


def test_zip_file_copy_error(mock_temp_files, capsys):
    """zip показывает ошибку при сбое копирования файла"""
    temp_path1, _ = mock_temp_files
    
    with patch('shutil.copy2', side_effect=Exception("Permission denied")):
        result = zip_.zip_(['archive', temp_path1], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "zip: error creating archive: Permission denied" in captured.out


def test_zip_directory_copy_error(mock_temp_directory, capsys):
    """zip показывает ошибку при сбое копирования директории"""
    with patch('shutil.copytree', side_effect=Exception("Permission denied")):
        result = zip_.zip_([mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "zip: error creating archive: Permission denied" in captured.out


def test_zip_mixed_files_and_dirs(mock_temp_files, mock_temp_directory, capsys):
    """zip успешно создает архив из mix файлов и директорий"""
    temp_path1, _ = mock_temp_files
    archive_name = 'mixed_archive'
    
    try:
        result = zip_.zip_([archive_name, temp_path1, mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        expected_name = archive_name + '.zip'
        assert Path(expected_name).exists()
        assert captured.out == ""
        
    finally:
        expected_name = archive_name + '.zip'
        if Path(expected_name).exists():
            Path(expected_name).unlink()


if __name__ == '__main__':
    pytest.main()