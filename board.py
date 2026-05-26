from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

class Board(ABC):
    @abstractmethod
    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """返回当前玩家所有可落子的坐标列表"""
        pass

    @abstractmethod
    def make_move(self, move: Tuple[int, int]) -> None:
        """在棋盘上落子，并自动切换玩家"""
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """对局是否结束"""
        pass

    @abstractmethod
    def get_winner(self) -> Optional[int]:
        """返回胜利方 (1 或 2)，平局返回 0，未结束返回 None"""
        pass

    @abstractmethod
    def print_board(self) -> None:
        """在控制台打印当前棋盘"""
        pass

    @property
    @abstractmethod
    def current_player(self) -> int:
        """当前轮到的玩家 (1 或 2)"""
        pass

    @abstractmethod
    def copy(self) -> 'Board':
        """深拷贝当前棋盘（为后续搜索树预留）"""
        pass

"""初始化"""
class TicTacToeBoard(Board):
    def __init__(self, size: int = 3):
        self.size = size
        # 用 numpy 二维数组存棋子，0空，1玩家1，2玩家2
        self.board = np.zeros((size, size), dtype=np.int8)
        self._current_player = 1
        self.winner = None
        self.game_over = False
        self.last_move = None

"""接口"""
def get_legal_moves(self) -> List[Tuple[int, int]]:
    if self.game_over:
        return []
    return list(zip(*np.where(self.board == 0)))

def make_move(self, move: Tuple[int, int]) -> None:
    r, c = move
    if self.board[r, c] != 0 or self.game_over:
        raise ValueError("非法落子")
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
        self._current_player = 3 - self._current_player  # 切换玩家

"""胜负判断"""
def _check_win(self, r: int, c: int) -> bool:
    player = self.board[r, c]
    directions = [(0,1), (1,0), (1,1), (1,-1)]
    for dr, dc in directions:
        count = 1
        for delta in [1, -1]:
            nr, nc = r + dr*delta, c + dc*delta
            while 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr, nc] == player:
                count += 1
                nr += dr*delta
                nc += dc*delta
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
    for r in range(self.size):
        row = ' '.join(symbols[self.board[r, c]] for c in range(self.size))
        print(row)
    print()

def copy(self) -> 'TicTacToeBoard':
    new_board = TicTacToeBoard(self.size)
    new_board.board = self.board.copy()
    new_board._current_player = self._current_player
    new_board.winner = self.winner
    new_board.game_over = self.game_over
    new_board.last_move = self.last_move
    return new_board
