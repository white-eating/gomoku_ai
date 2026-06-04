"""第二周功能验证脚本：Alpha-Beta、一致性、迭代加深、15x15 GomokuBoard。"""
from board import GomokuBoard, TicTacToeBoard
from minimax import (
    MinimaxPlayer,
    compare_minimax_and_alpha_beta,
    evaluate_gomoku,
    evaluate_tic_tac_toe,
)


def demo_alpha_beta_consistency():
    board = TicTacToeBoard()
    board.make_move((1, 1))
    board.make_move((0, 0))
    result = compare_minimax_and_alpha_beta(board, depth=5, player=1, eval_func=evaluate_tic_tac_toe)
    print("[1] Alpha-Beta 与无剪枝 Minimax 一致性验证")
    print(result)
    print()


def demo_iterative_deepening_gomoku():
    board = GomokuBoard()
    board.make_move((7, 7))
    board.make_move((7, 8))
    ai = MinimaxPlayer(
        player_id=1,
        depth=6,
        eval_func=evaluate_gomoku,
        use_alpha_beta=True,
        iterative=True,
        time_limit=2.0,
        max_moves=20,
    )
    move = ai.get_move(board)
    print("[2] 五子棋迭代加深搜索，时间阈值 2 秒")
    print(f"AI move = {move}")
    print(f"stats = {ai.last_stats}")
    print()


def demo_gomoku_win_detection():
    board = GomokuBoard()
    moves = [(7, 3), (0, 0), (7, 4), (0, 1), (7, 5), (0, 2), (7, 6), (0, 3), (7, 7)]
    for move in moves:
        board.make_move(move)
    print("[3] 15x15 GomokuBoard 与五子连珠判断")
    board.print_board()
    print(f"winner = {board.get_winner()}")


if __name__ == "__main__":
    demo_alpha_beta_consistency()
    demo_iterative_deepening_gomoku()
    demo_gomoku_win_detection()
