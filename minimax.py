# minimax.py
import math
import random
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from board import Board
from player import Player

Move = Tuple[int, int]
EvalFunc = Callable[[Board, int], float]

EXACT = "EXACT"
LOWER_BOUND = "LOWER"
UPPER_BOUND = "UPPER"


@dataclass
class SearchStats:
    """搜索统计信息，用于验证剪枝、置换表命中率和加速效果。"""
    nodes: int = 0
    cutoffs: int = 0
    completed_depth: int = 0
    elapsed: float = 0.0
    timed_out: bool = False
    tt_lookups: int = 0
    tt_hits: int = 0
    tt_stores: int = 0

    @property
    def tt_hit_rate(self) -> float:
        if self.tt_lookups == 0:
            return 0.0
        return self.tt_hits / self.tt_lookups


@dataclass
class TranspositionEntry:
    """置换表条目：同一局面在足够搜索深度下的缓存结果。"""
    depth: int
    value: float
    flag: str
    best_move: Optional[Move]


class SearchTimeout(Exception):
    pass


class ZobristHasher:
    """
    Zobrist 哈希器。
    为每个 (行, 列, 棋子类型) 预生成 64 位随机数，局面哈希为这些随机数的异或值。
    为避免同一棋面但轮到不同玩家时冲突，额外加入 current_player 随机数。
    """

    def __init__(self, size: int, seed: int = 20260608):
        self.size = size
        rng = random.Random(seed + size * 131)
        self.piece_keys = np.array(
            [
                [[0, rng.getrandbits(64), rng.getrandbits(64)] for _ in range(size)]
                for _ in range(size)
            ],
            dtype=np.uint64,
        )
        self.player_keys = {1: rng.getrandbits(64), 2: rng.getrandbits(64)}
        self.cache_name = f"_zobrist_cache_{seed}_{size}"

    def hash_board(self, board: Board) -> int:
        cached = getattr(board, self.cache_name, None)
        if cached is not None:
            return cached

        # 向量化取出每个位置当前棋子的随机数，再整体异或，比 Python 双重循环更快。
        selected = np.take_along_axis(self.piece_keys, board.board[:, :, None], axis=2).reshape(-1)
        h = int(np.bitwise_xor.reduce(selected, dtype=np.uint64))
        h ^= self.player_keys.get(board.current_player, 0)
        setattr(board, self.cache_name, h)
        return h


class TranspositionTable:
    """基于 Zobrist 哈希的字典缓存。"""

    def __init__(self, board_size: int, seed: int = 20260608):
        self.hasher = ZobristHasher(board_size, seed)
        self.table: Dict[Tuple[int, int], TranspositionEntry] = {}

    def make_key(self, board: Board, root_player: int) -> Tuple[int, int]:
        # root_player 会影响评估函数正负方向，因此也作为 key 的一部分。
        return self.hasher.hash_board(board), root_player

    def get(self, board: Board, root_player: int) -> Optional[TranspositionEntry]:
        return self.table.get(self.make_key(board, root_player))

    def store(self, board: Board, root_player: int, entry: TranspositionEntry) -> None:
        key = self.make_key(board, root_player)
        old = self.table.get(key)
        # 深度更大的搜索结果信息更充分；同深度时用新条目覆盖以保留最新 best_move。
        if old is None or entry.depth >= old.depth:
            self.table[key] = entry

    def __len__(self) -> int:
        return len(self.table)


# ---------- 评估函数 ----------
def evaluate_tic_tac_toe(board: Board, player: int) -> float:
    """井字棋终局评估：胜 1，负 -1，平 0。"""
    winner = board.get_winner()
    if winner == player:
        return 1.0
    if winner == 0:
        return 0.0
    if winner is not None:
        return -1.0
    return 0.0


def heuristic_tic_tac_toe(board: Board, player: int) -> float:
    """井字棋启发式评估。"""
    if board.is_game_over():
        return evaluate_tic_tac_toe(board, player)
    score = 0
    center = board.size // 2
    for r in range(board.size):
        for c in range(board.size):
            piece = int(board.board[r, c])
            if piece == player:
                score += 5 if (r, c) == (center, center) else 3 if r in (0, board.size - 1) and c in (0, board.size - 1) else 1
            elif piece != 0:
                score -= 5 if (r, c) == (center, center) else 3 if r in (0, board.size - 1) and c in (0, board.size - 1) else 1
    return float(score)


def evaluate_gomoku(board: Board, player: int) -> float:
    """
    五子棋第一版局面评估：按 5 元窗口累计分数，攻防平衡 = 己方分 - 对方分。
    该函数可供后续评估函数优化继续替换。
    """
    winner = board.get_winner()
    if winner == player:
        return 1_000_000_000.0
    if winner == 0:
        return 0.0
    if winner is not None:
        return -1_000_000_000.0

    opponent = 3 - player
    return float(_score_windows(board, player) - _score_windows(board, opponent))


def _score_windows(board: Board, player: int) -> int:
    size = board.size
    win_len = getattr(board, "win_len", 5)
    b = board.board
    score_table = {0: 0, 1: 1, 2: 20, 3: 600, 4: 4000, 5: 1_000_000}
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    score = 0
    opponent = 3 - player

    for r in range(size):
        for c in range(size):
            for dr, dc in directions:
                end_r = r + (win_len - 1) * dr
                end_c = c + (win_len - 1) * dc
                if not (0 <= end_r < size and 0 <= end_c < size):
                    continue
                pieces = [int(b[r + i * dr, c + i * dc]) for i in range(win_len)]
                if opponent in pieces:
                    continue
                count = pieces.count(player)
                if count:
                    score += score_table[count]
    return score


# ---------- 搜索走法生成与排序 ----------
def _candidate_moves(board: Board, player: int, eval_func: EvalFunc,
                     max_moves: Optional[int] = None,
                     preferred_move: Optional[Move] = None) -> List[Move]:
    """五子棋优先搜索已有棋子周围的候选点；井字棋保留全部合法走法。"""
    legal_moves = board.get_legal_moves()
    if not legal_moves:
        return []
    if board.size <= 3:
        moves = legal_moves
    else:
        occupied = np.argwhere(board.board != 0)
        if len(occupied) == 0:
            center = board.size // 2
            moves = [(center, center)] if (center, center) in legal_moves else legal_moves[:1]
        else:
            legal_set = set(legal_moves)
            near = set()
            radius = 2
            for r, c in occupied:
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = int(r) + dr, int(c) + dc
                        if (nr, nc) in legal_set:
                            near.add((nr, nc))
            moves = list(near) if near else legal_moves

        # 用一步静态评估排序：优先胜点、防守点和高分点，提高 Alpha-Beta 剪枝效率。
        scored = []
        for move in moves:
            child = board.copy()
            child.make_move(move)
            scored.append((eval_func(child, player), move))
        scored.sort(reverse=True, key=lambda item: item[0])
        moves = [move for _, move in scored]

    # 置换表曾经记录的 best_move 优先尝试，可进一步提高剪枝效率。
    if preferred_move in moves:
        moves.remove(preferred_move)  # type: ignore[arg-type]
        moves.insert(0, preferred_move)  # type: ignore[arg-type]

    if max_moves is not None and len(moves) > max_moves:
        moves = moves[:max_moves]
    return moves


# ---------- Minimax (无剪枝) ----------
def minimax(board: Board, depth: int, maximizing_player: bool, player: int, eval_func: EvalFunc,
            stats: Optional[SearchStats] = None, deadline: Optional[float] = None,
            max_moves: Optional[int] = None):
    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout
    if stats is not None:
        stats.nodes += 1

    if board.is_game_over() or depth == 0:
        return eval_func(board, player), None

    legal_moves = _candidate_moves(board, player, eval_func, max_moves=max_moves)
    if not legal_moves:
        return eval_func(board, player), None

    best_move = None
    if maximizing_player:
        max_score = -math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = minimax(new_board, depth - 1, False, player, eval_func, stats, deadline, max_moves)
            if score > max_score:
                max_score = score
                best_move = move
        return max_score, best_move

    min_score = math.inf
    for move in legal_moves:
        new_board = board.copy()
        new_board.make_move(move)
        score, _ = minimax(new_board, depth - 1, True, player, eval_func, stats, deadline, max_moves)
        if score < min_score:
            min_score = score
            best_move = move
    return min_score, best_move


# ---------- Alpha-Beta 剪枝 + 置换表 ----------
def alpha_beta(board: Board, depth: int, alpha: float, beta: float,
               maximizing_player: bool, player: int, eval_func: EvalFunc,
               stats: Optional[SearchStats] = None, deadline: Optional[float] = None,
               max_moves: Optional[int] = None,
               transposition_table: Optional[TranspositionTable] = None):
    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout
    if stats is not None:
        stats.nodes += 1

    original_alpha, original_beta = alpha, beta
    preferred_move = None

    if transposition_table is not None:
        if stats is not None:
            stats.tt_lookups += 1
        entry = transposition_table.get(board, player)
        if entry is not None:
            preferred_move = entry.best_move
            if entry.depth >= depth:
                if entry.flag == EXACT:
                    if stats is not None:
                        stats.tt_hits += 1
                    return entry.value, entry.best_move
                if entry.flag == LOWER_BOUND:
                    alpha = max(alpha, entry.value)
                elif entry.flag == UPPER_BOUND:
                    beta = min(beta, entry.value)
                if alpha >= beta:
                    if stats is not None:
                        stats.tt_hits += 1
                    return entry.value, entry.best_move

    if board.is_game_over() or depth == 0:
        value = eval_func(board, player)
        if transposition_table is not None:
            transposition_table.store(board, player, TranspositionEntry(depth, value, EXACT, None))
            if stats is not None:
                stats.tt_stores += 1
        return value, None

    legal_moves = _candidate_moves(board, player, eval_func, max_moves=max_moves, preferred_move=preferred_move)
    if not legal_moves:
        value = eval_func(board, player)
        if transposition_table is not None:
            transposition_table.store(board, player, TranspositionEntry(depth, value, EXACT, None))
            if stats is not None:
                stats.tt_stores += 1
        return value, None

    best_move = None
    if maximizing_player:
        value = -math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, False, player, eval_func,
                                  stats, deadline, max_moves, transposition_table)
            if score > value:
                value = score
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                if stats is not None:
                    stats.cutoffs += 1
                break
    else:
        value = math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, True, player, eval_func,
                                  stats, deadline, max_moves, transposition_table)
            if score < value:
                value = score
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                if stats is not None:
                    stats.cutoffs += 1
                break

    if transposition_table is not None:
        if value <= original_alpha:
            flag = UPPER_BOUND
        elif value >= original_beta:
            flag = LOWER_BOUND
        else:
            flag = EXACT
        transposition_table.store(board, player, TranspositionEntry(depth, value, flag, best_move))
        if stats is not None:
            stats.tt_stores += 1

    return value, best_move


def timed_alpha_beta(board: Board, depth: int, player: int, eval_func: EvalFunc,
                     max_moves: Optional[int] = None,
                     use_transposition_table: bool = False):
    """运行一次 Alpha-Beta，并返回 score、move、stats、置换表大小，用于实验测量。"""
    stats = SearchStats()
    tt = TranspositionTable(board.size) if use_transposition_table else None
    start = time.perf_counter()
    score, move = alpha_beta(
        board, depth, -math.inf, math.inf, True, player, eval_func,
        stats=stats, max_moves=max_moves, transposition_table=tt,
    )
    stats.elapsed = time.perf_counter() - start
    stats.completed_depth = depth
    return score, move, stats, len(tt) if tt is not None else 0


# ---------- 迭代加深 ----------
def iterative_deepening_search(board: Board, player: int, eval_func: EvalFunc,
                               time_limit: float = 2.0, max_depth: int = 10,
                               use_alpha_beta: bool = True,
                               max_moves: Optional[int] = 30,
                               use_transposition_table: bool = True):
    """
    在给定时间阈值内从深度 1 逐步加深搜索。
    超时则返回上一个完整深度的最佳走法。置换表在每一层之间复用，
    这样浅层搜索得到的 best_move 和局面估值可以加速更深层搜索。
    """
    start = time.perf_counter()
    deadline = start + time_limit
    best_move = None
    best_score = -math.inf
    aggregate = SearchStats()
    tt = TranspositionTable(board.size) if use_transposition_table and use_alpha_beta else None

    # 先给一个兜底走法，避免刚进入搜索就超时。
    fallback = _candidate_moves(board, player, eval_func, max_moves=max_moves)
    if fallback:
        best_move = fallback[0]

    for depth in range(1, max_depth + 1):
        stats = SearchStats()
        try:
            if use_alpha_beta:
                score, move = alpha_beta(board, depth, -math.inf, math.inf, True, player, eval_func,
                                         stats=stats, deadline=deadline, max_moves=max_moves,
                                         transposition_table=tt)
            else:
                score, move = minimax(board, depth, True, player, eval_func,
                                      stats=stats, deadline=deadline, max_moves=max_moves)
        except SearchTimeout:
            aggregate.timed_out = True
            break

        aggregate.nodes += stats.nodes
        aggregate.cutoffs += stats.cutoffs
        aggregate.tt_lookups += stats.tt_lookups
        aggregate.tt_hits += stats.tt_hits
        aggregate.tt_stores += stats.tt_stores
        aggregate.completed_depth = depth
        if move is not None:
            best_score, best_move = score, move
        if time.perf_counter() >= deadline:
            aggregate.timed_out = True
            break

    aggregate.elapsed = time.perf_counter() - start
    return best_score, best_move, aggregate


# ---------- 验证工具 ----------
def compare_minimax_and_alpha_beta(board: Board, depth: int, player: int, eval_func: EvalFunc):
    """验证同一局面、同一深度下，无剪枝 Minimax 与 Alpha-Beta 的评分和走法一致。"""
    mm_stats = SearchStats()
    ab_stats = SearchStats()
    mm_score, mm_move = minimax(board, depth, True, player, eval_func, stats=mm_stats)
    ab_score, ab_move = alpha_beta(board, depth, -math.inf, math.inf, True, player, eval_func, stats=ab_stats)
    return {
        "same_score": mm_score == ab_score,
        "same_move": mm_move == ab_move,
        "minimax": {"score": mm_score, "move": mm_move, "nodes": mm_stats.nodes},
        "alpha_beta": {"score": ab_score, "move": ab_move, "nodes": ab_stats.nodes, "cutoffs": ab_stats.cutoffs},
    }


def compare_transposition_table_speed(board: Board, depth: int, player: int, eval_func: EvalFunc,
                                      max_moves: Optional[int] = 16):
    """对比普通 Alpha-Beta 与集成置换表后的 Alpha-Beta，用于第三周实验记录。"""
    base_score, base_move, base_stats, _ = timed_alpha_beta(
        board, depth, player, eval_func, max_moves=max_moves, use_transposition_table=False
    )
    tt_score, tt_move, tt_stats, tt_size = timed_alpha_beta(
        board, depth, player, eval_func, max_moves=max_moves, use_transposition_table=True
    )
    speedup = base_stats.elapsed / tt_stats.elapsed if tt_stats.elapsed > 0 else math.inf
    node_reduction = 1 - (tt_stats.nodes / base_stats.nodes) if base_stats.nodes else 0.0
    return {
        "same_score": base_score == tt_score,
        "same_move": base_move == tt_move,
        "without_tt": {
            "score": base_score,
            "move": base_move,
            "nodes": base_stats.nodes,
            "cutoffs": base_stats.cutoffs,
            "elapsed": base_stats.elapsed,
        },
        "with_tt": {
            "score": tt_score,
            "move": tt_move,
            "nodes": tt_stats.nodes,
            "cutoffs": tt_stats.cutoffs,
            "elapsed": tt_stats.elapsed,
            "tt_lookups": tt_stats.tt_lookups,
            "tt_hits": tt_stats.tt_hits,
            "tt_hit_rate": tt_stats.tt_hit_rate,
            "tt_stores": tt_stats.tt_stores,
            "tt_size": tt_size,
        },
        "speedup": speedup,
        "node_reduction": node_reduction,
    }


# ---------- AI 玩家 ----------
class MinimaxPlayer(Player):
    def __init__(self, player_id: int, depth: int = 9, use_alpha_beta: bool = True,
                 eval_func: Optional[EvalFunc] = None, iterative: bool = False,
                 time_limit: float = 2.0, max_moves: Optional[int] = None,
                 use_transposition_table: bool = True):
        self.player_id = player_id
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.eval_func = eval_func if eval_func is not None else evaluate_tic_tac_toe
        self.iterative = iterative
        self.time_limit = time_limit
        self.max_moves = max_moves
        self.use_transposition_table = use_transposition_table
        self.last_stats: Optional[SearchStats] = None
        self.last_score: Optional[float] = None

    def get_move(self, board: Board):
        # 15x15 五子棋默认使用迭代加深 + Alpha-Beta + 候选走法限制。
        max_moves = self.max_moves
        if max_moves is None and board.size > 3:
            max_moves = 30

        if self.iterative:
            score, move, stats = iterative_deepening_search(
                board,
                self.player_id,
                self.eval_func,
                time_limit=self.time_limit,
                max_depth=self.depth,
                use_alpha_beta=self.use_alpha_beta,
                max_moves=max_moves,
                use_transposition_table=self.use_transposition_table,
            )
            self.last_stats = stats
            self.last_score = score
            return move

        stats = SearchStats()
        if self.use_alpha_beta:
            tt = TranspositionTable(board.size) if self.use_transposition_table else None
            start = time.perf_counter()
            score, move = alpha_beta(board, self.depth, -math.inf, math.inf, True,
                                     self.player_id, self.eval_func, stats=stats,
                                     max_moves=max_moves, transposition_table=tt)
            stats.elapsed = time.perf_counter() - start
        else:
            start = time.perf_counter()
            score, move = minimax(board, self.depth, True, self.player_id, self.eval_func,
                                  stats=stats, max_moves=max_moves)
            stats.elapsed = time.perf_counter() - start
        stats.completed_depth = self.depth
        self.last_stats = stats
        self.last_score = score
        return move
