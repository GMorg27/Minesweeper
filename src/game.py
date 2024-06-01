import pygame
from pygame.locals import *
import random

from const import MARGIN, ROOT_DIR, TILE_SIZE
from tile import Tile
from tile_states import TileStates


# game metadata
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

# pygame window specifications
BG_COLOR = (200, 200, 200)


# handles the pygame display and all game events
class Game:
    def __init__(self, difficulty: str):
        difficulty_data = DIFFICULTIES[difficulty]
        self.game_over = False
        self.quit = False
        self.num_mines = difficulty_data['num_mines']
        self.rows = difficulty_data['rows']
        self.cols = difficulty_data['cols']
        self.tiles = []
        self.tile_surfaces = []
        self.tile_group = pygame.sprite.Group()
        self.mines = []
        self.flags = []
        self.uncovered_tiles = 0

        # initialize pygame window
        screen_width = TILE_SIZE * (self.cols + 2*MARGIN)
        screen_height = TILE_SIZE * (self.rows + 2*MARGIN)
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Minesweeper')
        icon =  pygame.image.load(ROOT_DIR + '/textures/icon.png')
        pygame.display.set_icon(icon)
        
    # load tiles and execute main game loop
    def start(self):
        # load tile textures from tile_atlas.png
        tile_map = pygame.image.load(ROOT_DIR + '/textures/tile_atlas.png')
        for y in range(4):
            for x in range(4):
                image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                area = (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                image.blit(tile_map, (0, 0), area)
                self.tile_surfaces.append(image)
        
        # load tile sprites
        top_left = (MARGIN * TILE_SIZE, MARGIN * TILE_SIZE)
        for y in range(self.rows):
            self.tiles.append([])
            for x in range(self.cols):
                new_tile = Tile(self, self.tile_surfaces, (x, y), top_left)
                self.tiles[y].append(new_tile)
                self.tile_group.add(new_tile)
        
        # game loop
        while not self.quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    self.game_over = True
                    self.quit = True
                    break
                elif event.type == MOUSEBUTTONUP:
                    for sprite in self.tile_group:
                        sprite.check_click(event.pos, event.button)

            if not self.quit:
                # render game elements
                self.screen.fill(BG_COLOR)
                self.tile_group.draw(self.screen)
                pygame.display.update()
    
    # randomly populates the field with mines, excluding the clicked tile
    def plant_mines(self, click_pos: tuple[int, int]):
        for i in range(self.num_mines):
            while True:
                rand_row = random.randint(0, self.rows - 1)
                rand_col = random.randint(0, self.cols - 1)
                if (rand_col, rand_row) != click_pos and not self.tiles[rand_row][rand_col].is_mine:
                    self.tiles[rand_row][rand_col].is_mine = True
                    self.mines.append((rand_col, rand_row))
                    break

    # uncovers the tile at a given (x, y) position and possibly its surroundings
    def uncover(self, click_pos: tuple[int, int]):
        if len(self.mines) == 0:
            self.plant_mines(click_pos)

        # perform breadth first search starting at the clicked tile
        bfs_queue = [click_pos]
        while len(bfs_queue) > 0:
            current = bfs_queue.pop(0)
            mine_count = 0
            neighbors = []
            x_min = current[0] - 1 if current[0] - 1 >= 0 else 0
            y_min = current[1] - 1 if current[1] - 1 >= 0 else 0
            x_max = current[0] + 1 if current[0] + 1 < self.cols else self.cols - 1
            y_max = current[1] + 1 if current[1] + 1 < self.rows else self.rows - 1
            for x in range(x_min, x_max + 1):
                for y in range(y_min, y_max + 1):
                    if (x, y) != (current[0], current[1]):
                        candidate = self.tiles[y][x]
                        if candidate.state == TileStates.HIDDEN:
                            neighbors.append((x, y))
                        if candidate.is_mine:
                            mine_count += 1
            self.tiles[current[1]][current[0]].update_state(TileStates.UNCOVERED + mine_count)

            # stop searching along edges with neighboring mines
            if mine_count == 0:
                bfs_queue.extend(neighbors)

    # ends the game and opens the loss display
    def loss(self):
        self.game_over = True
        for pos in self.mines:
            self.tiles[pos[1]][pos[0]].reveal()
        for pos in self.flags:
            self.tiles[pos[1]][pos[0]].reveal()
        