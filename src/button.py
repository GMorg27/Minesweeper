from sprite import Sprite


# a general class for all buttons, sprites that can be left-clicked
class Button(Sprite):
    def __init__(self, surface_pairs, position: tuple[int, int], left_click):
        self.surface_pairs = surface_pairs
        self.position: tuple[int, int] = position
        self.left_click = left_click
        self.is_clicked: bool = False
        self.state: int = 0

        super().__init__(self.surface_pairs[self.state][self.is_clicked], position,
                         left_click, right_click=None, mouse_press=self.mouse_press, mouse_unpress=self.mouse_unpress)

    # display clicked surface
    def mouse_press(self, buttons: tuple[bool, bool, bool]):
        if buttons[0]:
            self.is_clicked = True
            self.image = self.surface_pairs[self.state][self.is_clicked]
    
    # revert to default surface
    def mouse_unpress(self):
        self.is_clicked = False
        self.image = self.surface_pairs[self.state][self.is_clicked]