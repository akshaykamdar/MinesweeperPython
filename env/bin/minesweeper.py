import tkinter as tk
from tkinter import messagebox
from gameboard import GameBoard

class MinesweeperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Minesweeper")

        self.gameboard = GameBoard()
        self.buttons = {}

        self.create_widgets()
        self.create_board()

        self.seconds = 0
        self.running = False

    def create_widgets(self):
        self.frame = tk.Frame(self.master, bg="#c0c0c0", bd=5, relief=tk.RIDGE)
        self.frame.pack(padx=10, pady=10)

        self.timer_label = tk.Label(self.master, text="Time: 0", font=("Verdana", 12, "bold"), bg="#ececec")
        self.timer_label.pack(side=tk.TOP, pady=5)

        self.reset_button = tk.Button(self.master, text="Reset", font=("Verdana", 12), bg="#4CAF50", fg="white",
                                      activebackground="#45a049", command=self.reset_game)
        self.reset_button.pack(side=tk.TOP, pady=5, fill=tk.X, padx=20)

        for r in range(self.gameboard.rows):
            for c in range(self.gameboard.cols):
                btn = tk.Button(self.frame, width=3, height=1, font=("Verdana", 16, "bold"),
                                relief=tk.RAISED, bg="#dcdcdc", fg="black")
                btn.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
                btn.bind("<Button-1>", lambda e, row=r, col=c: self.left_click(row, col))
                btn.bind("<Button-3>", lambda e, row=r, col=c: self.right_click(row, col))
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e0e0e0"))
                btn.bind("<Leave>", lambda e, b=btn: self.reset_btn_color(b))
                self.buttons[(r, c)] = btn

        for i in range(self.gameboard.rows):
            self.frame.grid_rowconfigure(i, weight=1)
        for j in range(self.gameboard.cols):
            self.frame.grid_columnconfigure(j, weight=1)

    def reset_btn_color(self, button):
        pos = None
        for key, b in self.buttons.items():
            if b == button:
                pos = key
                break
        if pos:
            if pos in self.gameboard.revealed:
                button.config(bg="#bbbbbb")
            else:
                button.config(bg="#dcdcdc")

    def create_board(self):
        self.gameboard.reset()
        self.seconds = 0
        self.running = False
        self.update_timer_label()

        for pos, button in self.buttons.items():
            button.config(text="", relief=tk.RAISED, state=tk.NORMAL, bg="#dcdcdc", fg="black")
            button.unbind("<Enter>")
            button.unbind("<Leave>")
            button.bind("<Enter>", lambda e, b=button: b.config(bg="#e0e0e0"))
            button.bind("<Leave>", lambda e, b=button: self.reset_btn_color(b))

    def left_click(self, row, col):
        if self.gameboard.game_over or (row, col) in self.gameboard.flags:
            return

        if self.gameboard.first_click:
            self.running = True
            self.run_timer()

        self.gameboard.reveal_cell(row, col)
        self.update_cells()

        if self.gameboard.game_over:
            self.reveal_mines()
            messagebox.showinfo("Game Over", "You clicked on a mine! Game Over!")
            self.running = False
        elif self.gameboard.check_win():
            messagebox.showinfo("Congratulations", "You have cleared the minefield!")
            self.running = False

    def right_click(self, row, col):
        if self.gameboard.game_over or (row, col) in self.gameboard.revealed:
            return

        self.gameboard.toggle_flag(row, col)
        self.update_cells()

    def update_cells(self):
        for (r, c), btn in self.buttons.items():
            if (r, c) in self.gameboard.revealed:
                btn.config(relief=tk.SUNKEN, state=tk.DISABLED, bg="#bbbbbb")
                count = self.gameboard.count_adjacent_mines(r, c)
                if count > 0:
                    btn.config(text=str(count), fg=self.get_color(count))
                else:
                    btn.config(text="")
            else:
                if (r, c) in self.gameboard.flags:
                    btn.config(text="⚑", fg="#d93131", bg="#dcdcdc", relief=tk.RAISED, state=tk.NORMAL)
                else:
                    btn.config(text="", bg="#dcdcdc", relief=tk.RAISED, state=tk.NORMAL)

    def reveal_mines(self):
        for mine in self.gameboard.mines:
            btn = self.buttons[mine]
            btn.config(text="*", bg="#ff4c4c", fg="black", relief=tk.SUNKEN, state=tk.DISABLED)

    def get_color(self, count):
        colors = {
            1: '#0000FF',
            2: '#008000',
            3: '#FF0000',
            4: '#000080',
            5: '#800000',
            6: '#008080',
            7: '#000000',
            8: '#808080',
        }
        return colors.get(count, '#000000')

    def update_timer_label(self):
        self.timer_label.config(text=f"Time: {self.seconds}")

    def run_timer(self):
        if self.running:
            self.seconds += 1
            self.update_timer_label()
            self.master.after(1000, self.run_timer)

    def reset_game(self):
        self.running = False
        self.seconds = 0
        self.create_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperGUI(root)
    root.mainloop()
