import pygame
from pygame.locals import *


# wrapper class for pygame sprite
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, position, left_click, right_click):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.left_click = left_click
        self.right_click = right_click

    # check if sprite is clicked and execute corresponding function if so
    def check_click(self, pos, button):
        # mouse left click
        if button == BUTTON_LEFT:
            if self.left_click is not None and self.rect.collidepoint(pos):
                self.left_click()
        # mouse right click
        elif button == BUTTON_RIGHT:
            if self.right_click is not None and self.rect.collidepoint(pos):
                self.right_click()
