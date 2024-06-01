from const import MARGIN, TILE_SIZE
from sprite import Sprite
from tile_states import TileStates


# the sprite for a Minesweeper tile
class Tile(Sprite):
    def __init__(self, game, surfaces, position: tuple[int, int], top_left: tuple[int, int]):
        self.game_object = game
        self.state = TileStates.HIDDEN
        self.surfaces = surfaces
        self.position = position
        self.is_mine = False
        
        sprite_pos = ((position[0]*TILE_SIZE + top_left[0]), (position[1]*TILE_SIZE + top_left[1]))
        super().__init__(self.surfaces[self.state], sprite_pos,
                         self.left_click, self.right_click)

    # left click uncovers the tile and possibly its surroundings
    def left_click(self):
        if not self.game_object.game_over:
            if self.state == TileStates.HIDDEN:
                if self.is_mine:
                    self.update_state(TileStates.MINE_HIT)
                    self.game_object.loss()
                else:
                    self.game_object.uncover(self.position)

    # right click toggles whether the tile is flagged
    def right_click(self):
        if not self.game_object.game_over:
            if self.state == TileStates.HIDDEN:
                self.update_state(TileStates.FLAG)
                self.game_object.flags.append(self.position)
            elif self.state == TileStates.FLAG:
                self.update_state(TileStates.HIDDEN)
                self.game_object.flags.remove(self.position)

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
