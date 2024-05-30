from sprite import Sprite
from tile_states import TileStates


# the sprite for a Minesweeper tile
class Tile(Sprite):
    size = 16

    def __init__(self, game, surfaces, position):
        self.game_object = game
        self.state = TileStates.HIDDEN
        self.surfaces = surfaces
        self.position = position
        self.is_bomb = False
        
        sprite_pos = (position[0]*self.size, position[1]*self.size)
        super().__init__(self.surfaces[self.state], sprite_pos,
                         self.left_click, self.right_click)

    # TODO
    def left_click(self):
        pass

    # TODO
    def right_click(self):
        pass
