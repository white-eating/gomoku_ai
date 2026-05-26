from board import TicTacToeBoard
from player import RandomPlayer
from game import Game

# 随机 vs 随机，自动对弈 100 局统计
results = {1: 0, 2: 0, 0: 0}
for _ in range(100):
    board = TicTacToeBoard()
    game = Game(board, RandomPlayer(seed=_), RandomPlayer(seed=_+1))
    winner = game.play(verbose=False)
    results[winner] += 1

print("先手胜: {}, 后手胜: {}, 平局: {}".format(results[1], results[2], results[0]))
