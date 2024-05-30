import pygame
from pygame.locals import *

from tile import Tile
from tile_states import TileStates


# game metadata
difficulties = {
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

# pygame window specifications
bg_color = (255, 255, 255)
tile_size = 16


# handles the pygame display and all game events
class Game:
    def __init__(self, difficulty):
        difficulty_data = difficulties[difficulty]
        self.num_mines = difficulty_data['num_mines']
        self.rows = difficulty_data['rows']
        self.cols = difficulty_data['cols']
        self.tiles = []
        self.tile_surfaces = []
        self.tile_group = pygame.sprite.Group()
        self.bombs = []
        self.flags = []
        self.uncovered_tiles = 0
        self.mines_planted = False

        # initialize pygame window
        self.screen = pygame.display.set_mode((self.cols * tile_size, self.rows * tile_size))
        pygame.display.set_caption('Minesweeper')
        
    # load tiles and execute main game loop
    def start(self):
        # load tile textures from tile_atlas.png
        tile_map = pygame.image.load('../textures/tile_atlas.png')
        for y in range(4):
            for x in range(4):
                image = pygame.Surface((tile_size, tile_size))
                area = (x*tile_size, y*tile_size, tile_size, tile_size)
                image.blit(tile_map, (0, 0), area)
                self.tile_surfaces.append(image)
        
        # load tile sprites
        for y in range(self.rows):
            self.tiles.append([])
            for x in range(self.cols):
                new_tile = Tile(self, self.tile_surfaces, (x, y))
                self.tiles[y].append(new_tile)
                self.tile_group.add(new_tile)
        
        # game loop
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                elif event.type == MOUSEBUTTONUP:
                    for sprite in self.tile_group:
                        sprite.check_click(event.pos, event.button)

            # render game elements
            self.screen.fill(bg_color)
            self.tile_group.draw(self.screen)
            pygame.display.update()
                