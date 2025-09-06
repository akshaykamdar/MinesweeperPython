import tkinter as tk
from tkinter import messagebox
import random

class Minesweeper:
    def __init__(self, master):
        self.master = master
        self.master.title("Minesweeper")

        self.rows = 9
        self.cols = 9
        self.num_mines = 10

        self.buttons = {}
        self.mines = set()
        self.flags = set()
        self.revealed = set()
        self.first_click = True
        self.game_over = False

        self.create_widgets()
        self.create_board()

    def create_widgets(self):
        self.frame = tk.Frame(self.master, bg="#c0c0c0", bd=5, relief=tk.RIDGE)
        self.frame.pack(padx=10, pady=10)

        self.timer_label = tk.Label(self.master, text="Time: 0", font=("Verdana", 12, "bold"), bg="#ececec")
        self.timer_label.pack(side=tk.TOP, pady=5)

        self.reset_button = tk.Button(self.master, text="Reset", font=("Verdana", 12), bg="#4CAF50", fg="white",
                                      activebackground="#45a049", command=self.reset_game)
        self.reset_button.pack(side=tk.TOP, pady=5, fill=tk.X, padx=20)

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.frame, width=3, height=1, font=("Verdana", 16, "bold"),
                                relief=tk.RAISED, bg="#dcdcdc", fg="black")
                btn.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")

                # Use bind for ButtonPress and ButtonRelease for better click detection
                btn.bind("<ButtonPress-1>", lambda e, row=r, col=c: self.on_left_press(row, col))
                btn.bind("<ButtonRelease-1>", lambda e, row=r, col=c: self.on_left_release(row, col))
                btn.bind("<ButtonPress-3>", lambda e, row=r, col=c: self.on_right_press(row, col))
                btn.bind("<ButtonRelease-3>", lambda e, row=r, col=c: self.on_right_release(row, col))

                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e0e0e0"))
                btn.bind("<Leave>", lambda e, b=btn: self.reset_btn_color(b))

                self.buttons[(r, c)] = btn

        for i in range(self.rows):
            self.frame.grid_rowconfigure(i, weight=1)
        for j in range(self.cols):
            self.frame.grid_columnconfigure(j, weight=1)

        # Track press states for right clicks to ensure toggle happens only on release after press
        self.right_click_pressed = {}

    def reset_btn_color(self, button):
        pos = None
        for key, b in self.buttons.items():
            if b == button:
                pos = key
                break
        if pos:
            if pos in self.revealed:
                button.config(bg="#bbbbbb")
            else:
                button.config(bg="#dcdcdc")

    def create_board(self):
        self.mines.clear()
        self.flags.clear()
        self.revealed.clear()
        self.first_click = True
        self.game_over = False
        self.seconds = 0
        self.update_timer_label()
        self.running = False
        self.right_click_pressed.clear()

        for pos, button in self.buttons.items():
            button.config(text="", relief=tk.RAISED, state=tk.NORMAL, bg="#dcdcdc", fg="black")
            button.unbind("<Enter>")
            button.unbind("<Leave>")
            button.bind("<Enter>", lambda e, b=button: b.config(bg="#e0e0e0"))
            button.bind("<Leave>", lambda e, b=button: self.reset_btn_color(b))

    def place_mines(self, first_click_pos):
        safe_zone = set()
        r0, c0 = first_click_pos
        for i in range(r0-1, r0+2):
            for j in range(c0-1, c0+2):
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    safe_zone.add((i,j))

        available = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) not in safe_zone]
        self.mines = set(random.sample(available, self.num_mines))

    # Left mouse button improved handling
    def on_left_press(self, row, col):
        if self.game_over or (row, col) in self.flags:
            return
        btn = self.buttons[(row, col)]
        btn.config(relief=tk.SUNKEN)

    def on_left_release(self, row, col):
        if self.game_over or (row, col) in self.flags:
            return
        btn = self.buttons[(row, col)]
        if btn['state'] == tk.NORMAL:
            btn.config(relief=tk.RAISED)
        if self.first_click:
            self.place_mines((row, col))
            self.first_click = False
            self.running = True
            self.run_timer()

        if (row, col) in self.mines:
            self.reveal_mines()
            self.buttons[(row,col)].config(bg="#ff4c4c")  # highlight clicked mine
            self.game_over = True
            self.running = False
            messagebox.showinfo("Game Over", "You clicked on a mine! Game Over!")
            return

        self.reveal_cell(row, col)

        if self.check_win():
            self.game_over = True
            self.running = False
            messagebox.showinfo("Congratulations", "You have cleared the minefield!")

    # Right mouse button improved handling with tracked press/release
    def on_right_press(self, row, col):
        if self.game_over or (row, col) in self.revealed:
            self.right_click_pressed[(row, col)] = False
            return
        self.right_click_pressed[(row, col)] = True
        btn = self.buttons[(row, col)]
        btn.config(relief=tk.SUNKEN)

    def on_right_release(self, row, col):
        if self.game_over or (row, col) in self.revealed:
            return
        if self.right_click_pressed.get((row, col), False):
            btn = self.buttons[(row, col)]
            btn.config(relief=tk.RAISED)
            self.toggle_flag(row, col)
        self.right_click_pressed[(row, col)] = False

    def toggle_flag(self, row, col):
        btn = self.buttons[(row, col)]
        if (row, col) in self.flags:
            btn.config(text="")
            self.flags.remove((row, col))
            btn.config(bg="#dcdcdc")
        else:
            if len(self.flags) < self.num_mines:
                btn.config(text="⚑", fg="#d93131")
                self.flags.add((row, col))
                btn.config(bg="#dcdcdc")

    def reveal_cell(self, row, col):
        if (row, col) in self.revealed or (row, col) in self.flags or self.game_over:
            return

        btn = self.buttons[(row, col)]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED, bg="#bbbbbb")
        self.revealed.add((row, col))

        count = self.count_adjacent_mines(row, col)
        if count > 0:
            btn.config(text=str(count), fg=self.get_color(count))
        else:
            btn.config(text="")
            for r in range(row-1, row+2):
                for c in range(col-1, col+2):
                    if 0 <= r < self.rows and 0 <= c < self.cols and (r, c) != (row, col):
                        self.reveal_cell(r, c)

    def count_adjacent_mines(self, row, col):
        count = 0
        for r in range(row-1, row+2):
            for c in range(col-1, col+2):
                if (r, c) != (row, col) and (r, c) in self.mines:
                    count +=1
        return count

    def get_color(self, count):
        colors = {1: '#0000FF', 2: '#008000', 3: '#FF0000', 4: '#000080',
                  5: '#800000', 6: '#008080', 7: '#000000', 8: '#808080'}
        return colors.get(count, '#000000')

    def reveal_mines(self):
        for mine in self.mines:
            if mine not in self.flags:
                btn = self.buttons[mine]
                btn.config(text="*", bg="#ff4c4c", fg="black", relief=tk.SUNKEN)

    def check_win(self):
        return len(self.revealed) == (self.rows * self.cols - self.num_mines)

    def run_timer(self):
        if self.running:
            self.seconds +=1
            self.update_timer_label()
            self.master.after(1000, self.run_timer)

    def update_timer_label(self):
        self.timer_label.config(text=f"Time: {self.seconds}")

    def reset_game(self):
        self.running = False
        self.seconds = 0
        self.right_click_pressed.clear()
        self.create_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
