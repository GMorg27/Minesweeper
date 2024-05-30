from enum import IntEnum


# defines names for indices of textures from tile_atlas.png
class TileStates(IntEnum):
    UNCOVERED: int = 0
    HIDDEN: int = 9
    FLAG: int = 10
    INCORRECT_FLAG: int = 11
    MINE: int = 12
    MINE_HIT: int = 13
