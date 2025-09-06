import pytest
from gameboard import GameBoard

@pytest.fixture
def board():
    gameboard = GameBoard()
    gameboard.reset()
    return gameboard

def test_mines_not_in_safe_zone(board):
    first_click = (3, 3)
    board.place_mines(first_click)
    safe_zone = {(r, c) for r in range(first_click[0]-1, first_click[0]+2)
                 for c in range(first_click[1]-1, first_click[1]+2)}
    assert not any(m in safe_zone for m in board.mines)

def test_flagging(board):
    pos = (0, 0)
    board.toggle_flag(*pos)
    assert pos in board.flags
    board.toggle_flag(*pos)
    assert pos not in board.flags

def test_reveal_safe_cell(board):
    board.place_mines((0, 0))
    safe_cell = next((r, c) for r in range(board.rows) for c in range(board.cols) if (r, c) not in board.mines)
    board.reveal_cell(*safe_cell)
    assert safe_cell in board.revealed
    assert not board.game_over

def test_reveal_mine_ends_game(board):
    board.place_mines((0, 0))
    mine = next(iter(board.mines))
    board.reveal_cell(*mine)
    assert board.game_over

def test_check_win(board):
    board.place_mines((0, 0))
    for r in range(board.rows):
        for c in range(board.cols):
            if (r, c) not in board.mines:
                board.reveal_cell(r, c)
    assert board.check_win()
