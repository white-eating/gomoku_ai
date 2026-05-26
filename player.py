from abc import ABC, abstractmethod
import numpy as np
from board import Board

class Player(ABC):
    """玩家抽象基类。"""

    @abstractmethod
    def get_move(self, board: Board) -> tuple:
        """根据当前棋盘状态返回一个落子坐标 (row, col)。"""
        pass


class HumanPlayer(Player):
    """人类玩家，从命令行输入坐标。"""

    def get_move(self, board: Board) -> tuple:
        while True:
            try:
                move_str = input(f"玩家 {board.current_player} 请输入坐标 (行 列): ")
                r, c = map(int, move_str.strip().split())
                if (r, c) in board.get_legal_moves():
                    return (r, c)
                else:
                    print("该位置不合法或已被占据，请重新输入。")
            except ValueError:
                print("输入格式错误，请按 '行 列' 格式输入两个整数，例如 '0 1'。")


class RandomPlayer(Player):
    """随机落子的 AI 玩家。"""

    def __init__(self, seed: int = None):
        self.rng = np.random.default_rng(seed)

    def get_move(self, board: Board) -> tuple:
        moves = board.get_legal_moves()
        if not moves:
            raise ValueError("没有合法走法")
        idx = self.rng.integers(len(moves))
        return tuple(moves[idx])
