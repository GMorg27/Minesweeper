import pygame
from pygame.locals import *


class Sprite(pygame.sprite.Sprite):
    """
    Wrapper class for pygame Sprite.
    """

    def __init__(self, image: pygame.Surface, position: tuple[int, int], left_click=None, right_click=None, mouse_press=None, mouse_unpress=None):
        """
        Initializes a Sprite object.

        Params:
            pygame.Surface: The pygame Surface to display on the Sprite.
            tuple[int, int]: The position relative to the window at which to draw the Sprite (from top left).
            Any | None: The function to execute upon left click.
            Any | None: The function to execute upon right click.
            Any | None: The function to execute when the Sprite is being clicked.
            Any | None: The function to execute when the Sprite is not being clicked.
        """
        super().__init__()
        self.image: pygame.Surface = image
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.left_click = left_click
        self.right_click = right_click
        self.mouse_press = mouse_press
        self.mouse_unpress = mouse_unpress

    def check_click(self, pos: tuple[int, int], button: int):
        """
        Check if Sprite was clicked, and execute corresponding function if so.

        Params:
            tuple[int, int]: The current mouse position relative to the window.
            int: The mouse button that was clicked.
        """
        if self.mouse_unpress:
            self.mouse_unpress()
            
        buttons = pygame.mouse.get_pressed()
        if button == BUTTON_LEFT:
            if self.left_click is not None and self.rect.collidepoint(pos):
                self.left_click(buttons)
        elif button == BUTTON_RIGHT:
            if self.right_click is not None and self.rect.collidepoint(pos):
                self.right_click(buttons)

    def check_mouse_press(self, pos: tuple[int, int]):
        """
        Check whether the Sprite is currently being clicked, and execute the corresponding function.

        Params:
            tuple[int, int]: The current mouse position relative to the window.
        """
        if self.mouse_press is not None:
            buttons = pygame.mouse.get_pressed()
            if self.rect.collidepoint(pos) and any(buttons):
                self.mouse_press(buttons)
            elif self.mouse_unpress is not None:
                self.mouse_unpress()
