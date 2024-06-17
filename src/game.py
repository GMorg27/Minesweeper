import pygame
from pygame.locals import *
import random

from button import Button
from const import MARGIN, ROOT_DIR, TILE_SIZE
from enums import FaceExpressions, TileStates
from sprite import Sprite
from tile import Tile
import utils


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
WIN_MENU_SIZE = (9*TILE_SIZE, 11*TILE_SIZE)
WIN_MENU_COLOR = (255, 255, 255, 200)
WIN_FONT_SIZE_TITLE = 24
WIN_FONT_SIZE_LG = 18
WIN_FONT_SIZE_SM = 15
WIN_FONT_COLOR = (0, 0, 0)
WIN_BUTTON_SIZE = (60, 25)
PAD_Y = 5
CLICK_DARKENING = 50


class Game:
    """
    A class to handle the pygame window and all game events.
    """

    def __init__(self, difficulty: str):
        """
        Initializes a Game object and the pygame window.

        Params:
            str: The game difficulty.
        """
        difficulty_data = DIFFICULTIES[difficulty]
        self.game_over: bool = False
        self.quit: bool = False
        self.num_mines: int = difficulty_data['num_mines']
        self.rows: int = difficulty_data['rows']
        self.cols: int = difficulty_data['cols']
        self.tiles: list[list[Tile]] = []
        self.visited: list[list[bool]] = [[False]*self.rows for y in range(self.cols)]
        self.tile_surfaces: list[pygame.Surface] = []
        self.face_surfaces: list[pygame.Surface] = []
        self.mines: list[tuple[int, int]] = []
        self.flags: list[tuple[int, int]] = []
        self.to_chord: list[Tile] = []
        self.uncovered_tiles: int = 0
        self.time: float = 0.0
        self.face_state = FaceExpressions.HAPPY

        # initialize pygame window
        if self.cols >= DIFFICULTIES['intermediate']['cols']:
            self.screen_width = TILE_SIZE * (self.cols + 2*MARGIN)
        else:
            self.screen_width = TILE_SIZE * (DIFFICULTIES['intermediate']['cols'] + 2*MARGIN)
        self.screen_height = TILE_SIZE * (self.rows + 2*MARGIN) + BANNER_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Minesweeper')
        icon = pygame.image.load(ROOT_DIR + '/assets/textures/mine.png')
        pygame.display.set_icon(icon)
        pygame.font.init()
        self.banner_font = pygame.font.Font(ROOT_DIR + '/assets/fonts/timer.ttf', BANNER_FONT_SIZE)
        self.win_font_title = pygame.font.Font(ROOT_DIR + '/assets/fonts/courier_new_bd.ttf', WIN_FONT_SIZE_TITLE)
        self.win_font_lg = pygame.font.Font(ROOT_DIR + '/assets/fonts/helvetica.ttf', WIN_FONT_SIZE_LG)
        self.win_font_sm = pygame.font.Font(ROOT_DIR + '/assets/fonts/helvetica.ttf', WIN_FONT_SIZE_SM)
        
    def start(self):
        """
        Load game elements and execute main loop.
        """
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
        top_left = ((self.screen_width - self.cols*TILE_SIZE)/2, (self.screen_height - self.rows*TILE_SIZE + BANNER_HEIGHT)/2)
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
        face_button = Button(self.face_surfaces, (button_x, button_y), self.restart)

        # load win menu
        win_menu_group = pygame.sprite.Group()
        top_left = ((self.screen_width - WIN_MENU_SIZE[0])/2, (self.screen_height - WIN_MENU_SIZE[1] + BANNER_HEIGHT)/2)
        win_menu_rect = pygame.Rect(top_left[0], top_left[1], WIN_MENU_SIZE[0], WIN_MENU_SIZE[1])
        win_menu_bg = pygame.Surface(pygame.Rect(win_menu_rect).size, pygame.SRCALPHA)
        pygame.draw.rect(win_menu_bg, WIN_MENU_COLOR, win_menu_bg.get_rect())
        text_surface = self.win_font_title.render("You won!", False, WIN_FONT_COLOR)
        win_message_pos = (top_left[0] + (WIN_MENU_SIZE[0] - text_surface.get_width())/2, top_left[1] + PAD_Y)
        win_message = Sprite(text_surface, win_message_pos)
        # the height at which to position the time display on win
        time_disp_pos_y = win_message_pos[1] + text_surface.get_height() + PAD_Y

        button_pos_x = top_left[0] + (WIN_MENU_SIZE[0] - WIN_BUTTON_SIZE[0])/2
        quit_pos_y = top_left[1] + WIN_MENU_SIZE[1] - WIN_BUTTON_SIZE[1] - PAD_Y
        quit_button_rect = pygame.Rect(button_pos_x, quit_pos_y, WIN_BUTTON_SIZE[0], WIN_BUTTON_SIZE[1])
        quit_button_surface = pygame.Surface(pygame.Rect(quit_button_rect).size, pygame.SRCALPHA)
        quit_button_surface_clicked = pygame.Surface(pygame.Rect(quit_button_rect).size, pygame.SRCALPHA)
        pygame.draw.rect(quit_button_surface, (255, 0, 0), quit_button_surface.get_rect())
        pygame.draw.rect(quit_button_surface_clicked, (255 - CLICK_DARKENING, 0, 0), quit_button_surface.get_rect())
        quit_text = self.win_font_sm.render("Quit", False, WIN_FONT_COLOR)
        text_position = ((quit_button_rect.width - quit_text.get_width())/2, (quit_button_rect.height - quit_text.get_height())/2)
        quit_button_surface.blit(quit_text, text_position)
        quit_button_surface_clicked.blit(quit_text, text_position)
        quit_button = Button([(quit_button_surface, quit_button_surface_clicked)], (button_pos_x, quit_pos_y), self.do_quit)

        win_menu_group.add(win_message, quit_button)

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
                    # prevent multiple sprites from being clicked at the same time
                    some_clicked = False
                    if not self.game_over:
                        for sprite in tile_group:
                            if sprite.check_click(event.pos, event.button):
                                some_clicked = True
                                break
                    elif not some_clicked and self.face_state == FaceExpressions.WIN:
                        some_clicked = quit_button.check_click(event.pos, event.button)
                    if not some_clicked:
                        some_clicked = face_button.check_click(event.pos, event.button)

            if not self.quit:
                face_button.check_mouse_press(pygame.mouse.get_pos())

                if not self.game_over:
                    buttons_pressed = pygame.mouse.get_pressed()
                    if buttons_pressed[0]:
                        click_location = pygame.mouse.get_pos()
                        bottom_right = (top_left[0] + TILE_SIZE*self.cols, top_left[1] + TILE_SIZE*self.rows)
                        if click_location[0] >= top_left[0] and click_location[1] >= top_left[1] \
                            and click_location[0] <= bottom_right[0] and click_location[1] <= bottom_right[1]:
                            self.face_state = FaceExpressions.SHOCKED
                        else:
                            self.face_state = FaceExpressions.HAPPY
                    else:
                        self.face_state = FaceExpressions.HAPPY
                
                    for sprite in tile_group:
                        if sprite not in self.to_chord:
                            sprite.check_mouse_press(pygame.mouse.get_pos())
                    self.to_chord = []

                    if len(self.mines) > 0:
                        self.time += 1.0 / FRAMERATE
                else:
                    quit_button.check_mouse_press(pygame.mouse.get_pos())

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
                timer_text = utils.time_to_str(self.time)
                text_surface = self.banner_font.render(timer_text, False, BANNER_FONT_COLOR, BANNER_FONT_BG)
                timer = Sprite(text_surface,
                               (self.screen_width - MARGIN*TILE_SIZE - text_surface.get_width(), (BANNER_HEIGHT - BANNER_FONT_SIZE)/2))
                face_button.state = self.face_state
                banner_group.add(banner, flag_icon, flag_counter, timer, face_button)

                # render game elements
                self.screen.fill(BG_COLOR)
                tile_group.draw(self.screen)
                banner_group.draw(self.screen)
                if self.game_over and self.face_state == FaceExpressions.WIN:
                    self.screen.blit(win_menu_bg, win_menu_rect)
                    win_menu_group.draw(self.screen)

                    win_menu_dynamic_group = pygame.sprite.Group()
                    text_surface = self.win_font_lg.render(timer_text, False, WIN_FONT_COLOR)
                    time_display = Sprite(text_surface,
                            (top_left[0] + (WIN_MENU_SIZE[0] - text_surface.get_width())/2, time_disp_pos_y))
                    win_menu_dynamic_group.add(time_display)
                    win_menu_dynamic_group.draw(self.screen)
                pygame.display.flip()
            
            clock.tick(FRAMERATE)

    def restart(self):
        """
        Reset game variables and Tiles.
        """
        self.game_over = False
        self.visited: list[list[bool]] = [[False]*self.rows for y in range(self.cols)]
        self.mines = []
        self.flags = []
        self.uncovered_tiles: int = 0
        self.time: float = 0.0

        for x in range(self.cols):
            for y in range(self.rows):
                self.tiles[x][y].update_state(TileStates.HIDDEN)
                self.tiles[x][y].is_mine = False

    def plant_mines(self, click_pos: tuple[int, int]):
        """
        Randomly populates the field with mines, excluding the clicked Tile.

        Params:
            tuple[int, int]: The position (x, y) within the field of the clicked Tile.
        """
        for i in range(self.num_mines):
            while True:
                rand_row = random.randint(0, self.rows - 1)
                rand_col = random.randint(0, self.cols - 1)
                if (rand_col, rand_row) != click_pos and not self.tiles[rand_col][rand_row].is_mine:
                    self.tiles[rand_col][rand_row].is_mine = True
                    self.mines.append((rand_col, rand_row))
                    break

    def uncover(self, click_pos: tuple[int, int]):
        """
        Uncovers the Tile and its surroundings at a given position.

        Params:
            tuple[int, int]: The position (x, y) within the field of the Tile to uncover.
        """
        if len(self.mines) == 0:
            self.plant_mines(click_pos)

        # perform breadth first search starting at the clicked tile
        bfs_queue = [click_pos]
        self.visited[click_pos[0]][click_pos[1]] = True
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
                        if not self.visited[x][y] and candidate.state == TileStates.HIDDEN:
                            neighbors.append((x, y))
                        if candidate.is_mine:
                            mine_count += 1
            
            self.tiles[current[0]][current[1]].update_state(TileStates.UNCOVERED + mine_count)
            self.uncovered_tiles += 1

            if self.uncovered_tiles == self.rows*self.cols - self.num_mines:
                self.win()
                return

            # stop searching along edges with neighboring mines
            if mine_count == 0:
                bfs_queue.extend(neighbors)
                for position in neighbors:
                    self.visited[position[0]][position[1]] = True

    def get_chord_info(self, click_pos: tuple[int, int], num_flags: int) -> tuple[bool, list[Tile]]:
        """
        Checks if a tile can be chorded and gets the list of tiles that would be uncovered with a chord
            (left and right click simultaneously).

        Params:
            tuple[int, int]: The position (x, y) within the field of the Tile.
            int: The number of flags that must be adjacent to the Tile in order to chord.
        
        Returns:
            tuple[bool, list[Tile]]: A boolean representing whether the Tile can currently be chorded
                and the list of tiles that would be uncovered if the chord was valid.
        """
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

    def chord(self, click_pos: tuple[int, int], num_flags: int):
        """
        If the correct number of adjacent Tiles has been flagged, uncover all adjacent hidden Tiles.

        Params:
            tuple[int, int]: The position (x, y) within the field of the center Tile.
            int: The number of flags that must be adjacent to the Tile in order to chord.
        """
        chord_info = self.get_chord_info(click_pos, num_flags)
        self.to_chord = chord_info[1]

        if chord_info[0]:
            for tile in self.to_chord:
                if tile.is_mine:
                    tile.update_state(TileStates.MINE_HIT)
                    self.loss()
                    return
            
            for tile in self.to_chord:
                if not self.visited[tile.position[0]][tile.position[1]]:
                    self.uncover(tile.position)
    
    def press_chord(self, click_pos: tuple[int, int], num_flags: int):
        """
        Display the pressed texture for all Tiles that would be uncovered with a chord.

        Params:
            tuple[int, int]: The position (x, y) within the field of the center Tile.
            int: The number of flags that must be adjacent to the Tile in order to chord.
        """
        self.to_chord = self.get_chord_info(click_pos, num_flags)[1]
        for tile in self.to_chord:
            if tile.state == TileStates.HIDDEN:
                tile.image = tile.surfaces[TileStates.UNCOVERED]

    def win(self):
        """
        Ends the game and updates the face Button to signify a win.
        """
        self.game_over = True
        self.face_state = FaceExpressions.WIN

    def loss(self):
        """
        Ends the game, reveals mistakes and remaining mines, and updates the face Button to signify a loss.
        """
        self.game_over = True
        self.face_state = FaceExpressions.LOSE
        for pos in self.mines:
            self.tiles[pos[0]][pos[1]].reveal()
        for pos in self.flags:
            self.tiles[pos[0]][pos[1]].reveal()
    
    def do_quit(self):
        """
        Quits the game, exiting the program.
        """
        self.quit = True
