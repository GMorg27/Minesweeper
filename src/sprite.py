from pygame import Rect, Surface, mouse, sprite
from pygame.locals import *


class Sprite(sprite.Sprite):
    """
    Wrapper class for pygame Sprite.
    """

    def __init__(self, image: Surface, position: tuple[int, int], left_click=None, right_click=None, mouse_press=None, mouse_unpress=None):
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
        self.image: Surface = image
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.left_click = left_click
        self.right_click = right_click
        self.mouse_press = mouse_press
        self.mouse_unpress = mouse_unpress

    def check_click(self, pos: tuple[int, int], button: int) -> bool:
        """
        Check if Sprite was clicked, and execute corresponding function if so.

        Params:
            tuple[int, int]: The current mouse position relative to the window.
            int: The mouse button that was clicked.
        
        Returns:
            bool: True iff the Sprite was clicked.
        """
        if self.mouse_unpress:
            self.mouse_unpress()
        
        if self.rect.collidepoint(pos):
            if button == BUTTON_LEFT and self.left_click is not None:
                self.left_click()
            elif button == BUTTON_RIGHT and self.right_click is not None:
                self.right_click()
            return True
        
        return False

    def check_mouse_press(self, pos: tuple[int, int]) -> bool:
        """
        Check whether the Sprite is currently being clicked, and execute the corresponding function.

        Params:
            tuple[int, int]: The current mouse position relative to the window.
        
        Returns:
            bool: True iff the Sprite is currently being clicked.
        """
        buttons = mouse.get_pressed()
        if self.rect.collidepoint(pos) and buttons[0]:
            if self.mouse_press is not None:
                self.mouse_press(buttons)
            return True
        elif self.mouse_unpress is not None:
            self.mouse_unpress()
        
        return False     
