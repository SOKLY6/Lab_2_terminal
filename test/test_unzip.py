import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import shutil
import zipfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import unzip


@pytest.fixture
def mock_zip_archive():
    """Создает временный zip архив для тестов unzip"""
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        archive_path = temp_file.name
    
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file1:
            file1.write("file1 content")
            file1.flush()
            zipf.write(file1.name, 'file1.txt')
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file2:
            file2.write("file2 content")
            file2.flush()
            zipf.write(file2.name, 'file2.txt')
    
    yield archive_path
    
    if Path(archive_path).exists():
        Path(archive_path).unlink()


@pytest.fixture
def mock_temp_directory():
    """Создает временную директорию для тестов unzip"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_unzip_empty_arguments(capsys):
    """unzip без аргументов показывает ошибку"""
    result = unzip.unzip([], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "unzip: missing archive operand" in captured.out


def test_unzip_single_archive(mock_zip_archive, capsys):
    """unzip с одним архивом успешно распаковывает в текущую директорию"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            result = unzip.unzip([mock_zip_archive], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            
        finally:
            os.chdir(original_dir)


def test_unzip_with_extract_directory(mock_zip_archive, mock_temp_directory, capsys):
    """unzip с указанием директории для распаковки"""
    result = unzip.unzip([mock_temp_directory, mock_zip_archive], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    extract_path = Path(mock_temp_directory)
    assert (extract_path / "file1.txt").exists()
    assert (extract_path / "file2.txt").exists()


def test_unzip_nonexistent_archive(capsys):
    """unzip с несуществующим архивом показывает ошибку"""
    result = unzip.unzip(['/nonexistent.zip'], set())
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert "cannot find or open" in captured.out


def test_unzip_invalid_file(capsys):
    """unzip с файлом не zip формата показывает ошибку"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_path = temp_file.name
        temp_file.write("not a zip file")
    
    try:
        result = unzip.unzip([temp_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "is not zipfile" in captured.out
        
    finally:
        Path(temp_path).unlink()


def test_unzip_with_flags(capsys):
    """unzip с флагами показывает ошибку"""
    result = unzip.unzip(['archive.zip'], {'x', 'v'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "unzip: does not support the flags:" in captured.out


def test_unzip_none_flags_initialization(mock_zip_archive, capsys):
    """unzip корректно обрабатывает flags=None"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            result = unzip.unzip([mock_zip_archive], None)
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            
        finally:
            os.chdir(original_dir)


def test_unzip_extraction_error(capsys):
    """unzip показывает ошибку при сбое распаковки"""
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as broken_archive:
        broken_path = broken_archive.name
        broken_archive.write(b"broken zip content")
    
    try:
        result = unzip.unzip([broken_path], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert "is not zipfile" in captured.out or "error extracting" in captured.out
        
    finally:
        Path(broken_path).unlink()


def test_unzip_mixed_valid_invalid_archives(mock_zip_archive, capsys):
    """unzip обрабатывает mix валидных и невалидных архивов"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as invalid_file:
                invalid_path = invalid_file.name
                invalid_file.write("not a zip file")
            
            result = unzip.unzip([mock_zip_archive, invalid_path, '/nonexistent.zip'], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            assert "is not zipfile" in captured.out
            assert "cannot find or open" in captured.out or "error extracting" in captured.out
            
        finally:
            os.chdir(original_dir)
            if Path(invalid_path).exists():
                Path(invalid_path).unlink()


def test_unzip_is_zip_archive_function(mock_zip_archive):
    """Тест вспомогательной функции is_zip_archive"""
    assert unzip.is_zip_archive(Path(mock_zip_archive)) == True
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as invalid_file:
        invalid_path = invalid_file.name
        invalid_file.write("not a zip file")
    
    try:
        assert unzip.is_zip_archive(Path(invalid_path)) == False
    finally:
        Path(invalid_path).unlink()
    
    assert unzip.is_zip_archive(Path('/nonexistent.zip')) == False


def test_unzip_with_nonexistent_extract_directory(mock_zip_archive, capsys):
    """unzip с несуществующей директорией для распаковки"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            result = unzip.unzip(['/nonexistent/dir', mock_zip_archive], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            
        finally:
            os.chdir(original_dir)


def test_unzip_file_conflicts(mock_zip_archive, capsys):
    """unzip обрабатывает конфликты файлов при распаковке"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            conflict_file = Path("file1.txt")
            conflict_file.write_text("original content")
            
            with patch('builtins.input', return_value='y'):
                result = unzip.unzip([mock_zip_archive], set())
                
                captured = capsys.readouterr()
                
                assert result == 0
            
        finally:
            os.chdir(original_dir)


def test_unzip_multiple_valid_archives(capsys):
    """unzip с несколькими валидными архивами"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            archive1 = Path("archive1.zip")
            archive2 = Path("archive2.zip")
            
            with zipfile.ZipFile(archive1, 'w') as zipf:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file1:
                    file1.write("archive1 content")
                    file1.flush()
                    zipf.write(file1.name, 'file1.txt')
            
            with zipfile.ZipFile(archive2, 'w') as zipf:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file2:
                    file2.write("archive2 content")
                    file2.flush()
                    zipf.write(file2.name, 'file2.txt')
            
            result = unzip.unzip([str(archive1), str(archive2)], set())
            
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


def test_unzip_temp_dir_cleanup(mock_zip_archive, capsys):
    """unzip корректно очищает временную директорию"""
    original_dir = Path.cwd()
    
    with tempfile.TemporaryDirectory() as test_dir:
        try:
            os.chdir(test_dir)
            
            result = unzip.unzip([mock_zip_archive], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert Path("file1.txt").exists()
            assert Path("file2.txt").exists()
            temp_dir = Path('temp_unzip')
            assert not temp_dir.exists()
            
        finally:
            os.chdir(original_dir)


import os

if __name__ == '__main__':
    pytest.main()