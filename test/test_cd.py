import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ubuntu_commands import cd


@pytest.fixture
def mock_temp_directory():
    """Создает временную директорию для тестов cd"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_cd_no_arguments(capsys):
    """cd без аргументов переходит в домашнюю директорию"""
    test_flags = None
    test_arguments = []
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        call_args = mock_chdir.call_args[0][0]
        assert str(Path.home()) in call_args
        assert captured.out == ""


def test_cd_home(capsys):
    """cd с аргументом ~ переходит в домашнюю директорию"""
    test_flags = None
    test_arguments = ['~']
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        call_args = mock_chdir.call_args[0][0]
        assert str(Path.home()) in call_args
        assert captured.out == ""


def test_cd_too_many_arguments(capsys):
    """cd с слишком большим количеством аргументов показывает ошибку"""
    test_flags = None
    test_arguments = ['dir1', 'dir2', 'dir3']
    
    result = cd.cd(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == "-bash: cd: too many arguments\n"


def test_cd_valid_directory(mock_temp_directory, capsys):
    """cd с валидной директорией переходит в нее"""
    test_flags = None
    test_arguments = [mock_temp_directory]
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        call_args = mock_chdir.call_args[0][0]
        assert mock_temp_directory in call_args
        assert captured.out == ""


def test_cd_to_file(capsys):
    """cd с файлом вместо директории показывает ошибку"""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
        
        try:
            test_flags = None
            test_arguments = [temp_path]
            
            result = cd.cd(test_arguments, test_flags)
            
            captured = capsys.readouterr()
            
            assert result == 1
            assert f"-bash: cd: {Path(temp_path).name}: Not a directory\n" == captured.out
            
        finally:
            os.unlink(temp_path)


def test_cd_nonexistent_directory(capsys):
    """cd с несуществующей директорией показывает ошибку"""
    test_flags = None
    test_arguments = ['/nonexistent/goose/directory']
    
    result = cd.cd(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "-bash: cd: directory:  No such file or directory\n"


def test_cd_with_flags(capsys):
    """cd с флагами показывает ошибку о неподдерживаемых флагах"""
    test_flags = {'l', 'a'}
    test_arguments = ['.']
    
    result = cd.cd(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert "-bash: cd: does not support the flags:" in captured.out
    assert "l" in captured.out
    assert "a" in captured.out


def test_cd_relative_path(capsys):
    """cd с относительным путем переходит в директорию"""
    test_flags = None
    test_arguments = ['.']
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        assert captured.out == ""


def test_cd_expanduser_existing(capsys):
    """cd с путем содержащим ~ переходит в домашнюю директорию"""
    test_flags = None
    test_arguments = ['~']
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        call_args = mock_chdir.call_args[0][0]
        assert str(Path.home()) in call_args
        assert captured.out == ""


def test_cd_expanduser_nonexistent(capsys):
    """cd с путем содержащим ~ для несуществующей директории показывает ошибку"""
    test_flags = None
    test_arguments = ['~/nonexistent_goose_dir']
    
    result = cd.cd(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "-bash: cd: nonexistent_goose_dir:  No such file or directory\n"


def test_cd_empty_string_argument(capsys):
    """cd с пустой строкой в качестве аргумента показывает ошибку"""
    test_flags = None
    test_arguments = ['']
    
    result = cd.cd(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 0
    assert captured.out == ""


def test_cd_current_directory(capsys):
    """cd с текущей директорией работает корректно"""
    test_flags = None
    test_arguments = ['.']
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        assert captured.out == ""


def test_cd_parent_directory(capsys):
    """cd с родительской директорией работает корректно"""
    test_flags = None
    test_arguments = ['..']
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        assert captured.out == ""


def test_cd_with_special_characters(capsys):
    """cd с путем содержащим специальные символы показывает ошибку"""
    test_flags = None
    test_arguments = ['/path/with spaces and $pecial/chars']
    
    result = cd.cd(test_arguments, test_flags)
    
    captured = capsys.readouterr()
    
    assert result == 1
    assert captured.out == "-bash: cd: chars:  No such file or directory\n"


def test_cd_single_dot(capsys):
    """cd с точкой переходит в текущую директорию"""
    test_flags = None
    test_arguments = ['.']
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        assert captured.out == ""


def test_cd_double_dot(capsys):
    """cd с двумя точками переходит в родительскую директорию"""
    test_flags = None
    test_arguments = ['..']
    
    with patch('os.chdir') as mock_chdir:
        result = cd.cd(test_arguments, test_flags)
        
        captured = capsys.readouterr()
        
        assert result == 0
        mock_chdir.assert_called_once()
        assert captured.out == ""