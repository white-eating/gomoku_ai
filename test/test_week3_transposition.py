import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from board import GomokuBoard, TicTacToeBoard
from minimax import (
    TranspositionTable,
    alpha_beta,
    compare_transposition_table_speed,
    evaluate_gomoku,
    evaluate_tic_tac_toe,
    iterative_deepening_search,
    SearchStats,
)
import math


def test_zobrist_hash_same_for_same_position_copy():
    board = GomokuBoard()
    board.make_move((7, 7))
    board.make_move((7, 8))
    tt = TranspositionTable(board.size)
    assert tt.make_key(board, root_player=1) == tt.make_key(board.copy(), root_player=1)


def test_alpha_beta_with_tt_same_result_as_without_tt():
    board = TicTacToeBoard()
    board.make_move((1, 1))
    board.make_move((0, 0))
    normal_stats = SearchStats()
    tt_stats = SearchStats()
    normal_score, normal_move = alpha_beta(
        board, 6, -math.inf, math.inf, True, 1, evaluate_tic_tac_toe, stats=normal_stats
    )
    tt = TranspositionTable(board.size)
    tt_score, tt_move = alpha_beta(
        board, 6, -math.inf, math.inf, True, 1, evaluate_tic_tac_toe, stats=tt_stats, transposition_table=tt
    )
    assert normal_score == tt_score
    assert normal_move == tt_move
    assert tt_stats.tt_lookups > 0
    assert tt_stats.tt_hits > 0
    assert len(tt) > 0


def test_compare_transposition_table_speed_fields():
    board = GomokuBoard()
    for move in [(7, 7), (7, 8), (8, 7), (8, 8), (6, 6), (6, 8)]:
        board.make_move(move)
    result = compare_transposition_table_speed(board, depth=3, player=1, eval_func=evaluate_gomoku, max_moves=10)
    assert result["same_score"]
    assert result["with_tt"]["tt_lookups"] > 0
    assert result["with_tt"]["tt_stores"] > 0
    assert result["with_tt"]["tt_hit_rate"] >= 0


def test_iterative_deepening_reuses_tt_and_reports_stats():
    board = GomokuBoard()
    board.make_move((7, 7))
    board.make_move((7, 8))
    score, move, stats = iterative_deepening_search(
        board, 1, evaluate_gomoku, time_limit=2.0, max_depth=4, max_moves=10, use_transposition_table=True
    )
    assert move in board.get_legal_moves()
    assert stats.completed_depth >= 1
    assert stats.tt_lookups > 0
    assert stats.tt_stores > 0
