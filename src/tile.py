from const import TILE_SIZE
from sprite import Sprite
from tile_states import TileStates


# the sprite for a Minesweeper tile
class Tile(Sprite):
    def __init__(self, game, surfaces, position: tuple[int, int], top_left: tuple[int, int]):
        self.game_object = game
        self.state = TileStates.HIDDEN
        self.surfaces = surfaces
        self.position: tuple[int, int] = position
        self.is_mine: bool = False
        
        sprite_pos = ((position[0]*TILE_SIZE + top_left[0]), (position[1]*TILE_SIZE + top_left[1]))
        super().__init__(self.surfaces[self.state], sprite_pos,
                         self.left_click, self.right_click, self.mouse_press, self.mouse_unpress)

    # left click uncovers the tile and possibly its surroundings
    def left_click(self, buttons: tuple[bool, bool, bool]):
        if not self.game_object.game_over:
            # right mouse button also pressed
            if buttons[2]:
                if self.state != TileStates.FLAG:
                    self.game_object.chord(self.position, self.state)
            elif self.state == TileStates.HIDDEN:
                if self.is_mine:
                    self.update_state(TileStates.MINE_HIT)
                    self.game_object.loss()
                else:
                    self.game_object.uncover(self.position)

    # right click toggles whether the tile is flagged
    def right_click(self, buttons: tuple[bool, bool, bool]):
        if not self.game_object.game_over:
            # left mouse button also pressed
            if buttons[0]:
                self.game_object.chord(self.position, self.state)
            elif self.state == TileStates.HIDDEN:
                self.update_state(TileStates.FLAG)
                self.game_object.flags.append(self.position)
            elif self.state == TileStates.FLAG:
                self.update_state(TileStates.HIDDEN)
                self.game_object.flags.remove(self.position)
    
    # display hidden tile press texture or do chording based on mouse button(s) pressed
    def mouse_press(self, buttons: tuple[bool, bool, bool]):
        if not self.game_object.game_over:
            # left click
            if buttons[0]:
                if buttons[2]:
                    self.game_object.press_chord(self.position, self.state)
                elif self.state == TileStates.HIDDEN:
                    self.image = self.surfaces[TileStates.UNCOVERED]
    
    # revert tile texture to actual state
    def mouse_unpress(self):
        self.image = self.surfaces[self.state]

    # change the tile's state and update to the corresponding texture
    def update_state(self, new_state: TileStates):
        self.state = new_state
        self.image = self.surfaces[self.state]

    # reveal the tile if it is a hidden mine or incorrectly-flagged
    def reveal(self):
        if self.is_mine:
            if self.state == TileStates.HIDDEN or self.state == TileStates.FLAG:
                self.update_state(TileStates.MINE)
        else:
            if self.state == TileStates.FLAG:
                self.update_state(TileStates.INCORRECT_FLAG)
