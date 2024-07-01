import tkinter as tk
import tkinter.font as tkFont

from const import MAX_NAME_LENGTH, NUM_HIGH_SCORES, ROOT_DIR
from data import Data
from game import Game
from utils import time_to_str


TK_WIDTH = 400
TK_HEIGHT = 400
SCORE_TEXT_WIDTH = 12 + MAX_NAME_LENGTH

file_io = Data()
game = Game(file_io)


class Menu(tk.Frame):
    """
    Wrapper class for tkinter startup menu GUI.
    """

    def __init__(self, parent: tk.Frame, *args, **kwargs):
        """
        Setup and display tkinter window.

        Params:
            parent: The top level widget representing the mainw window.
        """
        self.root: tk.Tk = parent
        self.root.title('Minesweeper')
        icon_image = tk.PhotoImage(ROOT_DIR + '/assets/textures/mine.ico')
        self.root.iconbitmap(False, icon_image)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width / 2 - TK_WIDTH / 2
        y = screen_height / 2 - TK_HEIGHT / 2
        self.root.geometry('%dx%d+%d+%d' % (TK_WIDTH, TK_HEIGHT, x, y))
        self.root.resizable(False, False)

        # initialize tkinter styles
        title_font = tkFont.Font(family='Courier New', size=20, weight=tkFont.BOLD)
        subtitle_font = tkFont.Font(family='Helvetica', size=12, weight=tkFont.BOLD)
        body_font = tkFont.Font(family='Helvetica', size=10, weight=tkFont.NORMAL)
        scores_font = tkFont.Font(font='TkFixedFont', size=10, weight=tkFont.NORMAL)
        padding = 10

        # menu elements
        tk.Label(self.root, text='Minesweeper', font=title_font).pack(pady=padding)
        
        difficulty_frame = tk.Frame(self.root)
        difficulty_frame.pack(pady=padding)
        choice_frame = tk.Frame(difficulty_frame)
        choice_frame.grid(row=0, column=0, padx=padding)
        tk.Label(choice_frame, text='Select Difficulty', font=subtitle_font).pack()
        self.difficulty: tk.StringVar = tk.StringVar(difficulty_frame, value='beginner')
        tk.Radiobutton(choice_frame, text='Beginner', font=body_font, variable=self.difficulty, value='beginner',
                       command=lambda: self.update_high_scores('beginner')).pack(anchor=tk.W)
        tk.Radiobutton(choice_frame, text='Intermediate', font=body_font, variable=self.difficulty, value='intermediate',
                       command=lambda: self.update_high_scores('intermediate')).pack(anchor=tk.W)
        tk.Radiobutton(choice_frame, text='Expert', font=body_font, variable=self.difficulty, value='expert',
                       command=lambda: self.update_high_scores('expert')).pack(anchor=tk.W)
        score_label_frame = tk.LabelFrame(difficulty_frame, font=scores_font)
        score_label_frame.grid(row=0, column=1, padx=padding)
        self.score_label: tk.Label = tk.Label(score_label_frame, text=self.get_high_scores_text(self.difficulty.get()), font=scores_font,
                                              width=SCORE_TEXT_WIDTH, height=NUM_HIGH_SCORES, anchor=tk.W)
        self.score_label.pack()

        name_frame = tk.Frame(self.root)
        name_frame.pack(pady=padding)
        tk.Label(name_frame, text='Name', font=subtitle_font).pack()
        player_name = tk.StringVar()
        reg = self.root.register(self.validate_name) 
        tk.Entry(name_frame, textvariable=player_name, font=body_font, width=12, validate="key", validatecommand=(reg, '%P')).pack()
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(side='bottom', pady=padding*2)
        tk.Button(button_frame, text='Start', font=subtitle_font, width=15, height=2, bg='lime',
                command=lambda: self.start_game(self.root, {'difficulty': self.difficulty.get(), 'name': player_name.get()})).pack()
        tk.Button(button_frame, text='Quit', font=subtitle_font, width=8, height=1, bg='red',
                command=self.root.quit).pack(pady=padding)

        self.root.mainloop()

    def validate_name(self, input: str) -> bool:
        """
        Validates the name Entry field to ensure it does not exceed maximum length.

        Params:
            str: Input text of tkinter Entry.
        
        Returns:
            bool: True iff the input does not exceed MAX_NAME_LENGTH characters.
        """
        return len(input) <= MAX_NAME_LENGTH

    def start_game(self, root: tk.Tk, game_info: tuple[str, str]):
        """
        Starts the game with information entered via the tkinter window.

        Params:
            tk.Tk: The top level widget representing the main window.
            tuple[str, str]: A tuple containing the game difficulty and player's entered name.
        """
        self.root.withdraw() # temporarily close the tkinter window
        difficulty = game_info['difficulty']
        player_name = game_info['name']
        if game.start(difficulty, player_name):
            self.update_high_scores(self.difficulty.get())
            root.deiconify() # reopen the tkinter window
        else:
            root.destroy() # quit tkinter
    
    def update_high_scores(self, difficulty: str):
        """
        Updates the high scores Label to show the high scores of the selected difficulty.

        Params:
            str: The difficulty selected.
        """
        self.score_label['text'] = self.get_high_scores_text(difficulty)
    
    def get_high_scores_text(self, difficulty: str):
        """
        Gets high scores of the current difficulty and returns formatted text.

        Params:
            str: The difficulty selected.
        
        Returns:
            str: Formatted text of the high scores.
        """
        high_scores = file_io.get_all_scores()
        text = ''
        if difficulty in high_scores.keys():
            scores = high_scores[difficulty]
            for i in range(NUM_HIGH_SCORES):
                position = i + 1
                position_text = f'%s. ' % position
                score_pair = scores[i] if i < len(scores) else ('', None)
                time_text = time_to_str(score_pair[1])
                name_text = score_pair[0].ljust(SCORE_TEXT_WIDTH - (len(position_text) + len(time_text)))
                text += position_text + name_text + time_text
                if position < NUM_HIGH_SCORES:
                    text += '\n'
            return text
        else:
            for i in range(NUM_HIGH_SCORES):
                position = i + 1
                text += f'%s.' % position
                if position < NUM_HIGH_SCORES:
                    text += '\n'
            return text


if __name__ == '__main__':
    root = tk.Tk()
    menu = Menu(root)
