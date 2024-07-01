import pygame
from pygame.locals import *
import random

from button import Button
from const import DIFFICULTIES, FRAMERATE, MARGIN, MAX_NAME_LENGTH, NUM_HIGH_SCORES, ROOT_DIR, TILE_SIZE
from data import Data
from enums import FaceExpressions, TileStates
from sprite import Sprite
from tile import Tile
from utils import time_to_str


# pygame window specifications
BG_COLOR = (200, 200, 200)
BANNER_HEIGHT = 3.5 * TILE_SIZE
BANNER_COLOR = (180, 180, 180)
BANNER_FONT_SIZE = 25
BANNER_FONT_COLOR = (255, 0, 0)
BANNER_FONT_BG = (0, 0, 0)
WIN_SCREEN_SIZE = (9*TILE_SIZE, 11*TILE_SIZE)
WIN_SCREEN_COLOR = (255, 255, 255, 200)
WIN_FONT_SIZE_LG = 25
WIN_FONT_SIZE_MD = 20
WIN_FONT_SIZE_SM = 12
WIN_FONT_COLOR = (0, 0, 0)
HIGH_SCORE_FONT_COLOR = (218, 165, 32)
WIN_PAD_Y = 5


class Game():
    """
    A class that handles the pygame display and all game events.
    """
    difficulty: str
    screen: pygame.Surface
    face_button: Button
    sound_button: Button
    win_screen_bg: pygame.Surface
    win_screen_rect: pygame.Rect

    def __init__(self, file_io: Data = Data()):
        """
        Initializes a Game object and loads all assets.

        Params:
            Data: A Data object to read and write to files. Will initialize one if not provided.
        """
        # game variables
        self.game_over: bool = False
        self.num_mines: int = 0
        self.rows: int = 0
        self.cols: int = 0
        self.tiles: list[list[Tile]] = []
        self.visited: list[list[bool]] = []
        self.mines: list[tuple[int, int]] = []
        self.flags: list[tuple[int, int]] = []
        self.to_chord: list[Tile] = []
        self.uncovered_tiles: int = 0
        self.time: float = 0.0

        # window variables
        self.screen_width: int = 0
        self.screen_height: int = 0
        self.quitting: bool = False
        self.reopen_tkinter: bool = False
        self.field_top_left: tuple[int, int] = (0, 0)
        self.banner_sprites: list[Sprite] = []
        self.footer_sprites: list[Sprite] = []
        self.win_screen_sprites: list[Sprite] = []
        self.buttons: list[Button] = []

        # file input/output
        self.player_name: str = ''
        self.player_rank: int = -1
        self.file_io: Data = file_io
        settings = self.file_io.get_settings()
        self.sound_enabled: bool = settings['sound_enabled']

        self.icon = pygame.image.load(ROOT_DIR + '/assets/textures/mine.png')
        self.tile_map = pygame.image.load(ROOT_DIR + '/assets/textures/tile_atlas.png')
        self.face_map = pygame.image.load(ROOT_DIR + '/assets/textures/face_atlas.png')
        self.flag_image = pygame.image.load(ROOT_DIR + '/assets/textures/flag.png')
        self.home_image = pygame.image.load(ROOT_DIR + '/assets/textures/home.png')
        self.home_image_clicked = pygame.image.load(ROOT_DIR + '/assets/textures/home_clicked.png')
        self.quit_image = pygame.image.load(ROOT_DIR + '/assets/textures/quit.png')
        self.quit_image_clicked = pygame.image.load(ROOT_DIR + '/assets/textures/quit_clicked.png')
        self.sound_image = pygame.image.load(ROOT_DIR + '/assets/textures/sound_on.png')
        self.sound_image_clicked = pygame.image.load(ROOT_DIR + '/assets/textures/sound_on_clicked.png')
        self.mute_image = pygame.image.load(ROOT_DIR + '/assets/textures/sound_mute.png')
        self.mute_image_clicked = pygame.image.load(ROOT_DIR + '/assets/textures/sound_mute_clicked.png')

        pygame.font.init()
        self.banner_font = pygame.font.Font(ROOT_DIR + '/assets/fonts/timer.ttf', BANNER_FONT_SIZE)
        self.win_font_lg = pygame.font.Font(ROOT_DIR + '/assets/fonts/courier_new_bd.ttf', WIN_FONT_SIZE_LG)
        self.win_font_md = pygame.font.Font(ROOT_DIR + '/assets/fonts/helvetica.ttf', WIN_FONT_SIZE_MD)
        self.win_font_sm = pygame.font.Font(ROOT_DIR + '/assets/fonts/helvetica.ttf', WIN_FONT_SIZE_SM)

        pygame.mixer.init()
        self.explosion_sound = pygame.mixer.Sound(ROOT_DIR + '/assets/sounds/explosion.mp3')
        self.flag_sound = pygame.mixer.Sound(ROOT_DIR + '/assets/sounds/flag_place.mp3')
        self.click_sound = pygame.mixer.Sound(ROOT_DIR + '/assets/sounds/tile_click.mp3')
        self.victory_sound = pygame.mixer.Sound(ROOT_DIR + '/assets/sounds/victory.mp3')
    
    def load(self, difficulty: str):
        """
        Configures the Game based on the selected difficulty and initializes pygame elements.

        Params:
            str: The game difficulty ('beginner', 'intermediate', or 'expert').
        """
        self.quitting = False
        self.reopen_tkinter = False

        # configure difficulty specifications
        self.difficulty = 'beginner'
        if difficulty in DIFFICULTIES.keys():
            self.difficulty = difficulty
        difficulty_data = DIFFICULTIES[self.difficulty]
        self.num_mines = difficulty_data['num_mines']
        self.rows = difficulty_data['rows']
        self.cols = difficulty_data['cols']

        # initialize pygame window
        pygame.display.init()
        if self.cols >= DIFFICULTIES['intermediate']['cols']:
            self.screen_width = TILE_SIZE * (self.cols + 2*MARGIN)
        else:
            self.screen_width = TILE_SIZE * (DIFFICULTIES['intermediate']['cols'] + 2*MARGIN)
        self.screen_height = TILE_SIZE * (self.rows + 2*MARGIN) + 2*BANNER_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Minesweeper')
        pygame.display.set_icon(self.icon)

        # load tile textures from tile_atlas.png
        tile_surfaces = []
        for y in range(4):
            for x in range(4):
                image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                area = (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                image.blit(self.tile_map, (0, 0), area)
                tile_surfaces.append(image)
        
        # load tile sprites
        self.tiles = []
        self.field_top_left = ((self.screen_width - self.cols*TILE_SIZE)/2, (self.screen_height - self.rows*TILE_SIZE)/2)
        for x in range(self.cols):
            self.tiles.append([])
            for y in range(self.rows):
                new_tile = Tile(tile_surfaces, (x, y), self.field_top_left)
                self.tiles[x].append(new_tile)
        
        # load face button texture tuples (unclicked, clicked) from face_atlas.png
        face_surfaces = []
        hidden_area = ((TileStates.HIDDEN%4)*TILE_SIZE, int(TileStates.HIDDEN/4)*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        uncovered_area = ((TileStates.UNCOVERED%4)*TILE_SIZE, int(TileStates.UNCOVERED/4)*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        button_size = (3*TILE_SIZE, 3*TILE_SIZE)
        for x in range(4):
            # place each face texture on top of unclicked and clicked tile textures
            default_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            clicked_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            default_image.blit(self.tile_map, (0, 0), hidden_area)
            clicked_image.blit(self.tile_map, (0, 0), uncovered_area)
            default_image = pygame.transform.scale(default_image, button_size)
            clicked_image = pygame.transform.scale(clicked_image, button_size)
            area = (x*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE) # area on face_atlas.png to blit from
            face_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            face_image.blit(self.face_map, (0, 0), area)
            face_image = pygame.transform.scale(face_image, (2*TILE_SIZE, 2*TILE_SIZE))
            face_loc = ((default_image.get_width() - face_image.get_width())/2, (default_image.get_height() - face_image.get_height())/2)
            default_image.blit(face_image, face_loc)
            clicked_image.blit(face_image, face_loc)
            face_surfaces.append((default_image, clicked_image))

        # load top banner static elements
        banner_surface = pygame.Surface((self.screen_width, BANNER_HEIGHT))
        banner_surface.fill(BANNER_COLOR)
        banner_sprite = Sprite(banner_surface, (0, 0))
        flag_surface = pygame.transform.scale(self.flag_image, (2*TILE_SIZE, 2*TILE_SIZE))
        flag_x = MARGIN * TILE_SIZE
        flag_y = (BANNER_HEIGHT - flag_surface.get_height()) / 2
        flag_icon = Sprite(flag_surface, (flag_x, flag_y))
        button_x = (self.screen_width - button_size[0]) / 2
        button_y = (BANNER_HEIGHT - button_size[1]) / 2
        self.face_button = Button(face_surfaces, (button_x, button_y), self.restart)
        self.banner_sprites = [banner_sprite, flag_icon, self.face_button]

        # load footer
        footer_surface = Sprite(banner_surface, (0, self.screen_height - BANNER_HEIGHT))
        button_x = (self.screen_width - self.home_image.get_width()) / 2
        button_y = (self.screen_height - (BANNER_HEIGHT + self.home_image.get_height())/2)
        home_button = Button([(self.home_image, self.home_image_clicked)], (button_x, button_y), self.quit_to_menu)
        pad_x = self.home_image.get_width() * 2
        button_x = (self.screen_width - self.quit_image.get_width()) / 2 - pad_x
        button_y = (self.screen_height - (BANNER_HEIGHT + self.quit_image.get_height())/2)
        quit_button = Button([(self.quit_image, self.quit_image_clicked)], (button_x, button_y), self.quit)
        button_x = (self.screen_width - self.sound_image.get_width()) / 2 + pad_x
        button_y = (self.screen_height - (BANNER_HEIGHT + self.sound_image.get_height())/2)
        self.sound_button = Button([(self.mute_image, self.mute_image_clicked), (self.sound_image, self.sound_image_clicked)],
                                   (button_x, button_y), self.toggle_sound)
        self.sound_button.state = self.sound_enabled
        self.footer_sprites = [footer_surface, home_button, quit_button, self.sound_button]

        self.buttons = [self.face_button, quit_button, home_button, self.sound_button]

        # load win screen static elements
        win_top_left = ((self.screen_width - WIN_SCREEN_SIZE[0])/2, (self.screen_height - WIN_SCREEN_SIZE[1])/2)
        self.win_screen_rect = pygame.Rect(win_top_left[0], win_top_left[1], WIN_SCREEN_SIZE[0], WIN_SCREEN_SIZE[1])
        self.win_screen_bg = pygame.Surface(self.win_screen_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.win_screen_bg, WIN_SCREEN_COLOR, self.win_screen_bg.get_rect())
        text_surface = self.win_font_lg.render("You won!", False, WIN_FONT_COLOR)
        win_message_pos = (win_top_left[0] + (WIN_SCREEN_SIZE[0] - text_surface.get_width())/2, win_top_left[1] + WIN_PAD_Y)
        win_message = Sprite(text_surface, win_message_pos)
        self.win_screen_sprites = [win_message]

    def restart(self):
        """
        Resets the game state to a new game of the same difficulty.
        """
        self.game_over = False
        self.visited = [[False]*self.rows for y in range(self.cols)]
        self.mines = []
        self.flags = []
        self.uncovered_tiles: int = 0
        self.time: float = 0.0

        for x in range(self.cols):
            for y in range(self.rows):
                self.tiles[x][y].update_state(TileStates.HIDDEN)
                self.tiles[x][y].is_mine = False

    def start(self, difficulty: str = 'beginner', name: str = '') -> bool:
        """
        Loads Game elements and executes the main loop that handles all events.

        Params:
            str: The game difficulty ('beginner', 'intermediate', or 'expert').
            str: The player name to be used in high scores.
        
        Returns:
            bool: True iff the tkinter startup menu should be reopened upon quitting.
        """
        self.player_name = name
        self.load(difficulty)
        self.restart()

        # game loop
        clock = pygame.time.Clock()
        while not self.quitting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_over = True
                    self.quitting = True
                    pygame.quit()
                    self.save_settings()
                    break
                elif event.type == MOUSEBUTTONUP:
                    for button in self.buttons:
                        if button.check_click(event.pos, event.button):
                            break
                    if not self.game_over:
                        self.check_tile_click(event)
            
            if not self.quitting:
                self.sound_button.state = self.sound_enabled
                for button in self.buttons:
                    button.check_mouse_press(pygame.mouse.get_pos())

                if not self.game_over:
                    self.check_tile_press()
                    self.update_face_button()

                    if len(self.mines) > 0:
                        self.time += 1.0 / FRAMERATE
            
                self.render()
                clock.tick(FRAMERATE)
        
        pygame.display.quit()
        return self.reopen_tkinter

    def render(self):
        """
        Updates dynamic visual elements and displays all Sprites.
        """
        tile_group = pygame.sprite.Group()
        for x in range(self.cols):
            for y in range(self.rows):
                tile_group.add(self.tiles[x][y])

        # load dynamic banner elements
        flags_remaining = self.num_mines - len(self.flags)
        text = str(abs(flags_remaining))
        if flags_remaining >= 0:
            text = text.rjust(3, '0')
        else:
            text = '-' + text.rjust(2, '0')
        text_surface = self.banner_font.render(text, False, BANNER_FONT_COLOR, BANNER_FONT_BG)
        flag_counter = Sprite(text_surface,
                              (MARGIN*TILE_SIZE + 2*self.flag_image.get_width(), (BANNER_HEIGHT - BANNER_FONT_SIZE)/2))
        # timer
        timer_text = time_to_str(self.time)
        text_surface = self.banner_font.render(timer_text, False, BANNER_FONT_COLOR, BANNER_FONT_BG)
        timer = Sprite(text_surface,
                        (self.screen_width - MARGIN*TILE_SIZE - text_surface.get_width(), (BANNER_HEIGHT - BANNER_FONT_SIZE)/2))
        banner_group = pygame.sprite.Group()
        for element in self.banner_sprites:
            banner_group.add(element)
        banner_group.add(flag_counter, timer)

        footer_group = pygame.sprite.Group()
        for element in self.footer_sprites:
            footer_group.add(element)

        # display game elements
        self.screen.fill(BG_COLOR)
        tile_group.draw(self.screen)
        banner_group.draw(self.screen)
        footer_group.draw(self.screen)
        if self.game_over and self.face_button.state == FaceExpressions.WIN:
            self.screen.blit(self.win_screen_bg, self.win_screen_rect)
            win_screen_group = pygame.sprite.Group()
            for element in self.win_screen_sprites:
                win_screen_group.add(element)

            # load dynamic win screen elements
            text_surface = self.win_font_md.render(timer_text, False, WIN_FONT_COLOR)
            pos_x = self.win_screen_rect.x + (WIN_SCREEN_SIZE[0] - text_surface.get_width())/2
            pos_y = self.win_screen_sprites[0].rect.y + self.win_screen_sprites[0].rect.height
            time_display = Sprite(text_surface, (pos_x, pos_y))
            text = f'%s High Scores' % self.difficulty.capitalize()
            text_surface = self.win_font_sm.render(text, False, WIN_FONT_COLOR)
            pos_x = self.win_screen_rect.x + (WIN_SCREEN_SIZE[0] - text_surface.get_width())/2
            pos_y += time_display.rect.height + WIN_PAD_Y
            high_score_title = Sprite(text_surface, (pos_x, pos_y))

            # display high scores
            pos_y += high_score_title.rect.height + WIN_PAD_Y
            all_scores = self.file_io.get_all_scores()
            if self.difficulty in all_scores.keys():
                scores = all_scores[self.difficulty]
                to_display = NUM_HIGH_SCORES if NUM_HIGH_SCORES <= len(scores) else len(scores)
                for i in range(to_display):
                    score = scores[i]
                    name_text = score[0].ljust(MAX_NAME_LENGTH)
                    time_text = time_to_str(score[1])
                    font_color = HIGH_SCORE_FONT_COLOR if self.player_rank == i else WIN_FONT_COLOR
                    # rank and name (left justified)
                    left_text = f'%s. %s' % (i + 1, name_text)
                    left_text_surface = self.win_font_sm.render(left_text, False, font_color)
                    pos_x_left = self.win_screen_rect.x + TILE_SIZE
                    left_text_sprite = Sprite(left_text_surface, (pos_x_left, pos_y))
                    # time (right justified)
                    right_text_surface = self.win_font_sm.render(time_text, False, font_color)
                    pos_x_right = self.win_screen_rect.x + self.win_screen_rect.width - TILE_SIZE - right_text_surface.get_width()
                    right_text_sprite = Sprite(right_text_surface, (pos_x_right, pos_y))
                    win_screen_group.add(left_text_sprite, right_text_sprite)
                    pos_y += left_text_sprite.rect.height

            win_screen_group.add(time_display, high_score_title)
            win_screen_group.draw(self.screen)
        
        pygame.display.flip()

    def check_tile_click(self, event: pygame.event.Event):
        """
        Attempts to find a Tile at the click location, executing the corresponding function if a Tile was clicked.

        Params:
            Event: A pygame mouse click event (MOUSEBUTTONUP).
        """
        tile_x = (event.pos[0] - self.field_top_left[0]) / TILE_SIZE
        tile_y = (event.pos[1] - self.field_top_left[1]) / TILE_SIZE
        if tile_x >= 0 and tile_x < self.cols and tile_y >= 0 and tile_y < self.rows:
            x = int(tile_x)
            y = int(tile_y)
            tile = self.tiles[x][y]
            if tile.check_click(event.pos, event.button):
                if event.button == BUTTON_LEFT:
                    self.tile_left_click((x, y))
                elif event.button == BUTTON_RIGHT:
                    self.tile_right_click((x, y))
                return
    
    def tile_left_click(self, pos: tuple[int, int]):
        """
        Tile left click mechanics, including chording if the right mouse button is also pressed.

        Params:
            tuple[int, int]: The Tile position within the 2D array.
        """
        tile = self.tiles[pos[0]][pos[1]]
        pressed = pygame.mouse.get_pressed()
        # right mouse button also pressed
        if pressed[2]:
            if tile.state != TileStates.HIDDEN and tile.state != TileStates.FLAG:
                self.chord(pos, tile.state)
        elif tile.state == TileStates.HIDDEN:
            if tile.is_mine:
                tile.update_state(TileStates.MINE_HIT)
                self.loss()
            else:
                if self.sound_enabled:
                    self.click_sound.play()
                self.uncover(pos)
    
    def tile_right_click(self, pos: tuple[int, int]):
        """
        Toggles whether the Tile is flagged, or chords if left mouse button is also pressed.

        Params:
            tuple[int, int]: The Tile position within the 2D array.
        """
        tile = self.tiles[pos[0]][pos[1]]
        pressed = pygame.mouse.get_pressed()
        # left mouse button also pressed
        if pressed[0]:
            if tile.state != TileStates.HIDDEN and tile.state != TileStates.FLAG:
                self.chord(pos, tile.state)
        elif tile.state == TileStates.HIDDEN:
            tile.update_state(TileStates.FLAG)
            self.flags.append(pos)
            if self.sound_enabled:
                self.flag_sound.play()
        elif tile.state == TileStates.FLAG:
            tile.update_state(TileStates.HIDDEN)
            self.flags.remove(pos)

    def check_tile_press(self):
        """
        Checks whether each Tile Sprite is currently being clicked and executes subsequent functions.
        """
        pressed = pygame.mouse.get_pressed()
        for x in range(self.cols):
            for y in range(self.rows):
                tile = self.tiles[x][y]
                if tile not in self.to_chord:
                    if tile.check_mouse_press(pygame.mouse.get_pos()):
                        # right mouse button also pressed
                        if pressed[2]:
                            self.press_chord((x, y), tile.state)
        self.to_chord = []

    def get_chord_info(self, pos: tuple[int, int], num_flags: int) -> tuple[bool, list[Tile]]:
        """
        Checks if a tile can be chorded and gets the list of tiles that would be uncovered with a chord
            (left and right click simultaneously).

        Params:
            tuple[int, int]: The Tile position within the 2D array.
            int: The number of flags that must be adjacent to the Tile in order to chord.
        
        Returns:
            tuple[bool, list[Tile]]: A boolean representing whether the Tile can currently be chorded
                and the list of tiles that would be uncovered if the chord is valid.
        """
        flag_count = 0
        neighbors = []
        x_min = pos[0] - 1 if pos[0] - 1 >= 0 else 0
        y_min = pos[1] - 1 if pos[1] - 1 >= 0 else 0
        x_max = pos[0] + 1 if pos[0] + 1 < self.cols else self.cols - 1
        y_max = pos[1] + 1 if pos[1] + 1 < self.rows else self.rows - 1
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                if (x, y) != (pos[0], pos[1]):
                    neighbor = self.tiles[x][y]
                    if neighbor.state == TileStates.FLAG:
                        flag_count += 1
                    elif neighbor.state == TileStates.HIDDEN:
                        neighbors.append(neighbor)

        return (flag_count == num_flags, neighbors)

    def chord(self, pos: tuple[int, int], num_flags: int):
        """
        If the correct number of adjacent Tiles has been flagged, uncovers all adjacent hidden Tiles.

        Params:
            tuple[int, int]: The position within the 2D array of the center Tile.
            int: The number of flags that must be adjacent to the center Tile in order to chord.
        """
        chord_info = self.get_chord_info(pos, num_flags)
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
            if len(self.to_chord) > 0 and self.sound_enabled:
                self.click_sound.play()

    def press_chord(self, pos: tuple[int, int], num_flags: int):
        """
        Displays the pressed texture for all tiles that may be chorded.
        """
        self.to_chord = self.get_chord_info(pos, num_flags)[1]
        for tile in self.to_chord:
            if tile.state == TileStates.HIDDEN:
                tile.image = tile.surfaces[TileStates.UNCOVERED]

    def plant_mines(self, pos: tuple[int, int]):
        """
        Randomly populates the field with mines, excluding the first Tile clicked.

        Params:
            tuple[int, int]: The position within the 2D array of the clicked Tile.
        """
        open_tiles = []
        for x in range(self.cols):
            for y in range(self.rows):
                if (x, y) != pos:
                    open_tiles.append((x, y))
        for i in range(self.num_mines):
            rand_index = random.randint(0, len(open_tiles) - 1)
            tile_pos = open_tiles[rand_index]
            self.tiles[tile_pos[0]][tile_pos[1]].is_mine = True
            self.mines.append((tile_pos[0], tile_pos[1]))
            del open_tiles[rand_index]

    def uncover(self, pos: tuple[int, int]):
        """
        Uncovers the Tile and its surroundings at a given position.

        Params:
            tuple[int, int]: The Tile position within the 2D array.
        """
        if len(self.mines) == 0:
            self.plant_mines(pos)

        # perform breadth first search starting at the clicked tile
        bfs_queue = [pos]
        self.visited[pos[0]][pos[1]] = True
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

    def update_face_button(self):
        """
        Changes facial expression to shocked iff a Tile is being clicked.
        """
        pressed = pygame.mouse.get_pressed()
        # left mouse button
        if pressed[0]:
            click_loc = pygame.mouse.get_pos()
            bottom_right = (self.field_top_left[0] + TILE_SIZE*self.cols,
                            self.field_top_left[1] + TILE_SIZE*self.rows)
            if click_loc[0] >= self.field_top_left[0] and click_loc[1] >= self.field_top_left[1] \
                and click_loc[0] <= bottom_right[0] and click_loc[1] <= bottom_right[1]:
                self.face_button.state = FaceExpressions.SHOCKED
            else:
                self.face_button.state = FaceExpressions.HAPPY
        else:
            self.face_button.state = FaceExpressions.HAPPY

    def win(self):
        """
        Ends the game, saves the time to ../data/highscores.txt, and updates the face Button to signify a win.
        """
        self.game_over = True
        self.face_button.state = FaceExpressions.WIN
        if self.sound_enabled:
            self.victory_sound.play()
        self.player_rank = self.file_io.add_score(self.time, self.difficulty, self.player_name)

    def loss(self):
        """
        Ends the game, reveals mistakes and remaining mines, and updates the face Button to signify a loss.
        """
        self.game_over = True
        self.face_button.state = FaceExpressions.LOSE
        if self.sound_enabled:
            self.explosion_sound.play()
        for pos in self.mines:
            self.tiles[pos[0]][pos[1]].reveal()
        for pos in self.flags:
            self.tiles[pos[0]][pos[1]].reveal()
        for x in range(self.cols):
            for y in range(self.rows):
                self.tiles[x][y].mouse_unpress()

    def quit(self):
        """
        Signifies that the program should exit without reopening the tkinter startup menu.
        """
        self.quitting = True
        self.save_settings()
    
    def quit_to_menu(self):
        """
        Signifies that the pygame display should quit and the tkinter startup menu be reopened.
        """
        self.quitting = True
        self.reopen_tkinter = True
        self.save_settings()
    
    def toggle_sound(self):
        """
        Enables/disables sound.
        """
        self.sound_enabled = not self.sound_enabled
    
    def save_settings(self):
        """
        Uses the Data class to write settings data to ../data/settings.txt.
        """
        data = {
            'sound_enabled': self.sound_enabled
        }
        self.file_io.write_settings(data)
