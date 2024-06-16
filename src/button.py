from pygame import Surface

from sprite import Sprite


class Button(Sprite):
    """
    A general class for buttons, Sprites that provide a function to execute upon left click.
    """

    def __init__(self, surface_pairs: list[tuple[Surface, Surface]], position: tuple[int, int], left_click):
        """
        Initializes a Button object.

        Params:
            list[tuple[Surface, Surface]]: A list of (clicked, unclicked) surface pairs that the Button will use.
            tuple[int, int]: The position relative to the window at which to draw the Button (from top left).
            Any: The function to execute upon left click.
        """  
        self.surface_pairs = surface_pairs
        self.position: tuple[int, int] = position
        self.left_click = left_click
        self.is_clicked: bool = False
        self.state: int = 0

        super().__init__(self.surface_pairs[self.state][self.is_clicked], position,
                         left_click, right_click=None, mouse_press=self.mouse_press, mouse_unpress=self.mouse_unpress)

    def mouse_press(self, buttons: tuple[bool, bool, bool]):
        """
        Displays clicked surface in current state.
        """
        if buttons[0]:
            self.is_clicked = True
            self.image = self.surface_pairs[self.state][self.is_clicked]
    
    def mouse_unpress(self):
        """
        Reverts to default, unclicked surface in current state.
        """
        self.is_clicked = False
        self.image = self.surface_pairs[self.state][self.is_clicked]
        