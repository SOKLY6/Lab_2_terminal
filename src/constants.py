import shutil
from pathlib import Path

POSSIBLE_SHORT_FLAGS = {'i', 'r', 'l', 'a'}
POSSIBLE_LONS_FLAGS = {'ignore-case', 'recursive', 'long', 'all'}
TRANSFORMATION_FLAGS = {
    'ignore-case': 'i',
    'recursive': 'r',
    'long': 'l',
    'all': 'a',
}

FOR_UNDO_HISTORY: list[list] = []
HISTORY_PATH: Path = Path.home() / '.history'

if not HISTORY_PATH.exists():
    HISTORY_PATH.touch()

TRASH_PATH: Path = Path.home() / '.trash'

if TRASH_PATH.exists():
    shutil.rmtree(TRASH_PATH)
TRASH_PATH.mkdir(exist_ok=True)
