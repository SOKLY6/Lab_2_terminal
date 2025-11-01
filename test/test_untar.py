import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import shutil
import tarfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import untar


@pytest.fixture
def mock_tar_archive():
    """Создает временный tar.gz архив для тестов untar"""
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as temp_file:
        archive_path = temp_file.name
    
    with tarfile.open(archive_path, 'w:gz') as tar:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file1:
            file1.write("file1 content")
            file1.flush()
            tar.add(file1.name, arcname='file1.txt')
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file2:
            file2.write("file2 content")
            file2.flush()
            tar.add(file2.name, arcname='file2.txt')
    
    yield archive_path
    
    if Path(archive_path).exists():
        Path(archive_path).unlink()


@pytest.fixture
def mock_temp_directory():
    """Создает временную директорию для тестов untar"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_untar_empty_arguments(capsys):
    """untar без аргументов показывает ошибку"""
    result = untar.untar([], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "untar: missing archive operand" in captured.out


def test_untar_single_archive(mock_tar_archive, capsys):
    """untar с одним архивом успешно распаковывает в текущую директорию"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            result = untar.untar([mock_tar_archive], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            
        finally:
            os.chdir(original_dir)


def test_untar_with_extract_directory(mock_tar_archive, mock_temp_directory, capsys):
    """untar с указанием директории для распаковки"""
    result = untar.untar([mock_temp_directory, mock_tar_archive], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    extract_path = Path(mock_temp_directory)
    assert (extract_path / "file1.txt").exists()
    assert (extract_path / "file2.txt").exists()


def test_untar_nonexistent_archive(capsys):
    """untar с несуществующим архивом показывает ошибку"""
    result = untar.untar(['/nonexistent.tar.gz'], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "cannot find or open" in captured.out


def test_untar_mixed_valid_invalid_archives(mock_tar_archive, capsys):
    """untar обрабатывает mix валидных и невалидных архивов"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as invalid_file:
                invalid_path = invalid_file.name
                invalid_file.write("not a tar file")
            
            result = untar.untar([mock_tar_archive, invalid_path, '/nonexistent.tar.gz'], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            assert "is not tarfile" in captured.out
            assert "error extracting" in captured.out
            
        finally:
            os.chdir(original_dir)
            if Path(invalid_path).exists():
                Path(invalid_path).unlink()


def test_untar_invalid_file(capsys):
    """untar с файлом не tar.gz формата показывает ошибку"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_path = temp_file.name
        temp_file.write("not a tar file")
    
    try:
        result = untar.untar([temp_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "is not tarfile" in captured.out
        
    finally:
        Path(temp_path).unlink()


def test_untar_with_flags(capsys):
    """untar с флагами показывает ошибку"""
    result = untar.untar(['archive.tar.gz'], {'x', 'v'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "untar: does not support the flags:" in captured.out


def test_untar_none_flags_initialization(mock_tar_archive, capsys):
    """untar корректно обрабатывает flags=None"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            result = untar.untar([mock_tar_archive], None)
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            
        finally:
            os.chdir(original_dir)


def test_untar_extraction_error(capsys):
    """untar показывает ошибку при сбое распаковки"""
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as broken_archive:
        broken_path = broken_archive.name
        broken_archive.write(b"broken tar content")
    
    try:
        result = untar.untar([broken_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "is not tarfile" in captured.out or "error extracting" in captured.out
        
    finally:
        Path(broken_path).unlink()


def test_untar_is_tar_gz_archive_function(mock_tar_archive):
    """Тест вспомогательной функции is_tar_gz_archive"""
    assert untar.is_tar_gz_archive(Path(mock_tar_archive)) == True
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as invalid_file:
        invalid_path = invalid_file.name
        invalid_file.write("not a tar file")
    
    try:
        assert untar.is_tar_gz_archive(Path(invalid_path)) == False
    finally:
        Path(invalid_path).unlink()
    
    assert untar.is_tar_gz_archive(Path('/nonexistent.tar.gz')) == False


def test_untar_with_nonexistent_extract_directory(mock_tar_archive, capsys):
    """untar с несуществующей директорией для распаковки"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            result = untar.untar(['/nonexistent/dir', mock_tar_archive], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            
        finally:
            os.chdir(original_dir)


def test_untar_file_conflicts(mock_tar_archive, capsys):
    """untar обрабатывает конфликты файлов при распаковке"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            conflict_file = Path("file1.txt")
            conflict_file.write_text("original content")
            
            with patch('builtins.input', return_value='y'):
                result = untar.untar([mock_tar_archive], set())
                
                captured = capsys.readouterr()
                
                assert result == 0
            
        finally:
            os.chdir(original_dir)


def test_untar_multiple_valid_archives(capsys):
    """untar с несколькими валидными архивами"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            archive1 = Path("archive1.tar.gz")
            archive2 = Path("archive2.tar.gz")
            
            with tarfile.open(archive1, 'w:gz') as tar:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file1:
                    file1.write("archive1 content")
                    file1.flush()
                    tar.add(file1.name, arcname='file1.txt')
            
            with tarfile.open(archive2, 'w:gz') as tar:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file2:
                    file2.write("archive2 content")
                    file2.flush()
                    tar.add(file2.name, arcname='file2.txt')
            
            result = untar.untar([str(archive1), str(archive2)], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            
        finally:
            os.chdir(original_dir)
            if archive1.exists():
                archive1.unlink()
            if archive2.exists():
                archive2.unlink()


import os

if __name__ == '__main__':
    pytest.main()