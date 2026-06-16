# test_mcts.py
from board import GomokuBoard
from mcts_from_scratch import MCTSPlayer

if __name__ == "__main__":
    board = GomokuBoard(size=9)   # 小棋盘测试速度
    player = MCTSPlayer(player_id=1, num_simulations=300)
    move = player.get_move(board)
    print(f"MCTS 选择落子: {move}")
    board.make_move(move)
    board.print_board()