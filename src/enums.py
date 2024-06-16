from enum import IntEnum


class FaceExpressions(IntEnum):
    """
    Defines names for integer indices of textures from face_atlas.png.
    """
    HAPPY: int = 0
    SHOCKED: int = 1
    LOSE: int = 2
    WIN: int = 3


class TileStates(IntEnum):
    """
    Defines names for integer indices of textures from tile_atlas.png.
    """
    UNCOVERED: int = 0
    HIDDEN: int = 9
    FLAG: int = 10
    INCORRECT_FLAG: int = 11
    MINE: int = 12
    MINE_HIT: int = 13
