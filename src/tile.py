from pygame import Surface, mouse

from const import TILE_SIZE
from enums import TileStates
from sprite import Sprite


class Tile(Sprite):
    """
    The Sprite for a Minesweeper tile.
    """

    def __init__(self, surfaces: list[Surface], position: tuple[int, int], top_left: tuple[int, int]):
        """
        Initializes a Tile object.

        Params:
            list[Surface]: A list of the textures for each possible tile state.
            tuple[int, int]: The (x, y) indices of the tile within the field 2D array.
            tuple[int, int]: The position relative to the window of the top left corner of the field.
        """
        self.state = TileStates.HIDDEN
        self.surfaces: list[Surface] = surfaces
        self.position: tuple[int, int] = position
        self.is_mine: bool = False
        
        sprite_pos = ((position[0]*TILE_SIZE + top_left[0]), (position[1]*TILE_SIZE + top_left[1]))
        super().__init__(self.surfaces[self.state], sprite_pos,
                         None, None, self.mouse_press, self.mouse_unpress)
    
    def mouse_press(self, buttons: tuple[bool, bool, bool]):
        """
        Displays the pressed texture when the Tile is being clicked.

        Params:
            tuple[bool, bool, bool]: A list of mouse buttons that are currently being clicked.
        """
        # left click
        if buttons[0] and not buttons[1]:
            if self.state == TileStates.HIDDEN:
                self.image = self.surfaces[TileStates.UNCOVERED]
    
    def mouse_unpress(self):
        """
        Reverts the Tile's texture to its actual state.
        """
        self.image = self.surfaces[self.state]

    def update_state(self, new_state: TileStates):
        """
        Changes the tile's state and updates to the corresponding texture.

        Params:
            TileStates: A new TileState enum value.
        """
        self.state = new_state
        self.image = self.surfaces[self.state]

    def reveal(self):
        """
        Reveals the Tile if it is a hidden mine or incorrectly flagged.
        """
        if self.is_mine:
            if self.state == TileStates.HIDDEN or self.state == TileStates.FLAG:
                self.update_state(TileStates.MINE)
        else:
            if self.state == TileStates.FLAG:
                self.update_state(TileStates.INCORRECT_FLAG)
