from board import TicTacToeBoard
from player import RandomPlayer, HumanPlayer

class Game:
    def __init__(self, board, player1, player2):
        self.board = board
        self.players = {1: player1, 2: player2}

    def play(self, verbose=True):
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
                print(f"玩家 {winner} 获胜！")
        return self.board.get_winner()
