from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np

class Board(ABC):
    """棋盘抽象基类，定义所有棋盘必须实现的接口。"""

    @abstractmethod
    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """返回当前玩家所有合法落子坐标列表。"""
        pass

    @abstractmethod
    def make_move(self, move: Tuple[int, int]) -> None:
        """在棋盘上落子，并自动切换当前玩家。"""
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """对局是否已结束。"""
        pass

    @abstractmethod
    def get_winner(self) -> Optional[int]:
        """返回胜利方：1(玩家1) / 2(玩家2) ，平局返回 0，未结束返回 None。"""
        pass

    @abstractmethod
    def print_board(self) -> None:
        """在控制台打印棋盘。"""
        pass

    @property
    @abstractmethod
    def current_player(self) -> int:
        """当前轮到的玩家。"""
        pass

    @abstractmethod
    def copy(self) -> 'Board':
        """深拷贝当前棋盘（为后续搜索预留）。"""
        pass


class TicTacToeBoard(Board):
    """3x3 井字棋棋盘。"""

    def __init__(self, size: int = 3):
        self.size = size
        # 0: 空, 1: 玩家1, 2: 玩家2
        self.board = np.zeros((size, size), dtype=np.int8)
        self._current_player = 1
        self.winner: Optional[int] = None
        self.game_over = False
        self.last_move: Optional[Tuple[int, int]] = None

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        if self.game_over:
            return []
        # np.where 返回 (rows, cols) 数组，组合成坐标列表
        rows, cols = np.where(self.board == 0)
        return list(zip(rows, cols))

    def make_move(self, move: Tuple[int, int]) -> None:
        if self.game_over:
            raise ValueError("游戏已结束，不能落子")
        r, c = move
        if not (0 <= r < self.size and 0 <= c < self.size):
            raise ValueError(f"坐标 ({r}, {c}) 超出棋盘范围")
        if self.board[r, c] != 0:
            raise ValueError(f"位置 ({r}, {c}) 已有棋子")

        # 落子
        self.board[r, c] = self._current_player
        self.last_move = move

        # 判断胜负
        if self._check_win(r, c):
            self.winner = self._current_player
            self.game_over = True
        elif len(self.get_legal_moves()) == 0:
            self.winner = 0  # 平局
            self.game_over = True
        else:
            # 切换玩家 (1->2, 2->1)
            self._current_player = 3 - self._current_player

    def _check_win(self, r: int, c: int) -> bool:
        """检查最后落子 (r,c) 是否形成连线胜利。"""
        player = self.board[r, c]
        # 四个方向：水平、垂直、主对角线、副对角线
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # 正方向延伸
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr, nc] == player:
                count += 1
                nr += dr
                nc += dc
            # 负方向延伸
            nr, nc = r - dr, c - dc
            while 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr, nc] == player:
                count += 1
                nr -= dr
                nc -= dc
            if count >= 3:
                return True
        return False

    def is_game_over(self) -> bool:
        return self.game_over

    def get_winner(self) -> Optional[int]:
        return self.winner

    @property
    def current_player(self) -> int:
        return self._current_player

    def print_board(self) -> None:
        symbols = {0: '.', 1: 'X', 2: 'O'}
        print("  " + " ".join(str(i) for i in range(self.size)))
        for r in range(self.size):
            row = [symbols[self.board[r, c]] for c in range(self.size)]
            print(f"{r} {' '.join(row)}")
        print()

    def copy(self) -> 'TicTacToeBoard':
        new_board = TicTacToeBoard(self.size)
        new_board.board = self.board.copy()
        new_board._current_player = self._current_player
        new_board.winner = self.winner
        new_board.game_over = self.game_over
        new_board.last_move = self.last_move
        return new_board
