import pygame
from pygame.locals import *
import random

from button import Button
from const import MARGIN, ROOT_DIR, TILE_SIZE
from sprite import Sprite
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
FRAMERATE = 30

# pygame window specifications
BG_COLOR = (200, 200, 200)
BANNER_HEIGHT = 3.5 * TILE_SIZE
BANNER_COLOR = (180, 180, 180)
BANNER_FONT_SIZE = 25
BANNER_FONT_COLOR = (255, 0, 0)
BANNER_FONT_BG = (0, 0, 0)


# handles the pygame display and all game events
class Game:
    def __init__(self, difficulty: str):
        difficulty_data = DIFFICULTIES[difficulty]
        self.game_over: bool = False
        self.quit: bool = False
        self.num_mines: int = difficulty_data['num_mines']
        self.rows: int = difficulty_data['rows']
        self.cols: int = difficulty_data['cols']
        self.tiles: list[list[Tile]] = []
        self.tile_surfaces: list[pygame.Surface] = []
        self.face_surfaces: list[pygame.Surface] = []
        self.mines: list[tuple[int, int]] = []
        self.flags: list[tuple[int, int]] = []
        self.to_chord: list[Tile] = []
        self.uncovered_tiles: int = 0
        self.time: float = 0.0

        # initialize pygame window
        if self.cols >= DIFFICULTIES['intermediate']['cols']:
            self.screen_width = TILE_SIZE * (self.cols + 2*MARGIN)
        else:
            self.screen_width = TILE_SIZE * (DIFFICULTIES['intermediate']['cols'] + 2*MARGIN)
        self.screen_height = TILE_SIZE * (self.rows + 2*MARGIN) + BANNER_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Minesweeper')
        icon =  pygame.image.load(ROOT_DIR + '/assets/textures/mine.png')
        pygame.display.set_icon(icon)
        pygame.font.init()
        self.banner_font = pygame.font.Font(ROOT_DIR + '/assets/fonts/timer.ttf', BANNER_FONT_SIZE)
        
    # load game elements and execute main game loop
    def start(self):
        # load tile textures from tile_atlas.png
        tile_map = pygame.image.load(ROOT_DIR + '/assets/textures/tile_atlas.png')
        for y in range(4):
            for x in range(4):
                image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                area = (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                image.blit(tile_map, (0, 0), area)
                self.tile_surfaces.append(image)
        
        # load face button texture tuples (unclicked, clicked) from face_atlas.png
        faces = pygame.image.load(ROOT_DIR + '/assets/textures/face_atlas.png')
        hidden_area = ((TileStates.HIDDEN%4)*TILE_SIZE, int(TileStates.HIDDEN/4)*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        uncovered_area = ((TileStates.UNCOVERED%4)*TILE_SIZE, int(TileStates.UNCOVERED/4)*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        for x in range(4):
            # place each face texture on top of unclicked and clicked tile textures
            default_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            clicked_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            default_image.blit(tile_map, (0, 0), hidden_area)
            clicked_image.blit(tile_map, (0, 0), uncovered_area)
            default_image = pygame.transform.scale(default_image, (3*TILE_SIZE, 3*TILE_SIZE))
            clicked_image = pygame.transform.scale(clicked_image, (3*TILE_SIZE, 3*TILE_SIZE))
            # area on face_atlas.png to blit from
            area = (x*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
            face_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            face_image.blit(faces, (0, 0), area)
            face_image = pygame.transform.scale(face_image, (2*TILE_SIZE, 2*TILE_SIZE))
            face_loc = ((default_image.get_width() - face_image.get_width())/2, (default_image.get_height() - face_image.get_height())/2)
            default_image.blit(face_image, face_loc)
            clicked_image.blit(face_image, face_loc)
            self.face_surfaces.append((default_image, clicked_image))
        button_size = (default_image.get_width(), default_image.get_height())
        
        # load tile sprites
        tile_group = pygame.sprite.Group()
        top_left = ((self.screen_width - self.cols*TILE_SIZE)/2, (self.screen_height - BANNER_HEIGHT - self.rows*TILE_SIZE)/2 + BANNER_HEIGHT)
        for x in range(self.cols):
            self.tiles.append([])
            for y in range(self.rows):
                new_tile = Tile(self, self.tile_surfaces, (x, y), top_left)
                self.tiles[x].append(new_tile)
                tile_group.add(new_tile)
        
        # load top banner
        banner_group = pygame.sprite.Group()
        banner_image = pygame.Surface((self.screen_width, BANNER_HEIGHT))
        banner_image.fill(BANNER_COLOR)
        banner = Sprite(banner_image, (0, 0))
        flag_image = pygame.image.load(ROOT_DIR + '/assets/textures/flag.png')
        flag_image = pygame.transform.scale(flag_image, (2*TILE_SIZE, 2*TILE_SIZE))
        flag_x = MARGIN * TILE_SIZE
        flag_y = (BANNER_HEIGHT - flag_image.get_height()) / 2
        flag_icon = Sprite(flag_image, (flag_x, flag_y))
        button_x = (self.screen_width - button_size[0]) / 2
        button_y = (BANNER_HEIGHT - button_size[1]) / 2
        face_button = Button(self.face_surfaces, (button_x, button_y), left_click=None)
        
        # game loop
        clock = pygame.time.Clock()
        while not self.quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    self.game_over = True
                    self.quit = True
                    break
                elif event.type == MOUSEBUTTONUP:
                    for sprite in tile_group:
                        sprite.check_click(event.pos, event.button)
                    face_button.check_click(event.pos, event.button)

            if not self.quit:
                face_button.check_mouse_press(pygame.mouse.get_pos())
                if not self.game_over:
                    for sprite in tile_group:
                        if sprite not in self.to_chord:
                            sprite.check_mouse_press(pygame.mouse.get_pos())
                    self.to_chord = []
                    
                    self.time += 1.0 / FRAMERATE

                # update banner elements
                banner_group = pygame.sprite.Group()
                # flag counter
                flags_remaining = self.num_mines - len(self.flags)
                text = str(abs(flags_remaining))
                if flags_remaining >= 0:
                    text = text.rjust(3, '0')
                else:
                    text = '-' + text.rjust(2, '0')
                text_surface = self.banner_font.render(text, False, BANNER_FONT_COLOR, BANNER_FONT_BG)
                flag_counter = Sprite(text_surface,
                                      (flag_x + flag_image.get_width(), (BANNER_HEIGHT - BANNER_FONT_SIZE)/2))
                # timer
                seconds = int(self.time)
                minutes_text = str(int(seconds / 60)).rjust(2, '0')
                seconds_text =  str(seconds % 60).rjust(2, '0')
                text = minutes_text + ':' + seconds_text
                text_surface = self.banner_font.render(text, False, BANNER_FONT_COLOR, BANNER_FONT_BG)
                timer = Sprite(text_surface,
                               (self.screen_width - MARGIN*TILE_SIZE - text_surface.get_width(), (BANNER_HEIGHT - BANNER_FONT_SIZE)/2))
                banner_group.add(banner, flag_icon, flag_counter, timer, face_button)

                # render game elements
                self.screen.fill(BG_COLOR)
                tile_group.draw(self.screen)
                banner_group.draw(self.screen)
                pygame.display.flip()
            
            clock.tick(FRAMERATE)
    
    # randomly populates the field with mines, excluding the clicked tile
    def plant_mines(self, click_pos: tuple[int, int]):
        for i in range(self.num_mines):
            while True:
                rand_row = random.randint(0, self.rows - 1)
                rand_col = random.randint(0, self.cols - 1)
                if (rand_col, rand_row) != click_pos and not self.tiles[rand_col][rand_row].is_mine:
                    self.tiles[rand_col][rand_row].is_mine = True
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
                        candidate = self.tiles[x][y]
                        if candidate.state == TileStates.HIDDEN:
                            neighbors.append((x, y))
                        if candidate.is_mine:
                            mine_count += 1
            self.tiles[current[0]][current[1]].update_state(TileStates.UNCOVERED + mine_count)

            # stop searching along edges with neighboring mines
            if mine_count == 0:
                bfs_queue.extend(neighbors)

    # returns whether a tile can be chorded and the list of tiles that would be uncovered
    def get_chord_info(self, click_pos: tuple[int, int], num_flags: int) -> tuple[bool, list[Tile]]:
        flag_count = 0
        neighbors = []
        x_min = click_pos[0] - 1 if click_pos[0] - 1 >= 0 else 0
        y_min = click_pos[1] - 1 if click_pos[1] - 1 >= 0 else 0
        x_max = click_pos[0] + 1 if click_pos[0] + 1 < self.cols else self.cols - 1
        y_max = click_pos[1] + 1 if click_pos[1] + 1 < self.rows else self.rows - 1
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                if (x, y) != (click_pos[0], click_pos[1]):
                    neighbor = self.tiles[x][y]
                    if neighbor.state == TileStates.FLAG:
                        flag_count += 1
                    elif neighbor.state == TileStates.HIDDEN:
                        neighbors.append(neighbor)

        return (flag_count == num_flags, neighbors)

    # if the correct number of adjacent tiles has been flagged, uncover all adjacent hidden tiles
    def chord(self, click_pos: tuple[int, int], num_flags: int):
        chord_info = self.get_chord_info(click_pos, num_flags)
        self.to_chord = chord_info[1]

        if chord_info[0]:
            for tile in self.to_chord:
                if tile.is_mine:
                    tile.update_state(TileStates.MINE_HIT)
                    if not self.game_over:
                        self.loss()
                else:
                    self.uncover(tile.position)
    
    # display pressed animation for all tiles that would be uncovered with a chord
    def press_chord(self, click_pos: tuple[int, int], num_flags: int):
        self.to_chord = self.get_chord_info(click_pos, num_flags)[1]
        for tile in self.to_chord:
            if tile.state == TileStates.HIDDEN:
                tile.image = tile.surfaces[TileStates.UNCOVERED]

    # ends the game and opens the loss display
    def loss(self):
        self.game_over = True
        for pos in self.mines:
            self.tiles[pos[0]][pos[1]].reveal()
        for pos in self.flags:
            self.tiles[pos[0]][pos[1]].reveal()
        