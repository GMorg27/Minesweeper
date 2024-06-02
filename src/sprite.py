import pygame
from pygame.locals import *


# wrapper class for pygame sprite
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, position: tuple[int, int], left_click=None, right_click=None, mouse_press=None, mouse_unpress=None):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.left_click = left_click
        self.right_click = right_click
        self.mouse_press = mouse_press
        self.mouse_unpress = mouse_unpress

    # check if sprite was clicked and execute corresponding function if so
    def check_click(self, pos: tuple[int, int], button: int):
        if button == BUTTON_LEFT:
            if self.left_click is not None and self.rect.collidepoint(pos):
                self.left_click()
        elif button == BUTTON_RIGHT:
            if self.right_click is not None and self.rect.collidepoint(pos):
                self.right_click()

    # check if sprite is currently being left clicked and execute corresponding function
    def check_mouse_press(self, pos: tuple[int, int]):
        if self.mouse_press is not None:
            buttons = pygame.mouse.get_pressed()
            if self.rect.collidepoint(pos) and buttons[0]:
                self.mouse_press()
            elif self.mouse_unpress is not None:
                self.mouse_unpress()
