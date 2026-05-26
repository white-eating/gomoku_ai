from board import Board
from player import Player

class Game:
    """游戏控制器，管理两个玩家交替落子直到游戏结束。"""

    def __init__(self, board: Board, player1: Player, player2: Player):
        self.board = board
        self.players = {1: player1, 2: player2}

    def play(self, verbose: bool = True):
        """开始游戏循环，返回最终 winner (0/1/2)。"""
        while not self.board.is_game_over():
            if verbose:
                self.board.print_board()
            current = self.board.current_player
            move = self.players[current].get_move(self.board)
            self.board.make_move(move)

        if verbose:
            self.board.print_board()
            winner = self.board.get_winner()
            if winner == 0:
                print("平局！")
            else:
                print(f"玩家 {winner} ({('X' if winner==1 else 'O')}) 获胜！")
        return self.board.get_winner()
