#!/usr/bin/env python3
# collect_experiment_data.py
"""
采集报告中所需的真实实验数据：
1. 井字棋：纯 Minimax vs Alpha-Beta 剪枝（深度2,4,6,8）
2. 五子棋：不同深度（1,3,5,7）对随机玩家的胜率及平均每步耗时
"""

import time
import numpy as np
from board import TicTacToeBoard, GomokuBoard
from minimax import MinimaxPlayer, SearchStats
from player import RandomPlayer

def run_tic_tac_toe_comparison():
    """井字棋：纯Minimax vs Alpha-Beta 对比"""
    print("\n========== 井字棋：纯 Minimax vs Alpha-Beta 剪枝 ==========")
    print(f"{'深度':<4} {'Minimax节点':<12} {'Alpha-Beta节点':<14} {'剪枝比例':<10} {'Minimax耗时(s)':<14} {'Alpha-Beta耗时(s)':<18} {'加速比':<8}")
    print("-" * 85)

    for depth in [2, 4, 6, 8]:
        # 纯 Minimax（不启用 Alpha-Beta）
        board = TicTacToeBoard()
        player = MinimaxPlayer(player_id=1, depth=depth, use_alpha_beta=False, eval_func=None, iterative=False)
        # 为了获得稳定的搜索统计，直接调用 alpha_beta 函数（但需要传入同一个棋盘）
        # 这里更简单：手动调用搜索函数并记录 stats
        from minimax import minimax  # 直接导入纯minimax函数
        stats = SearchStats()
        start = time.perf_counter()
        score, move = minimax(board, depth, True, 1, player.eval_func, stats=stats)
        minimax_time = time.perf_counter() - start
        minimax_nodes = stats.nodes

        # Alpha-Beta
        board2 = TicTacToeBoard()
        player2 = MinimaxPlayer(player_id=1, depth=depth, use_alpha_beta=True, eval_func=None, iterative=False)
        from minimax import alpha_beta
        stats2 = SearchStats()
        start2 = time.perf_counter()
        score2, move2 = alpha_beta(board2, depth, -float('inf'), float('inf'), True, 1, player2.eval_func, stats=stats2)
        ab_time = time.perf_counter() - start2
        ab_nodes = stats2.nodes

        pruning_rate = (1 - ab_nodes / minimax_nodes) * 100 if minimax_nodes else 0
        speedup = minimax_time / ab_time if ab_time > 0 else 0

        print(f"{depth:<4} {minimax_nodes:<12} {ab_nodes:<14} {pruning_rate:<9.1f}% {minimax_time:<14.4f} {ab_time:<18.4f} {speedup:<8.2f}")

def run_gomoku_depth_experiment(num_games_per_side=30, max_moves=30):
    """
    五子棋不同深度对随机玩家的胜率及平均每步耗时
    num_games_per_side: 先手/后手各多少局
    """
    print("\n========== 五子棋：不同深度 vs 随机玩家 ==========")
    print(f"每深度运行先手 {num_games_per_side} 局 + 后手 {num_games_per_side} 局，max_moves={max_moves}")
    print(f"{'深度':<4} {'先手胜率':<10} {'后手胜率':<10} {'平均每步耗时(s)':<18}")
    print("-" * 50)

    for depth in [1, 3, 5, 7]:
        # 先手
        wins_first = 0
        total_time_first = 0.0
        total_moves_first = 0
        for _ in range(num_games_per_side):
            board = GomokuBoard(size=15)
            ai = MinimaxPlayer(player_id=1, depth=depth, use_alpha_beta=True,
                               max_moves=max_moves, use_transposition_table=True)
            random_opponent = RandomPlayer()
            ai.player_id = 1
            random_opponent.player_id = 2
            players = {1: ai, 2: random_opponent}
            step_times = []
            while not board.is_game_over():
                cur = players[board.current_player]
                start = time.perf_counter()
                move = cur.get_move(board)
                elapsed = time.perf_counter() - start
                if cur == ai:
                    step_times.append(elapsed)
                board.make_move(move)
            winner = board.get_winner()
            if winner == 1:
                wins_first += 1
            total_time_first += sum(step_times)
            total_moves_first += len(step_times)
        avg_step_time_first = total_time_first / total_moves_first if total_moves_first else 0
        win_rate_first = wins_first / num_games_per_side * 100

        # 后手
        wins_second = 0
        total_time_second = 0.0
        total_moves_second = 0
        for _ in range(num_games_per_side):
            board = GomokuBoard(size=15)
            random_opponent = RandomPlayer()
            ai = MinimaxPlayer(player_id=2, depth=depth, use_alpha_beta=True,
                               max_moves=max_moves, use_transposition_table=True)
            random_opponent.player_id = 1
            ai.player_id = 2
            players = {1: random_opponent, 2: ai}
            step_times = []
            while not board.is_game_over():
                cur = players[board.current_player]
                start = time.perf_counter()
                move = cur.get_move(board)
                elapsed = time.perf_counter() - start
                if cur == ai:
                    step_times.append(elapsed)
                board.make_move(move)
            winner = board.get_winner()
            if winner == 2:
                wins_second += 1
            total_time_second += sum(step_times)
            total_moves_second += len(step_times)
        avg_step_time_second = total_time_second / total_moves_second if total_moves_second else 0
        win_rate_second = wins_second / num_games_per_side * 100

        # 平均每步耗时（先手后手平均）
        avg_step_time = (avg_step_time_first + avg_step_time_second) / 2
        print(f"{depth:<4} {win_rate_first:<9.1f}% {win_rate_second:<9.1f}% {avg_step_time:<18.4f}")

if __name__ == "__main__":
    run_tic_tac_toe_comparison()
    run_gomoku_depth_experiment(num_games_per_side=30, max_moves=30)