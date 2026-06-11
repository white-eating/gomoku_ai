"""第三周验证脚本：置换表（Zobrist 哈希 + 字典缓存）与加速效果测量。"""

from board import GomokuBoard
from minimax import compare_transposition_table_speed, evaluate_gomoku, iterative_deepening_search


def build_demo_board():
    board = GomokuBoard()
    # 构造一个中盘局面，保证有足够分支用于观察置换表命中与加速效果。
    moves = [
        (7, 7), (7, 8),
        (8, 7), (8, 8),
        (6, 6), (6, 8),
        (9, 7), (5, 9),
        (7, 6), (8, 6),
    ]
    for move in moves:
        board.make_move(move)
    return board


def main():
    board = build_demo_board()
    player = board.current_player

    print("=== 第三周：Alpha-Beta + 置换表效果对比 ===")
    result = compare_transposition_table_speed(
        board,
        depth=3,
        player=player,
        eval_func=evaluate_gomoku,
        max_moves=12,
    )

    print(f"same_score: {result['same_score']}")
    print(f"same_move: {result['same_move']}")
    print("\n[without transposition table]")
    print(f"move: {result['without_tt']['move']}, score: {result['without_tt']['score']}")
    print(f"nodes: {result['without_tt']['nodes']}")
    print(f"cutoffs: {result['without_tt']['cutoffs']}")
    print(f"elapsed: {result['without_tt']['elapsed']:.4f}s")

    print("\n[with transposition table]")
    print(f"move: {result['with_tt']['move']}, score: {result['with_tt']['score']}")
    print(f"nodes: {result['with_tt']['nodes']}")
    print(f"cutoffs: {result['with_tt']['cutoffs']}")
    print(f"elapsed: {result['with_tt']['elapsed']:.4f}s")
    print(f"tt_lookups: {result['with_tt']['tt_lookups']}")
    print(f"tt_hits: {result['with_tt']['tt_hits']}")
    print(f"tt_hit_rate: {result['with_tt']['tt_hit_rate']:.2%}")
    print(f"tt_stores: {result['with_tt']['tt_stores']}")
    print(f"tt_size: {result['with_tt']['tt_size']}")
    print(f"speedup: {result['speedup']:.2f}x")
    print(f"node_reduction: {result['node_reduction']:.2%}")

    print("\n=== 2 秒迭代加深 + 置换表 ===")
    score, move, stats = iterative_deepening_search(
        board,
        player=player,
        eval_func=evaluate_gomoku,
        time_limit=2.0,
        max_depth=8,
        max_moves=12,
        use_transposition_table=True,
    )
    print(f"best_move: {move}, score: {score}")
    print(f"completed_depth: {stats.completed_depth}")
    print(f"elapsed: {stats.elapsed:.4f}s")
    print(f"nodes: {stats.nodes}")
    print(f"cutoffs: {stats.cutoffs}")
    print(f"tt_lookups: {stats.tt_lookups}")
    print(f"tt_hits: {stats.tt_hits}")
    print(f"tt_hit_rate: {stats.tt_hit_rate:.2%}")
    print(f"tt_stores: {stats.tt_stores}")


if __name__ == "__main__":
    main()
