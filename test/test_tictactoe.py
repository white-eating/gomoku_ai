import sys
from pathlib import Path

# 将项目根目录（test 的上一级）加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from board import TicTacToeBoard

class TestTicTacToe:
    def setup_method(self):
        self.board = TicTacToeBoard()

    def test_initial_state(self):
        assert self.board.current_player == 1
        assert not self.board.is_game_over()
        assert self.board.get_winner() is None
        assert len(self.board.get_legal_moves()) == 9

    def test_legal_move_and_switch(self):
        self.board.make_move((0, 0))
        assert self.board.board[0, 0] == 1
        assert self.board.current_player == 2
        assert (0, 0) not in self.board.get_legal_moves()

    def test_win_horizontal(self):
        # X moves
        self.board.make_move((0, 0))  # 1
        self.board.make_move((1, 0))  # 2
        self.board.make_move((0, 1))  # 1
        self.board.make_move((1, 1))  # 2
        self.board.make_move((0, 2))  # 1 -> wins
        assert self.board.is_game_over()
        assert self.board.get_winner() == 1

    def test_win_vertical(self):
        self.board.make_move((0, 0))  # 1
        self.board.make_move((1, 1))  # 2
        self.board.make_move((1, 0))  # 1
        self.board.make_move((2, 2))  # 2
        self.board.make_move((2, 0))  # 1 -> wins
        assert self.board.get_winner() == 1

    def test_win_diagonal(self):
        self.board.make_move((0, 0))  # 1
        self.board.make_move((0, 1))  # 2
        self.board.make_move((1, 1))  # 1
        self.board.make_move((0, 2))  # 2
        self.board.make_move((2, 2))  # 1 -> wins
        assert self.board.get_winner() == 1

    def test_win_anti_diagonal(self):
        self.board.make_move((0, 2))  # 1
        self.board.make_move((0, 1))  # 2
        self.board.make_move((1, 1))  # 1
        self.board.make_move((1, 0))  # 2
        self.board.make_move((2, 0))  # 1 -> wins
        assert self.board.get_winner() == 1

    def test_draw(self):
        # 填满棋盘产生平局
        moves = [(0,0),(0,1),(0,2),
                 (1,1),(1,0),(1,2),
                 (2,0),(2,1),(2,2)]
        for i, m in enumerate(moves):
            self.board.make_move(m)
            if i < 8:  # 最后一次之前不应结束
                assert not self.board.is_game_over()
        assert self.board.is_game_over()
        assert self.board.get_winner() == 0

    def test_illegal_move_raises(self):
        self.board.make_move((0, 0))
        with pytest.raises(ValueError):
            self.board.make_move((0, 0))  # 已有棋子
        with pytest.raises(ValueError):
            self.board.make_move((3, 0))   # 超出范围

    def test_copy_independence(self):
        self.board.make_move((0, 0))
        board2 = self.board.copy()
        self.board.make_move((1, 1))
        assert self.board.board[1, 1] == 2
        assert board2.board[1, 1] == 0
        assert board2.current_player == 2  # 拷贝时的当前玩家
        assert self.board.current_player == 1
