from enum import IntEnum


# defines names for indices of textures from face_atlas.png
class FaceStates(IntEnum):
    DEFAULT: int = 0
    WORRIED: int = 1
    LOSS: int = 2
    WIN: int = 3
    