import tkinter as tk
import tkinter.font as tkFont

from const import ROOT_DIR
from game import Game


TK_WIDTH = 400
TK_HEIGHT = 400


def startup_menu():
    """
    Sets up and displays the startup menu using tkinter.
    """
    # setup tkinter window
    menu_root = tk.Tk()
    menu_root.title('Minesweeper')
    icon_image = tk.PhotoImage(ROOT_DIR + '/assets/textures/mine.ico')
    menu_root.iconbitmap(False, icon_image)
    screen_width = menu_root.winfo_screenwidth()
    screen_height = menu_root.winfo_screenheight()
    x = screen_width / 2 - TK_WIDTH / 2
    y = screen_height / 2 -TK_HEIGHT / 2
    menu_root.geometry('%dx%d+%d+%d' % (TK_WIDTH, TK_HEIGHT, x, y))
    menu_root.resizable(False, False)

    # initialize tkinter styles
    title_font = tkFont.Font(family='Courier New', size=20, weight=tkFont.BOLD)
    subtitle_font = tkFont.Font(family='Helvetica', size=12, weight=tkFont.BOLD)
    body_font = tkFont.Font(family='Helvetica', size=10, weight=tkFont.NORMAL)
    padding = 10

    # menu elements
    tk.Label(menu_root, text='Minesweeper', font=title_font).pack(pady=padding)
    
    difficulty_frame = tk.Frame(menu_root)
    difficulty_frame.pack(pady=padding)
    tk.Label(difficulty_frame, text='Select Difficulty', font=subtitle_font).pack()
    difficulty = tk.StringVar(difficulty_frame, value='beginner')
    tk.Radiobutton(difficulty_frame, text='Beginner', font=body_font, variable=difficulty, value='beginner').pack(anchor=tk.W)
    tk.Radiobutton(difficulty_frame, text='Intermediate', font=body_font, variable=difficulty, value='intermediate').pack(anchor=tk.W)
    tk.Radiobutton(difficulty_frame, text='Expert', font=body_font, variable=difficulty, value='expert').pack(anchor=tk.W)

    name_frame = tk.Frame(menu_root)
    name_frame.pack(pady=padding)
    tk.Label(name_frame, text='Name', font=subtitle_font).pack()
    player_name = tk.StringVar()
    tk.Entry(name_frame, textvariable=player_name, font=body_font, width=15).pack()
    
    button_frame = tk.Frame(menu_root)
    button_frame.pack(side='bottom', pady=padding*2)
    tk.Button(button_frame, text='Start', font=subtitle_font, width=15, height=2, bg='lime',
              command=lambda: start_game(menu_root, {'difficulty': difficulty.get(), 'name': player_name.get()})).pack()
    tk.Button(button_frame, text='Quit', font=subtitle_font, width=8, height=1, bg='red',
              command=menu_root.quit).pack(pady=padding)

    menu_root.mainloop()


def start_game(root: tk.Tk, game_info: tuple[str, str]):
    """
    Starts the game with information entered via the tkinter window.

    Params:
        tk.Tk: The top level widget representing the main window.
        tuple[str, str]: A tuple containing the game difficulty and player's entered name.
    """
    root.destroy()
    difficulty = game_info['difficulty']
    player_name = game_info['name']
    game = Game(difficulty)
    # start game and reopen startup menu again if user chooses to return
    if game.start():
        del root, game_info, difficulty, player_name, game
        startup_menu()


if __name__ == '__main__':
    startup_menu()
