import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from board import GomokuBoard, TicTacToeBoard
from minimax import (
    MinimaxPlayer,
    compare_minimax_and_alpha_beta,
    evaluate_gomoku,
    evaluate_tic_tac_toe,
    iterative_deepening_search,
)


def place_sequence(board, moves):
    for move in moves:
        board.make_move(move)


def test_gomoku_initial_state():
    board = GomokuBoard()
    assert board.size == 15
    assert board.current_player == 1
    assert len(board.get_legal_moves()) == 225
    assert board.get_winner() is None


def test_gomoku_horizontal_win():
    board = GomokuBoard()
    moves = [(7, 3), (0, 0), (7, 4), (0, 1), (7, 5), (0, 2), (7, 6), (0, 3), (7, 7)]
    place_sequence(board, moves)
    assert board.is_game_over()
    assert board.get_winner() == 1


def test_gomoku_vertical_win():
    board = GomokuBoard()
    moves = [(3, 7), (0, 0), (4, 7), (0, 1), (5, 7), (0, 2), (6, 7), (0, 3), (7, 7)]
    place_sequence(board, moves)
    assert board.get_winner() == 1


def test_gomoku_diagonal_win():
    board = GomokuBoard()
    moves = [(3, 3), (0, 0), (4, 4), (0, 1), (5, 5), (0, 2), (6, 6), (0, 3), (7, 7)]
    place_sequence(board, moves)
    assert board.get_winner() == 1


def test_gomoku_anti_diagonal_win():
    board = GomokuBoard()
    moves = [(3, 7), (0, 0), (4, 6), (0, 1), (5, 5), (0, 2), (6, 4), (0, 3), (7, 3)]
    place_sequence(board, moves)
    assert board.get_winner() == 1


def test_alpha_beta_same_as_minimax_on_tictactoe():
    board = TicTacToeBoard()
    board.make_move((1, 1))
    board.make_move((0, 0))
    result = compare_minimax_and_alpha_beta(board, depth=5, player=1, eval_func=evaluate_tic_tac_toe)
    assert result["same_score"]
    assert result["same_move"]
    assert result["alpha_beta"]["nodes"] <= result["minimax"]["nodes"]


def test_iterative_deepening_returns_legal_move_quickly():
    board = GomokuBoard()
    board.make_move((7, 7))
    board.make_move((7, 8))
    score, move, stats = iterative_deepening_search(
        board,
        player=1,
        eval_func=evaluate_gomoku,
        time_limit=2.0,
        max_depth=4,
        use_alpha_beta=True,
        max_moves=12,
    )
    assert move in board.get_legal_moves()
    assert stats.completed_depth >= 1
    assert stats.elapsed <= 2.5


def test_minimax_player_iterative_for_gomoku():
    board = GomokuBoard()
    ai = MinimaxPlayer(player_id=1, depth=3, eval_func=evaluate_gomoku, iterative=True, time_limit=2.0, max_moves=10)
    move = ai.get_move(board)
    assert move == (7, 7)
