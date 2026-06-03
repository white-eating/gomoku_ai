# minimax.py
import math
from board import Board
from player import Player

# ---------- 评估函数 ----------
def evaluate_tic_tac_toe(board: Board, player: int) -> float:
    """终局评估：胜1，负-1，平0。"""
    winner = board.get_winner()
    if winner == player:
        return 1.0
    elif winner == 0:
        return -0.0
    elif winner is not None :
        return -1.0
    return 0.0

def heuristic_tic_tac_toe(board: Board, player: int) -> float:
    """启发式评估（仅供参考，不推荐用于完美玩法）。"""
    if board.is_game_over():
        return evaluate_tic_tac_toe(board, player)
    score = 0
    center = board.size // 2
    for r in range(board.size):
        for c in range(board.size):
            if board.board[r, c] == player:
                if (r, c) == (center, center):
                    score += 5
                elif r in (0, board.size-1) and c in (0, board.size-1):
                    score += 3
                else:
                    score += 1
            elif board.board[r, c] != 0:
                if (r, c) == (center, center):
                    score -= 5
                elif r in (0, board.size-1) and c in (0, board.size-1):
                    score -= 3
                else:
                    score -= 1
    return score

# ---------- Minimax (无剪枝) ----------
def minimax(board: Board, depth: int, maximizing_player: bool, player: int, eval_func):
    if board.is_game_over():
        return eval_func(board, player), None
    if depth == 0:
        return eval_func(board, player), None

    legal_moves = board.get_legal_moves()
    if not legal_moves:
        return eval_func(board, player), None

    best_move = None
    if maximizing_player:
        max_score = -math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = minimax(new_board, depth-1, False, player, eval_func)
            if score > max_score:
                max_score = score
                best_move = move
        return max_score, best_move
    else:
        min_score = math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = minimax(new_board, depth-1, True, player, eval_func)
            if score < min_score:
                min_score = score
                best_move = move
        return min_score, best_move

# ---------- Alpha-Beta 剪枝 ----------
def alpha_beta(board: Board, depth: int, alpha: float, beta: float,
               maximizing_player: bool, player: int, eval_func):
    if board.is_game_over():
        return eval_func(board, player), None
    if depth == 0:
        return eval_func(board, player), None

    legal_moves = board.get_legal_moves()
    if not legal_moves:
        return eval_func(board, player), None

    best_move = None
    if maximizing_player:
        value = -math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = alpha_beta(new_board, depth-1, alpha, beta, False, player, eval_func)
            if score > value:
                value = score
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_move
    else:
        value = math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = alpha_beta(new_board, depth-1, alpha, beta, True, player, eval_func)
            if score < value:
                value = score
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, best_move

# ---------- AI 玩家 ----------
class MinimaxPlayer(Player):
    def __init__(self, player_id: int, depth=9, use_alpha_beta=True, eval_func=None):
        self.player_id = player_id  # 记录 AI 是玩家 1 还是 2
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.eval_func = eval_func if eval_func is not None else evaluate_tic_tac_toe

    def get_move(self, board: Board):
        if self.use_alpha_beta:
            best_score, best_move = alpha_beta(
                board, 
                self.depth, 
                -math.inf, 
                math.inf, 
                True, # 对于 AI 来说，它总是试图最大化自己的得分
                self.player_id,
                self.eval_func 
            )
        else:
            best_score, best_move = minimax(
                board, 
                self.depth, 
                True, 
                self.player_id, 
                self.eval_func 
            )
        
        #print(f"[DEBUG] AI 选择: {best_move}, 得分: {best_score}")
        return best_move