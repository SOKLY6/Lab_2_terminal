import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import mv


@pytest.fixture
def mock_temp_files():
    """Создает временные файлы для тестов mv"""
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
    """Создает временную директорию для тестов mv"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_mv_empty_arguments(capsys):
    """mv без аргументов показывает ошибку"""
    result = mv.mv([], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "mv: missing file operand\n"


def test_mv_single_argument(capsys):
    """mv с одним аргументом показывает ошибку"""
    result = mv.mv(['source.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "mv: missing destination file operand after 'source.txt'\n"


def test_mv_nonexistent_source(capsys):
    """mv с несуществующим исходным файлом показывает ошибку"""
    result = mv.mv(['/nonexistent.txt', 'dest.txt'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "mv: cannot stat '/nonexistent.txt':" in captured.out
    assert "No such file or directory" in captured.out


def test_mv_successful_file_to_file(mock_temp_files, capsys):
    """mv успешно перемещает файл в файл"""
    temp_path1, _ = mock_temp_files
    dest_path = temp_path1 + '_moved'
    
    try:
        with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
            result = mv.mv([temp_path1, dest_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert not Path(temp_path1).exists()
            assert Path(dest_path).exists()
            with open(dest_path, 'r', encoding='utf-8') as f:
                assert f.read() == "file1 content"
            assert captured.out == ""
            assert len(mock_history) == 1
            
    finally:
        if Path(dest_path).exists():
            Path(dest_path).unlink()


def test_mv_successful_file_to_directory(mock_temp_files, mock_temp_directory, capsys):
    """mv успешно перемещает файл в директорию"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
        result = mv.mv([temp_path1, mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        dest_file = Path(mock_temp_directory) / Path(temp_path1).name
        assert dest_file.exists()
        with open(dest_file, 'r', encoding='utf-8') as f:
            assert f.read() == "file1 content"
        assert captured.out == ""
        assert len(mock_history) == 1


def test_mv_successful_directory(mock_temp_directory, capsys):
    """mv успешно перемещает директорию"""
    dest_dir = mock_temp_directory + '_moved'
    
    try:
        with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
            result = mv.mv([mock_temp_directory, dest_dir], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert not Path(mock_temp_directory).exists()
            assert Path(dest_dir).exists()
            assert Path(dest_dir).is_dir()
            assert captured.out == ""
            assert len(mock_history) == 1
            
    finally:
        if Path(dest_dir).exists():
            shutil.rmtree(dest_dir)


def test_mv_directory_to_existing_dir(mock_temp_directory, capsys):
    """mv успешно перемещает директорию в существующую директорию"""
    with tempfile.TemporaryDirectory() as dest_dir:
        with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
            result = mv.mv([mock_temp_directory, dest_dir], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert not Path(mock_temp_directory).exists()
            final_dest = Path(dest_dir) / Path(mock_temp_directory).name
            assert final_dest.exists()
            assert final_dest.is_dir()
            assert captured.out == ""
            assert len(mock_history) == 1


def test_mv_multiple_files(mock_temp_files, mock_temp_directory, capsys):
    """mv успешно перемещает несколько файлов в директорию"""
    temp_path1, temp_path2 = mock_temp_files
    
    with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
        result = mv.mv([temp_path1, temp_path2, mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        assert not Path(temp_path2).exists()
        dest_file1 = Path(mock_temp_directory) / Path(temp_path1).name
        dest_file2 = Path(mock_temp_directory) / Path(temp_path2).name
        assert dest_file1.exists()
        assert dest_file2.exists()
        assert captured.out == ""
        assert len(mock_history) == 1


def test_mv_file_move_error(mock_temp_files, capsys):
    """mv показывает ошибку при сбое перемещения файла"""
    temp_path1, _ = mock_temp_files
    
    with patch('shutil.move', side_effect=Exception("Permission denied")):
        result = mv.mv([temp_path1, 'dest.txt'], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "mv: cannot move" in captured.out
        assert "Permission denied" in captured.out


def test_mv_directory_to_file_error(mock_temp_directory, capsys):
    """mv показывает ошибку при попытке переместить директорию в файл"""
    with tempfile.NamedTemporaryFile(delete=False) as dest_file:
        dest_path = dest_file.name
        
        try:
            result = mv.mv([mock_temp_directory, dest_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 1
            assert "mv: cannot overwrite non-directory" in captured.out
            
        finally:
            Path(dest_path).unlink()


def test_mv_nonexistent_target_directory(capsys):
    """mv показывает ошибку при несуществующей целевой директории для множественных файлов"""
    result = mv.mv(['file1.txt', 'file2.txt', '/nonexistent/dir'], set())
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "mv: target '/nonexistent/dir': No such file or directory" in captured.out


def test_mv_target_not_directory(capsys):
    """mv показывает ошибку когда цель не является директорией для множественных файлов"""
    with tempfile.NamedTemporaryFile(delete=False) as target_file:
        target_path = target_file.name
        
        try:
            result = mv.mv(['file1.txt', 'file2.txt', target_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 1
            assert f"mv: target '{target_path}' is not a directory" in captured.out
            
        finally:
            Path(target_path).unlink()


def test_mv_multiple_files_with_errors(mock_temp_files, mock_temp_directory, capsys):
    """mv продолжает работу при ошибках с несколькими файлами"""
    temp_path1, _ = mock_temp_files
    
    with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
        result = mv.mv([temp_path1, '/nonexistent.txt', mock_temp_directory], set())
        
        captured = capsys.readouterr()
        
        assert result == 0
        assert not Path(temp_path1).exists()
        assert "mv: cannot stat '/nonexistent.txt': No such file or directory" in captured.out
        assert len(mock_history) == 1


def test_mv_with_flags(capsys):
    """mv с флагами показывает ошибку"""
    result = mv.mv(['src', 'dest'], {'x', 'y'})
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "mv: does not support the flags:" in captured.out
    assert "x" in captured.out
    assert "y" in captured.out


def test_mv_none_flags_initialization(capsys):
    """mv корректно обрабатывает flags=None"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
        temp_path = temp_file.name
        temp_file.write("test content")
    
    dest_path = temp_path + '_moved'
    
    try:
        with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
            result = mv.mv([temp_path, dest_path], None)
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert not Path(temp_path).exists()
            assert Path(dest_path).exists()
            assert captured.out == ""
            assert len(mock_history) == 1
            
    finally:
        if Path(temp_path).exists():
            Path(temp_path).unlink()
        if Path(dest_path).exists():
            Path(dest_path).unlink()


def test_mv_invalid_dirname(mock_temp_directory, capsys):
    """mv показывает ошибку при невалидном имени директории"""
    with patch('src.ubuntu_commands.mv.helper_functions.is_valid_dirname', return_value=False):
        result = mv.mv([mock_temp_directory, 'invalid*dir'], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "mv: invalid directory name 'invalid*dir'" in captured.out


def test_mv_file_creation_with_parent_dirs(mock_temp_files, capsys):
    """mv создает родительские директории при перемещении файла"""
    temp_path1, _ = mock_temp_files
    dest_path = '/tmp/nested/dirs/moved_file.txt'
    
    try:
        with patch('src.ubuntu_commands.mv.FOR_UNDO_HISTORY', []) as mock_history:
            result = mv.mv([temp_path1, dest_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 0
            assert not Path(temp_path1).exists()
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


def test_mv_nonexistent_item_type(mock_temp_files, capsys):
    """mv показывает ошибку для элемента, который не файл и не директория"""
    temp_path1, _ = mock_temp_files
    
    with patch('pathlib.Path.is_file', return_value=False), \
         patch('pathlib.Path.is_dir', return_value=False):
        result = mv.mv([temp_path1, 'dest.txt'], set())
        
        captured = capsys.readouterr()
        
        assert result == 1
        assert "mv: cannot move" in captured.out
        assert "No such file or directory" in captured.out


def test_mv_directory_overwrite_file_error(mock_temp_directory, capsys):
    """mv показывает ошибку при попытке перезаписать файл директорией"""
    with tempfile.NamedTemporaryFile(delete=False) as dest_file:
        dest_path = dest_file.name
        
        try:
            result = mv.mv([mock_temp_directory, dest_path], set())
            
            captured = capsys.readouterr()
            
            assert result == 1
            assert "mv: cannot overwrite non-directory" in captured.out
            
        finally:
            Path(dest_path).unlink()


if __name__ == '__main__':
    pytest.main()