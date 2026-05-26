from abc import ABC, abstractmethod
from board import Board

class Player(ABC):
    @abstractmethod
    def get_move(self, board: Board) -> tuple:
        pass

class HumanPlayer(Player):
    def get_move(self, board: Board):
        while True:
            try:
                move = input(f"玩家{board.current_player} 输入坐标 (行 列): ")
                r, c = map(int, move.split())
                if (r, c) in board.get_legal_moves():
                    return (r, c)
                print("不合法，重新输入")
            except:
                print("格式错误")

class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)

    def get_move(self, board: Board):
        moves = board.get_legal_moves()
        return tuple(moves[self.rng.integers(len(moves))])
