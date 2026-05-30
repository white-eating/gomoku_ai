from board import Board
from player import Player

class Game:
    """游戏控制器，管理两个玩家交替落子直到游戏结束。"""

    def __init__(self, board: Board, player1: Player, player2: Player):
        self.board = board
        self.players = {1: player1, 2: player2}
        self.history: list = []

    def play(self, verbose: bool = True):
        """开始游戏循环，返回最终 winner (0/1/2)。"""
        while not self.board.is_game_over():
            if verbose:
                self.board.print_board()
            current = self.board.current_player
            move = self.players[current].get_move(self.board)
            self.do_move(move)

        if verbose:
            self.board.print_board()
            winner = self.board.get_winner()
            if winner == 0:
                print("平局！")
            else:
                print(f"玩家 {winner} ({('X' if winner==1 else 'O')}) 获胜！")
        return self.board.get_winner()

    def do_move(self, move):
        """落子并自动保存历史（供 CLI 等手动循环使用）。"""
        self.history.append(self.board.copy())
        self.board.make_move(move)

    def undo(self, steps: int = 1) -> bool:
        """撤销指定步数，返回是否成功撤销了至少一步。"""
        if not self.history:
            return False
        actual = min(steps, len(self.history))
        restored = None
        for _ in range(actual):
            restored = self.history.pop()
        self.board = restored
        return True
