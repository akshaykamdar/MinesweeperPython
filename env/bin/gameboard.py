import random

class GameBoard:
    def __init__(self, rows=9, cols=9, num_mines=10):
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines

        self.mines = set()
        self.flags = set()
        self.revealed = set()
        self.game_over = False
        self.first_click = True

    def place_mines(self, first_click_pos):
        safe_zone = set()
        r0, c0 = first_click_pos
        for i in range(r0-1, r0+2):
            for j in range(c0-1, c0+2):
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    safe_zone.add((i, j))

        available = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) not in safe_zone]
        self.mines = set(random.sample(available, self.num_mines))
        self.first_click = False

    def count_adjacent_mines(self, row, col):
        count = 0
        for r in range(row-1, row+2):
            for c in range(col-1, col+2):
                if (r, c) != (row, col) and (r, c) in self.mines:
                    count += 1
        return count

    def reveal_cell(self, row, col):
        if self.game_over or (row, col) in self.flags or (row, col) in self.revealed:
            return
        if self.first_click:
            self.place_mines((row, col))
        if (row, col) in self.mines:
            self.game_over = True
            self.revealed.add((row, col))
            return
        self._reveal_recursive(row, col)

    def _reveal_recursive(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if (row, col) in self.revealed or (row, col) in self.flags:
            return
        self.revealed.add((row, col))

        if self.count_adjacent_mines(row, col) == 0:
            for r in range(row-1, row+2):
                for c in range(col-1, col+2):
                    if (r, c) != (row, col):
                        self._reveal_recursive(r, c)

    def toggle_flag(self, row, col):
        if self.game_over or (row, col) in self.revealed:
            return
        if (row, col) in self.flags:
            self.flags.remove((row, col))
        else:
            if len(self.flags) < self.num_mines:
                self.flags.add((row, col))

    def check_win(self):
        return len(self.revealed) == self.rows * self.cols - self.num_mines

    def reset(self):
        self.mines.clear()
        self.flags.clear()
        self.revealed.clear()
        self.game_over = False
        self.first_click = True
