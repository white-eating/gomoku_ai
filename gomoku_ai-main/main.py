from board import TicTacToeBoard
from player import HumanPlayer, RandomPlayer
from game import Game
from cli import CLI

def run_human_vs_ai():
    """人机对弈：人类 vs 随机AI。"""
    board = TicTacToeBoard()
    game = Game(board, HumanPlayer(), RandomPlayer())
    cli = CLI(game)
    cli.run()


def run_random_vs_random(games=100):
    """运行多局随机对局并统计结果。"""
    results = {1: 0, 2: 0, 0: 0}
    for i in range(games):
        board = TicTacToeBoard()
        # 每局使用不同种子，使对局不同
        game = Game(board, RandomPlayer(seed=i*2), RandomPlayer(seed=i*2+1))
        winner = game.play(verbose=False)
        results[winner] += 1
    print(f"随机 vs 随机，{games} 局统计：")
    print(f"先手胜: {results[1]} ({results[1]/games*100:.1f}%)")
    print(f"后手胜: {results[2]} ({results[2]/games*100:.1f}%)")
    print(f"平局:   {results[0]} ({results[0]/games*100:.1f}%)")

if __name__ == "__main__":
    run_human_vs_ai()
