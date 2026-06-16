# tournament.py
import time
import argparse
from typing import Type, Tuple
from board import GomokuBoard
from player import Player
from minimax import MinimaxPlayer
from mcts_from_scratch import MCTSPlayer

def play_one_game(player1: Player, player2: Player, verbose: bool = False) -> int:
    board = GomokuBoard(size=15)
    players = {1: player1, 2: player2}
    player1.player_id = 1
    player2.player_id = 2

    while not board.is_game_over():
        cur = players[board.current_player]
        move = cur.get_move(board)
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
                        progress_interval: int = 1, board_size: int = 15) -> Tuple[int, int, int]:
    if player1_kwargs is None:
        player1_kwargs = {}
    if player2_kwargs is None:
        player2_kwargs = {}

    wins1, wins2, draws = 0, 0, 0
    start_total = time.time()

    for i in range(1, num_games + 1):
        game_start = time.time()
        # 关键修复：传入 player_id 作为第一个位置参数
        p1 = player1_cls(1, **player1_kwargs)
        p2 = player2_cls(2, **player2_kwargs)
        winner = play_one_game(p1, p2, verbose=False)
        if winner == 1:
            wins1 += 1
        elif winner == 2:
            wins2 += 1
        else:
            draws += 1

        if i % progress_interval == 0:
            elapsed = time.time() - game_start
            total_elapsed = time.time() - start_total
            avg_time = total_elapsed / i
            remaining = avg_time * (num_games - i)
            print(f"[{i}/{num_games}] 本轮耗时 {elapsed:.2f}s | "
                  f"进度 {i/num_games*100:.1f}% | "
                  f"比分 {wins1}:{wins2} (平{draws}) | "
                  f"预计剩余 {remaining:.0f}s")

    return wins1, wins2, draws

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-games", type=int, default=100, help="对局数")
    parser.add_argument("--player1", type=str, default="minimax", choices=["minimax", "mcts"])
    parser.add_argument("--player2", type=str, default="minimax", choices=["minimax", "mcts"])
    parser.add_argument("--board-size", type=int, default=15, help="棋盘大小")
    parser.add_argument("--depth1", type=int, default=3, help="Minimax深度(玩家1)")
    parser.add_argument("--depth2", type=int, default=3, help="Minimax深度(玩家2)")
    parser.add_argument("--mcts-sim1", type=int, default=300, help="MCTS模拟次数(玩家1)")
    parser.add_argument("--mcts-sim2", type=int, default=300, help="MCTS模拟次数(玩家2)")
    parser.add_argument("--max-moves", type=int, default=24, help="Minimax每步候选数")
    args = parser.parse_args()

    def get_player_cls_and_kwargs(name, depth, mcts_sim):
        if name == "minimax":
            return MinimaxPlayer, {"depth": depth, "use_alpha_beta": True,
                                   "max_moves": args.max_moves,
                                   "use_transposition_table": True}
        else:
            return MCTSPlayer, {"num_simulations": mcts_sim}

    cls1, kwargs1 = get_player_cls_and_kwargs(args.player1, args.depth1, args.mcts_sim1)
    cls2, kwargs2 = get_player_cls_and_kwargs(args.player2, args.depth2, args.mcts_sim2)

    print(f"开始 {args.num_games} 局: {args.player1} vs {args.player2}, 棋盘{args.board_size}x{args.board_size}")
    w1, w2, d = play_multiple_games(cls1, cls2, num_games=args.num_games,
                                    player1_kwargs=kwargs1, player2_kwargs=kwargs2,
                                    board_size=args.board_size)
    print(f"\n最终结果: {args.player1} 胜 {w1}, {args.player2} 胜 {w2}, 平局 {d}")
    print(f"胜率: {args.player1} {w1/args.num_games*100:.1f}% , {args.player2} {w2/args.num_games*100:.1f}%")