from pygame import Surface, mouse

from const import TILE_SIZE
from enums import TileStates
from sprite import Sprite


class Tile(Sprite):
    """
    The Sprite for a Minesweeper tile.
    """

    def __init__(self, game, surfaces: list[Surface], position: tuple[int, int], top_left: tuple[int, int]):
        """
        Initializes a Tile object.

        Params:
            Any: The Game object managing the current game.
            list[Surface]: A list of the textures for each possible tile state.
            tuple[int, int]: The (x, y) indices of the tile within the field 2D array.
            tuple[int, int]: The position relative to the window of the top left corner of the field.
        """
        self.game_object = game
        self.state = TileStates.HIDDEN
        self.surfaces: list[Surface] = surfaces
        self.position: tuple[int, int] = position
        self.is_mine: bool = False
        
        sprite_pos = ((position[0]*TILE_SIZE + top_left[0]), (position[1]*TILE_SIZE + top_left[1]))
        super().__init__(self.surfaces[self.state], sprite_pos,
                         self.left_click, self.right_click, self.mouse_press, self.mouse_unpress)

    def left_click(self):
        """
        Uncovers the Tile and its surroundings.
        """
        if not self.game_object.game_over:
            buttons_pressed = mouse.get_pressed()
            # right mouse button also pressed
            if buttons_pressed[2]:
                if self.state != TileStates.FLAG:
                    self.game_object.chord(self.position, self.state)
            elif self.state == TileStates.HIDDEN:
                if self.is_mine:
                    self.update_state(TileStates.MINE_HIT)
                    self.game_object.loss()
                else:
                    self.game_object.click_sound.play()
                    self.game_object.uncover(self.position)

    def right_click(self):
        """
        Toggles whether or not the Tile is flagged.
        """
        if not self.game_object.game_over:
            buttons_pressed = mouse.get_pressed()
            # left mouse button also pressed
            if buttons_pressed[0]:
                if self.state != TileStates.FLAG:
                    self.game_object.chord(self.position, self.state)
            elif self.state == TileStates.HIDDEN:
                self.update_state(TileStates.FLAG)
                self.game_object.flags.append(self.position)
                self.game_object.flag_sound.play()
            elif self.state == TileStates.FLAG:
                self.update_state(TileStates.HIDDEN)
                self.game_object.flags.remove(self.position)
    
    def mouse_press(self, buttons: tuple[bool, bool, bool]):
        """
        Displays the pressed texture when the Tile is being clicked.
        Does chording if both the left and right mouse buttons are pressed.

        Params:
            tuple[bool, bool, bool]: A list of mouse buttons that are currently being clicked.
        """
        if not self.game_object.game_over:
            # left click
            if buttons[0]:
                # right click
                if buttons[2]:
                    self.game_object.press_chord(self.position, self.state)
                elif self.state == TileStates.HIDDEN:
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
