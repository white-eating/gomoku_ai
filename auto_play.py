import time
import argparse
from typing import Tuple, Type, Optional
from board import GomokuBoard
from player import Player
from minimax import MinimaxPlayer

def play_one_game(player1: Player, player2: Player, verbose: bool = False) -> int:
    """对弈一局，返回胜利方：1/2/0(平局)"""
    board = GomokuBoard(size=15)
    players = {1: player1, 2: player2}
    player1.player_id = 1
    player2.player_id = 2

    while not board.is_game_over():
        current = players[board.current_player]
        move = current.get_move(board)
        board.make_move(move)
        if verbose:
            print(f"玩家{board.current_player} 落子 {move}")
            board.print_board()
            print()

    winner = board.get_winner()
    if verbose:
        if winner == 0:
            print("平局")
        else:
            print(f"玩家{winner} 获胜")
    return winner

def play_multiple_games(player1_cls: Type[Player], player2_cls: Type[Player],
                        num_games: int = 100, player1_kwargs=None, player2_kwargs=None,
                        verbose: bool = False, progress_interval: int = 1) -> Tuple[int, int, int]:
    """
    批量对弈，返回 (player1胜场, player2胜场, 平局数)
    progress_interval: 每多少局打印一次进度（设为1表示每局都打印）
    """
    if player1_kwargs is None:
        player1_kwargs = {}
    if player2_kwargs is None:
        player2_kwargs = {}

    wins1, wins2, draws = 0, 0, 0
    start_total = time.time()

    for i in range(1, num_games + 1):
        game_start = time.time()
        p1 = player1_cls(player_id=1, **player1_kwargs)
        p2 = player2_cls(player_id=2, **player2_kwargs)
        winner = play_one_game(p1, p2, verbose=False)
        if winner == 1:
            wins1 += 1
        elif winner == 2:
            wins2 += 1
        else:
            draws += 1

        # 实时进度显示
        if i % progress_interval == 0:
            elapsed = time.time() - game_start
            total_elapsed = time.time() - start_total
            avg_time = total_elapsed / i
            remaining = avg_time * (num_games - i)
            print(f"[{i}/{num_games}] 本轮耗时 {elapsed:.2f}s | "
                  f"总进度 {i/num_games*100:.1f}% | "
                  f"比分 {wins1}:{wins2} (平{draws}) | "
                  f"预计剩余 {remaining:.0f}s")

    return wins1, wins2, draws

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="五子棋 AI 自动对弈")
    parser.add_argument("--num-games", type=int, default=100, help="对弈局数")
    parser.add_argument("--depth1", type=int, default=3, help="玩家1的Minimax深度")
    parser.add_argument("--depth2", type=int, default=4, help="玩家2的Minimax深度")
    parser.add_argument("--use-ab", action="store_true", default=True, help="是否使用Alpha-Beta")
    parser.add_argument("--progress", type=int, default=1, help="每N局打印一次进度")
    args = parser.parse_args()

    print(f"开始 {args.num_games} 局对弈: Minimax(depth={args.depth1}) vs Minimax(depth={args.depth2})")
    w1, w2, d = play_multiple_games(
        MinimaxPlayer, MinimaxPlayer,
        num_games=args.num_games,
        player1_kwargs={"depth": args.depth1, "use_alpha_beta": args.use_ab},
        player2_kwargs={"depth": args.depth2, "use_alpha_beta": args.use_ab},
        progress_interval=args.progress
    )
    print(f"\n最终结果: 玩家1胜 {w1} 场, 玩家2胜 {w2} 场, 平局 {d} 场")
    print(f"胜率: 玩家1 {w1/args.num_games*100:.1f}% , 玩家2 {w2/args.num_games*100:.1f}%")