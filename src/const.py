from pathlib import Path


DIFFICULTIES = {
    'beginner': {
        'num_mines': 10,
        'rows': 9,
        'cols': 9
    },
    'intermediate': {
        'num_mines': 40,
        'rows': 16,
        'cols': 16
    },
    'expert': {
        'num_mines': 99,
        'rows': 16,
        'cols': 30
    }
}
FRAMERATE = 30
MARGIN = 1
MAX_NAME_LENGTH = 6
NUM_HIGH_SCORES = 5
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
TILE_SIZE = 16
